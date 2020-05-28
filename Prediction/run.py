# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: Task runner
Author: Juanwu Lu
Facility: Tongji University
"""
import argparse, sys
import brain
from cfg import nn_cfg, t_cfg
import preprocessing as dataloader
import datetime, time
import numpy as np
import torch
from tensorboardX import SummaryWriter

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int, default=int(time.time()), help='(Seed for randomization, default=%(default)d)')
parser.add_argument('--device', default='gpu', type=str, required=False, help='(If use gpu, default=%(default)s')
parser.add_argument('--owm', default=True, type=bool, required=False, help='(If use OWM, default=%(default)s)')
args = parser.parse_args()

# Settings
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2' # ignore warnings
if torch.cuda.is_available() and getattr(args, 'device')=='gpu':
    device = torch.device("cuda")
    os.environ["CUDA_VISIBLE_DEVICES"] = '0' # use gpu 0
    torch.backends.cudnn.benchmark = True
else:
    device = torch.device("cpu")
writer = SummaryWriter() # Logger

# Head
print('-'*100)
print("# Traffic congestion spatial feature prediction\n")
print("# Author: Juanwu Lu\n")
print("# All rights reserved")
print("# 2020 College of Transportation Engineering at Tongji University")
print('-'*100)
print('# Arguments = ')
for arg in vars(args):
    print('\t',  arg, ':', getattr(args, arg))
print('-'*100)
print('#', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'device:', device)

# Randomize
np.random.seed(args.seed)
torch.manual_seed(args.seed)
if torch.cuda.is_available():
    torch.cuda.manual_seed(args.seed)
else:
    print('# CUDA unavailable.')
    sys.exit(0)

# Load data
print('# Loading data...')
data, inputsize = dataloader.get()
print('# Input type: NCHW', '\n# Input size: ', inputsize)

# Initialization
print('# Initializing...')
net = brain.NNet(nn_cfg).to(device)
agent = brain.Agent(net, t_cfg)
print('-'*100)

# Run tasks
print('# Training...')
xtrain = data['train']['x'].cuda()
ytrain = data['train']['y'].cuda()
xeval = data['test']['x'].cuda()
yeval = data['test']['y'].cuda()
# Loop training
agent.run(xtrain, ytrain, xeval, yeval, writer=writer)
print('-'*100)
# Test
print('# Testing...')
xtest = data['test']['x'].cuda()
ytest = data['test']['y'].cuda()
loss_t, acc_t = agent.eval(xtest, ytest)
print('# | Bechmark | loss = {:3f}, acc={:2.2f}%'.format(loss_t, 100*acc_t))
#writer.add_scalar("Test/loss", loss_t, u)
#writer.add_scalar("Test/accuracy", acc_t, u)