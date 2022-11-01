import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.optim as optimizer

import uproot as u
import numpy as np
import awkward as ak

from lib.ReadInput import ReadTextFile

class Custom_Dense_Net(torch.nn.Module):
    batch_size = 100
    lr = 1e-3
    max_epochs = 100
    def __init__(self, input_file, n_input, n_output, n_neuron_hidden, n_hidden_layers):
        self.GPU = ReadTextFile(input_file)
        self.nGPU = gpu()
        self.n_input    =  n_input
        self.n_output   =  n_output
        self.n_neuron_hidden  =  n_neuron_hidden
        self.n_hidden_layers=n_hidden_layers
        
        self.input_layer = torch.nn.Linear(self.n_input, self.n_neuron_hidden)
        self.hiddenmiddle = torch.nn.Linear(self.n_neuron_hidden, self.n_neuron_hidden)
        self.predict = torch.nn.Linear(self.n_neuron_hidden, self.n_output)
        self.dropout = nn.Dropout(p=0.1)
                
    def gpu(self):
        _gpu = -99
        if self.GPU == "-1":
            os.environ['CUDA_VISIBLE_DEVICES'] = self.GPU
            _gpu = -1
            print("\033[1;32m Device:: \033[0m GPUs are disabled, will use CPUs.")
        elif self.GPU == "-99":
            os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2,3' # on PKU farm we have 4
            print("\033[1;32m Device:: \033[0m All GPUs are enabled.")
        else:
            _gpu = len(self.GPU.split(","))
            os.environ['CUDA_VISIBLE_DEVICES'] = self.GPU
            print("\033[1;32m Device:: \033[0m Enable GPU: {}.".format(self.GPU))
        return _gpu
    
    def forward(self, x):
        out = self.input_layer(x)
        out = self.dropout(out)
        out = torch.relu(out)
        for i in range(self.n_hidden_layers):
            out = self.hiddenmiddle(out)
            out = self.dropout(out)
            out = torch.relu(out) 
        out = self.predict(out) 
        return out
    
class Custom_CNN_Net(torch.nn.Module):
    def __init__(self, input_file):
        self.GPU = ReadTextFile(input_file)
        self.nGPU = gpu()
        
    def gpu(self):
        _gpu = -99
        if self.GPU == "-1":
            os.environ['CUDA_VISIBLE_DEVICES'] = self.GPU
            _gpu = -1
            print("\033[1;32m Device:: \033[0m GPUs are disabled, will use CPUs.")
        elif self.GPU == "-99":
            os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2,3' # on PKU farm we have 4
            print("\033[1;32m Device:: \033[0m All GPUs are enabled.")
        else:
            _gpu = len(self.GPU.split(","))
            os.environ['CUDA_VISIBLE_DEVICES'] = self.GPU
            print("\033[1;32m Device:: \033[0m Enable GPU: {}.".format(self.GPU))
        return _gpu
    
class Custom_LSTM_Net(torch.nn.Module):
    def __init__(self, input_file):
        self.GPU = ReadTextFile(input_file)
        self.nGPU = gpu()
        
    def gpu(self):
        _gpu = -99
        if self.GPU == "-1":
            os.environ['CUDA_VISIBLE_DEVICES'] = self.GPU
            _gpu = -1
            print("\033[1;32m Device:: \033[0m GPUs are disabled, will use CPUs.")
        elif self.GPU == "-99":
            os.environ['CUDA_VISIBLE_DEVICES'] = '0,1,2,3' # on PKU farm we have 4
            print("\033[1;32m Device:: \033[0m All GPUs are enabled.")
        else:
            _gpu = len(self.GPU.split(","))
            os.environ['CUDA_VISIBLE_DEVICES'] = self.GPU
            print("\033[1;32m Device:: \033[0m Enable GPU: {}.".format(self.GPU))
        return _gpu
    
def active_DNN(Input):
    Global = Input[0]
    
    
    
    return Output