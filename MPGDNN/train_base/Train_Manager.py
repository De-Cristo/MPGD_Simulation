import os
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.optim as optimizer

import uproot as u
import numpy as np
import awkward as ak

from lib.ReadInput import ReadTextFile

class Train_Manager:
    
    def __init__(self, input_file, output_file):
        self.batch_size = 16
        self.lr = 1e-4
        self.max_epochs = 100
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
    
    
    
