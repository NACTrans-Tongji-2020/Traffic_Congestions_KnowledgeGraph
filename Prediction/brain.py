# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: Neural network for congestion prediction
Author: Juanwu Lu
Facility: Tongji University
"""
from __future__ import print_function
import numpy as np
import time
import torch
import torch.nn as nn

class NNet(nn.Module):
    r"""
    The main neural network structure based on CNN. 
    Input a sequence of previous observation of congestion image,
    and output a prediction of future congestion spatial distribution.
    """
    def __init__(self, config):
        super(NNet, self).__init__()
        # Static layers and activation functions
        self.maxpool = nn.MaxPool2d(config.pool_size)
        self.dropout = nn.Dropout(config.drop_prob)
        self.relu = nn.ReLU()
        self.padding = nn.ReplicationPad2d(config.padding)
        # Body
        self.c1 = nn.Conv2d(config.n_inputs[0], config.conv1_d, kernel_size=config.conv1_k, stride=config.conv1_s)
        self.c2 = nn.Conv2d(config.conv1_d, config.conv2_d, kernel_size=config.conv2_k, stride=config.conv2_s)
        self.c3 = nn.Conv2d(config.conv2_d, config.conv3_d, kernel_size=config.conv3_k, stride=config.conv3_s)
        self.f1 = nn.Linear(config.conv_out, config.fc1_d, bias=False)
        self.f2 = nn.Linear(config.fc1_d, config.fc2_d, bias=False)
        self.f3 = nn.Linear(config.fc2_d, config.n_ouputs, bias=False)
        # Global initilization
        nn.init.xavier_normal_(self.f1.weight)
        nn.init.xavier_normal_(self.f2.weight)
        nn.init.xavier_normal_(self.f3.weight)
    
    def forward(self, x):
        # Store outputs of each layer classify in accordance with layer types
        c_list, h_list = [], []
        # Gated (Add bias using padding in each layer)
        ## Cast input to float type
        x = x.float()
        ## Conv1
        x = self.padding(x)
        c_list.append(torch.mean(x, 0, True))
        conv1 = self.dropout(self.relu(self.c1(x)))
        conv1_p = self.maxpool(conv1)

        ## Conv2
        conv1_p = self.padding(conv1_p)
        c_list.append(torch.mean(conv1_p, 0, True))
        conv2 = self.dropout(self.relu(self.c2(conv1_p)))
        conv2_p = self.maxpool(conv2)

        ## Conv3
        conv2_p = self.padding(conv2_p)
        c_list.append(torch.mean(conv2_p, 0, True))
        conv3 = self.dropout(self.relu(self.c3(conv2_p)))
        conv3_p = self.maxpool(conv3)

        ## Fc1
        h = conv3_p.view(x.size(0), -1)
        h_list.append(torch.mean(h, 0, True))
        h = self.relu(self.f1(h))
        
        ## Fc2
        h_list.append(torch.mean(h, 0, True))
        h = self.relu(self.f2(h))

        ## Fc3
        h_list.append(torch.mean(h, 0, True))
        y = self.f3(h)
        return y, c_list, h_list

class Agent(object):
    r"""
    Trainer for training with statndard BP method or with orthogonal weight modification (OWM) module. 
    REFERENCE:
    Zeng, G., Chen, Y., Cui, B. et al. Continual learning of context-dependent processing in neural networks. 
    Nat Mach Intell 1, 364–372 (2019). https://doi.org/10.1038/s42256-019-0080-x
    """
    def __init__(self, model, config):
        if torch.cuda.is_available():
            # Run on GPU
            dtype = torch.cuda.FloatTensor
        else:
            dtype = torch.FloatTensor
        self.model = model
        self.n_epochs=config.n_epochs
        self.batch_size = config.batch_size
        self.lr = config.lr
        self.lr_owm = config.lr_owm
        self.clipgrad = config.clipgrad
        self.eval_freq = config.eval_freq
        # initialize optimizer
        self.loss = nn.MSELoss()
        self.optimizer = self._get_optimizer()
        # initial P-matrices for OWM with identity matrices
        with torch.no_grad():
            self.Pc1 = torch.autograd.Variable(torch.eye(config.pc1_d).type(dtype))
            self.Pc2 = torch.autograd.Variable(torch.eye(config.pc2_d).type(dtype))
            self.Pc3 = torch.autograd.Variable(torch.eye(config.pc3_d).type(dtype))
            self.P1 = torch.autograd.Variable(torch.eye(config.p1_d).type(dtype))
            self.P2 = torch.autograd.Variable(torch.eye(config.p2_d).type(dtype))
            self.P3 = torch.autograd.Variable(torch.eye(config.p3_d).type(dtype))
        
        self.test_max = 0

    def _get_optimizer(self):
        """
        Customize training optimizer with OWM.
        :Return
            optimizer (torch.optim): customized optimizer.
        """
        # Get layer params
        f1_params = list(map(id, self.model.f1.parameters()))
        f2_params = list(map(id, self.model.f2.parameters()))
        f3_params = list(map(id, self.model.f3.parameters()))
        base_params = filter(lambda p: id(p) not in f1_params + f2_params + f3_params, self.model.parameters())
        # Create customized optimizer
        optimizer = torch.optim.Adam([
            {'params': base_params},
            {'params': self.model.f1.parameters(), 'lr': self.lr_owm},
            {'params': self.model.f2.parameters(), 'lr': self.lr_owm},
            {'params': self.model.f3.parameters(), 'lr': self.lr_owm}
        ], lr=self.lr)
        return optimizer
    
    def train(self, x, y, cur_epoch=0, n_epochs=0):
        r"""
        Main training function for model.
        :params
            x (tensor): training inputs.
            y (tensor): training target.
            cur_epoch (int): current epoch number.
            n_epoch (int): total number of epochs.
        """
        self.model.train()

        # If input has batch size, generate random index list
        r_len = np.arange(x.size(0))
        np.random.shuffle(r_len)
        r_len = torch.LongTensor(r_len).cuda()
        
        # Loop batches
        for b_indx in range(0, len(r_len), self.batch_size):
            b = r_len[b_indx:min(b_indx + self.batch_size, len(r_len))]
            inputs = torch.autograd.Variable(x[b])
            target = torch.autograd.Variable(y[b])

            # Forward Propagation
            outputs, c_list, h_list = self.model.forward(inputs)
            loss = self.loss(outputs, target)

            # Backward Propagation
            self.optimizer.zero_grad()
            loss.backward()
            
            # OWM algorithm
            lambda_ = b_indx/len(r_len)/n_epochs + cur_epoch/n_epochs
            alpha_list = [1.0*1e-6**lambda_, 1.0*1e-5**lambda_, 1.0*0.01**lambda_, 1.0*0.1**lambda_]

            def weight_modification(p, x, w, alpha=1.0, cnn=True, stride=1):
                # For convolutional layers
                if cnn:
                    _,_,H,W = x.shape
                    F, _, HH, WW = w.shape
                    S = stride
                    # output shape
                    Ho = int(1 + (H-HH)/S)
                    Wo = int(1 + (W - WW)/S)
                    for i in range(Ho):
                        for j in range(Wo):
                            # flatten the high-dimensional input
                            r = x[:,:, i*S:i*S+HH, j*S:j*S+WW].contiguous().view(1, -1)
                            k = torch.mm(p, torch.t(r))
                            p.sub_(torch.mm(k, torch.t(k)) / (alpha + torch.mm(r, k)))
                    # update weight gradient with p matrix
                    w.grad.data = torch.mm(w.grad.data.view(F, -1), torch.t(p.data)).view_as(w)
                # For linear layers
                else:
                    r = x
                    k = torch.mm(p, torch.t(r))
                    p.sub_(torch.mm(k, torch.t(k)) / (alpha + torch.mm(r, k)))
                    w.grad.data =  torch.mm(w.grad.data, torch.t(p.data))
            
            # Compensate embedding gradients
            for n, w in self.model.named_parameters():
                # modify weight in each layer
                if n=='c1.weight':
                    weight_modification(self.Pc1, c_list[0], w, alpha=alpha_list[0], stride=1)
                if n=='c2.weight':
                    weight_modification(self.Pc2, c_list[1], w, alpha=alpha_list[0], stride=1)
                if n=='c3.weight':
                    weight_modification(self.Pc3, c_list[2], w, alpha=alpha_list[0], stride=1)
                if n=='f1.weight':
                    weight_modification(self.P1, h_list[0], w, alpha=alpha_list[1], cnn=False)
                if n=='f2.weight':
                    weight_modification(self.P2, h_list[1], w, alpha=alpha_list[2], cnn=False)
                if n=='f3.weight':
                    weight_modification(self.P3, h_list[2], w, alpha=alpha_list[3], cnn=False)
            
            # Step weight gradients
            if self.clipgrad:
                torch.nn.utils.clip_grad_norm(self.model.parameters, self.clipgrad)
            self.optimizer.step()
        return

    def eval(self,x, y):
        r"""
        Main evaluation function.
        :params
            x (tensor): input dataset.
            y (tensor): target dataset.
        :return
            mean loss and mean accuracy
        """
        total_loss, total_acc, total_num = 0., 0., 0.
        self.model.eval()
        # Similarly retrieve batch size from input
        r = np.arange(x.size(0))
        r = torch.LongTensor(r).cuda()
        # Loop batches
        for i in range(0, len(r), self.batch_size):
            b = r[i:min(i+self.batch_size, len(r))]
            with torch.no_grad():
                inputs = torch.autograd.Variable(x[b])
                target = torch.autograd.Variable(y[b])
            
            # Forward propagation
            output, _, _ = self.model.forward(inputs)
            loss = self.loss(output, target)
            acc = torch.abs(output - target) / target

            # Observe and log
            total_loss += loss.data.cpu().numpy().item()*len(b)
            total_acc += acc.sum().data.cpu().numpy().item()
            total_num += len(b)
        return total_loss/total_num, total_acc/total_num
    
    def run(self, xtrain, ytrain, xeval, yeval, writer=None):
        r"""
        Main function of the training agent.
        :params
            xtrain (tensor): training datasets.
            ytrain (tensor): training targets.
            xeval (tensor): evaluation datasets.
            yeval (tensor): evaluation targets.
            writer (SummaryWriter): for retrieve and log scalars.
        """
        best_loss, best_acc = np.inf, 0.
        # loop epchos and train
        for e in range(self.n_epochs):
            # Train
            self.train(xtrain, ytrain, cur_epoch=e, n_epochs=self.n_epochs)
            loss_t, acc_t = self.eval(xtrain, ytrain)
            print('# | Epoch {:d}/{:d} | Train: loss={:3f}, acc={:2.2f}%'.format(
                            e+1, self.n_epochs, loss_t, 100*acc_t))
            # Evaluation
            loss_e, acc_e = self.eval(xeval, yeval)
            print('# | Evaluation | loss={:3f}, acc={:2.2f}%\n'.format(loss_e, 100*acc_e), end='')
            if writer:
                writer.add_scalar("Train/loss", loss_t, e)
                writer.add_scalar("Train/accuracy", 100*acc_t, e)
                writer.add_scalar("Eval/loss",loss_e, e)
                writer.add_scalar("Eval/accuracy", 100*acc_e, e)
            if e % self.eval_freq == 0:
                torch.save({'epoch': e+1, 'state_dict':self.model.state_dict()}, './model/{:s}-{:d}.pth'.format(time.time(), e+1))
#        except Exception as e:
#            print(e)
            return
