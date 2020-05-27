# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: Configurations
Author: Juanwu Lu
Facility: Tongji University
"""
from easydict import EasyDict

# Neural network configurations
nn_cfg = EasyDict()
nn_cfg.n_inputs = [3, 32, 32]
nn_cfg.n_ouputs = nn_cfg.n_inputs[1] * nn_cfg.n_inputs[2]
nn_cfg.pool_size = 2
nn_cfg.drop_prob = 0.2
nn_cfg.padding = 1

# [convolutional 1]
nn_cfg.conv1_d = 256
nn_cfg.conv1_k = 3
nn_cfg.conv1_s = 1

# [convolutional 2]
nn_cfg.conv2_d = 128
nn_cfg.conv2_k = 3
nn_cfg.conv2_s = 1

# [convolutional 3]
nn_cfg.conv3_d = 64
nn_cfg.conv3_k = 3
nn_cfg.conv3_s = 1

# [linear]
nn_cfg.conv_out = 64 * 4 * 4
nn_cfg.fc1_d = 1024
nn_cfg.fc2_d = 1024

# Training configurations
t_cfg = EasyDict()
t_cfg.n_epochs = 500000
t_cfg.batch_size = 64
t_cfg.lr = 0.00261
t_cfg.lr_owm = t_cfg.lr
t_cfg.clipgrad = None
t_cfg.eval_freq = 10000

# owm definition
t_cfg.pc1_d = nn_cfg.n_inputs[0] * 2 * 2
t_cfg.pc2_d = nn_cfg.conv1_d * 2 * 2
t_cfg.pc3_d = nn_cfg.conv2_d * 2 * 2
t_cfg.p1_d = nn_cfg.conv3_d * 2 * 2
t_cfg.p2_d = nn_cfg.fc1_d
t_cfg.p3_d = nn_cfg.fc2_d