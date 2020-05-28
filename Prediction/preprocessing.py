# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: training data generator
Author: Juanwu Lu
Facility: Tongji University
"""
import math
import numpy as np
import os
import pandas as pd
import pickle
import torch
from torch.utils.data import Dataset, DataLoader 
from torchvision import transforms


class FCDBH(Dataset):
    """`FCDBH`_ Dataset.

    :params:
        root (string): Root directory of dataset where directory
            ``cifar-10-batches-py`` exists or will be saved to if download is set to True.
        train (bool, optional): If True, creates dataset from training set, otherwise
            creates from test set.
        transform (callable, optional): A function/transform that takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        download (bool, optional): If true, downloads the dataset from the internet and
            puts it in root directory. If dataset is already downloaded, it is not
            downloaded again.

    """
    def __init__(self, root, train=True, transform=None, target_transform=None):
        super(FCDBH, self).__init__()
        base_folder = 'fcd-bh'
        filename = "fcd-bh.rar"
        train_list = [
            ['data_batch_1', ''],
            ['data_batch_2', ''],
            ['data_batch_3', ''],
            ['data_batch_4', '']
        ]
        test_list = [
            ['test_batch', '']
        ]
        self.train = train  # training set or test set
        if self.train:
            downloaded_list = train_list
        else:
            downloaded_list = test_list
        self.transform =  transform
        self.target_transform = target_transform
        self.data = []
        self.targets = []
        # now load the picked numpy arrays
        for file_name, checksum in downloaded_list:
            file_path = os.path.join(root, base_folder, file_name)
            with open(file_path, 'rb') as f:
                entry = pickle.load(f, encoding='latin1')
                self.data.append(entry['data'])
                if 'targets' in entry:
                    self.targets.extend(entry['targets'])
                else:
                    self.targets.extend(entry['fine_targets'])
        self.data = np.vstack(self.data).reshape(-1, 4, 32, 32)
        self.data = self.data.transpose((0, 2, 3, 1))  # convert to HWC

    def __getitem__(self, index):
        """
        :params
            index (int): Index

        :returns
            tuple: (image, target) where target is index of the target class.
        """
        img, target = self.data[index], self.targets[index]

        # Preprocess data
        # Flatten the target matrix to fit network ouputs
        target = target.flatten()

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target


    def __len__(self):
        return len(self.data)

def generator(data_list):
    r"""
    Generate training datasets with pickle module.
    :params
        data_list (list): list of data path
    """
    # Define boundaries
    lon_step = (114.1 - 113.9) / 32
    lat_step = (22.58 - 22.55) / 32
    for pth in data_list:
        data = pd.read_csv(pth)
        
        # Divide and generate batches by date
        img = []

        # Load data
        for timestmp in np.sort(data.SliceStamp.unique()):
            try:
                # 建立时间片采样矩阵
                tmp = data[data.SliceStamp == timestmp]
                matrix = np.zeros([32,32])
                cnt = np.zeros([32,32])
                for indx in range(len(tmp)):
                    # 读取记录数据
                    lon = tmp.CoreLongit.values[indx]
                    lat = tmp.CoreLatitu.values[indx]
                    lev = tmp.Level.values[indx]

                    # 计算栅格位置
                    col = math.floor((lon-np.min(data.CoreLongit.values)) / lon_step)
                    row = math.floor((lat-np.min(data.CoreLatitu.values)) / lat_step)
                    matrix[row][col] += lev
                    cnt[row][col] += 1
                matrix = np.divide(matrix, cnt, np.zeros_like(matrix), where=cnt!=0)
                img.append(matrix)
            except Exception as e:
                print(timestmp, e)
            
        # Seperate data inputs and targets
        x, y = [], []
        for i in range(len(img)-5):
            mts = img[i : i+5]
            x.append(mts[:4])
            y.append(mts[-1])
        
        # Save batch data
        batch = {}
        batch['data'] = x
        batch['targets'] = y
        batch['batch_name'] = pth
        with open(pth[:-4], 'wb') as f:
            pickle.dump(batch, f)
        
        return

def get(root='./data/'):
    size = [4, 32, 32]
    # Normalization
    mean = [2.5] * 4
    std = [2.5] * 4
    # FCDBH
    if not os.path.isdir(os.path.join(root, 'fcd-bh')):
        print("# Data missing. Please check local files.")
        return 
    if not os.path.isdir(os.path.join(root, 'binary-fcd')):
        data={}
        os.makedirs(os.path.join(root, 'binary-fcd'))
        # Load data
        dat = {}
        dat['train'] = FCDBH(root, train=True, transform=transforms.Compose([transforms.ToTensor(),transforms.Normalize(mean,std)]))
        dat['test'] = FCDBH(root, train=False, transform=transforms.Compose([transforms.ToTensor(),transforms.Normalize(mean,std)]))
        for s in ['train', 'test']:
            shuffle = True if s == 'train' else False
            loader = DataLoader(dat[s], batch_size=1, shuffle=shuffle)
            data[s] = {'x':[], 'y':[]}
            for img, label in loader:
                target = label.numpy()[0]
                data[s]['x'].append(img)
                data[s]['y'].append(torch.Tensor(target))
        # "Unify" and save
        for s in ['train', 'test']:
            data[s]['x'] = torch.stack(data[s]['x']).view(-1, size[0], size[1], size[2])
            data[s]['y'] = torch.stack(data[s]['y']).view(-1, size[1] * size[2])
            torch.save(data[s]['x'],
                    os.path.join(os.path.expanduser(os.path.join(root, 'binary-fcd')), 'data' + s + 'x.bin'))
            torch.save(data[s]['y'],
                    os.path.join(os.path.expanduser(os.path.join(root, 'binary-fcd')), 'data' + s + 'y.bin'))
    
    else:
        data = dict.fromkeys(['train', 'test'])
        # Load binary files for training
        for s in ['train', 'test']:
            data[s] = {'x':[], 'y':[]}
            data[s]['x'] = torch.load(os.path.join(os.path.expanduser(os.path.join(root, 'binary-fcd')),'data' + s +'x.bin'))
            data[s]['y'] = torch.load(os.path.join(os.path.expanduser(os.path.join(root, 'binary-fcd')),'data' + s +'y.bin'))
    
    return data, size
