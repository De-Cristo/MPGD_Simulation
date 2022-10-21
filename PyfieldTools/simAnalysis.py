from util import *

from multiprocessing import Pool

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inFile", dest='infile', default='../Simulation/xray.root', type=str, help="input root file (default=../Simulation/xray.root)")
parser.add_argument("-o", "--outDir", dest='outdir', default='./plots/', type=str, help="direction that output figure stored in")
parser.add_argument("-m", "--MultiThreads", dest='mt', default=1, type=int, help="The number of threads that been used")
args = parser.parse_args()

inFile = args.infile
ourDir = args.outdir
MT     = args.mt
os.system('mkdir -p {}'.format(ourDir))

process_tree = u.open(inFile)["full_simulation_tree"]

label_sel = 0
# label_sel = reduce(np.logical_or, [process_tree1[k].array() == 1 for k in label_n_masks[Label1]])

arg_list = []

information_list = all_information

twoD = False
for _var in information_list:
    if label_sel != 0:
        arguement = [ak.flatten(process_tree[_var].array()[label_sel], axis=None), _var, ourDir, twoD]
    else:
        arguement = [ak.flatten(process_tree[_var].array(), axis=None), _var, ourDir, twoD]
    arg_list.append(arguement)
    
with Pool(MT) as p:
    p.map(plot_manager, arg_list)
    
arg_list = []
twoD = True
for _plot_name in twod_list:
    if label_sel != 0:
        arguement = [ak.flatten(process_tree[twod_plots[_plot_name][0]].array()[label_sel], axis=None), _plot_name, ourDir, twoD, ak.flatten(process_tree[twod_plots[_plot_name][1]].array()[label_sel], axis=None),_plot_name]
    else:
        arguement = [ak.flatten(process_tree[twod_plots[_plot_name][0]].array(), axis=None), _plot_name, ourDir, twoD, ak.flatten(process_tree[twod_plots[_plot_name][1]].array(), axis=None),_plot_name]
    arg_list.append(arguement)

with Pool(MT) as p:
    p.map(plot_manager, arg_list)
