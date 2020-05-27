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
import cifar as dataloader
import datetime, time
import numpy as np
import torch
from tensorboardX import SummaryWriter

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int, default=int(time.time()), help='(Seed for randomization, default=%(default)d)')
parser.add_argument('--experiment', default='cifar-10', type=str, required=False, help='(Experiment dataset, default=%(default)s')
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
data, taskcla, inputsize = dataloader.get(seed=args.seed)
print('# Input size: ', inputsize, '\n# Task info: ', taskcla)

# Initialization
print('# Initializing...')
net = brain.NNet(nn_cfg).to(device)
agent = brain.Agent(net, t_cfg)
print('-'*100)

# Run tasks
acc, loss = np.zeros((len(taskcla), len(taskcla)), dtype=np.float32), np.zeros((len(taskcla), len(taskcla)), dtype=np.float32)
for t, ncla in taskcla:
    print('# Task {:2d} ({:s})'.format(t+1, data[t]['name']))
    xtrain = data[t]['train']['x'].cuda()
    ytrain = data[t]['train']['y'].cuda()
    xeval = data[t]['test']['x'].cuda()
    yeval = data[t]['test']['y'].cuda()
    # Loop training
    agent.run(t, xtrain, ytrain, xeval, yeval, writer=writer)
    # Test
    for u in range(t+1):
        xtest = data[u]['test']['x'].cuda()
        ytest = data[u]['test']['y'].cuda()
        loss_t, acc_t = agent.eval(xtest, ytest)
        print('# | Test on task {:2d}-{:15s} | loss = {:3f}, acc={:2.2f}%'.format(u, data[u]['name'], loss_t, 100*acc_t))
        acc[t, u] = acc_t
        loss[t, u] = loss_t
        writer.add_scalar("Test/loss", loss_t, u)
        writer.add_scalar("Test/accuracy", acc_t, u)