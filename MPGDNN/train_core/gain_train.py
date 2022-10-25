import pandas as pd
import matplotlib.pyplot as plt
from train.Train_Manager import Train_Manager

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--configFile",  dest="config",   default='../cfgs/gain_train.txt',  type=str,  help="configuration file (default = ../cfgs/gain_train.txt)" )
parser.add_argument("-n", "--outFileName", dest="name",     default='xray',  type=str,  help="The name of the output root file (default = xray)" )
args = parser.parse_args()

def main():
    
    TM = Train_Manager(args.config,args.name)
    
    TM.max_epochs = 200
    
    print(TM.batch_size)
    print(TM.max_epochs)
    return 0

if __name__ == '__main__':
    main()
    