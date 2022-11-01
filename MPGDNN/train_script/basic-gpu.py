import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from math import ceil
import torch
import torch.nn as nn

import argparse
import uproot as u
import awkward as ak

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--inFile", dest='infile', default='../../Simulation/test_xray_2nd.root', type=str, help="input root file (default=../../Simulation/test_xray_2nd.root)")
args = parser.parse_args()

#dataset
process_tree = u.open(args.infile)["full_simulation_tree"]
train_base = process_tree.arrays(["PrimaryElectron_number","PrimaryElectron_zposition", "FinalElectron_number"], library="pd")

x_train = train_base.iloc[0:10000, 0:1001]
y_train = train_base.iloc[0:10000, 1001:1002]

# print(x_train)
# print(y_train)
# exit(0)

# from sklearn.preprocessing import MinMaxScaler
 
# Mscalerx = MinMaxScaler(feature_range=[0,1])
# Mscalery = MinMaxScaler(feature_range=[0,1])

# X_train = Mscalerx.fit_transform(x_train)
# Y_train = Mscalery.fit_transform(y_train)

from sklearn.preprocessing import StandardScaler
 
Sscalerx = StandardScaler()
# Sscalery = StandardScaler()

X_train = Sscalerx.fit_transform(x_train)
# Y_train = Sscalery.fit_transform(y_train)
Y_train = y_train.to_numpy()
# print(X_train)
# print(Y_train)
# exit(0)
# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# dtype = torch.FloatTensor

X_train = torch.tensor(X_train, dtype=torch.float32)
Y_train = torch.tensor(Y_train, dtype=torch.float32)
torch_dataset = torch.utils.data.TensorDataset(X_train, Y_train)  # 组成torch专门的数据库
batch_size = 100
trainval_ratio = 0.8
test_ratio = 0.2
train_ratio = 0.8
val_ratio = 0.2


torch.manual_seed(seed=2021)
train_validaion, test = torch.utils.data.random_split(
    torch_dataset,
    lengths=[int(trainval_ratio * torch_dataset.__len__()), ceil(test_ratio * torch_dataset.__len__())],
)

train, validation = torch.utils.data.random_split(
    train_validaion, 
    lengths=[int(train_ratio * train_validaion.__len__()), ceil(val_ratio * train_validaion.__len__())],
)
 
train_data = torch.utils.data.DataLoader(train,
                                         batch_size=batch_size,
                                         shuffle=True)

import torch.optim as optim
 
feature_number = 1001
out_prediction = 1
learning_rate = 0.01
epochs = 20
 
class Net(torch.nn.Module):
    def __init__(self, n_feature, n_output, n_neuron1, n_neuron2,n_layer):
        self.n_feature=n_feature
        self.n_output=n_output
        self.n_neuron1=n_neuron1
        self.n_neuron2=n_neuron2
        self.n_layer=n_layer
        super(Net, self).__init__()
        self.input_layer = torch.nn.Linear(self.n_feature, self.n_neuron1)
        self.hidden1 = torch.nn.Linear(self.n_neuron1, self.n_neuron2)  
        self.hidden2 = torch.nn.Linear(self.n_neuron2, self.n_neuron2)
        self.predict = torch.nn.Linear(self.n_neuron2, self.n_output)
 
    def forward(self, x):
        out = self.input_layer(x)
        out = torch.relu(out)
        out = self.hidden1(out)
        out = torch.relu(out)
        for i in range(self.n_layer):
            out = self.hidden2(out)
            out = torch.relu(out) 
        out = self.predict(
            out
        ) 
        return out
    
net = Net(n_feature=feature_number,
                      n_output=out_prediction,
                      n_layer=1,
                      n_neuron1=256,
                      n_neuron2=256)
# net.to(device)
optimizer = optim.Adam(net.parameters(), learning_rate)
criteon = torch.nn.MSELoss()

train_loss=[]
validation_loss=[]
for epoch in range(epochs):  # 整个数据集迭代次数
    net.train()
    for batch_idx, (data, target) in enumerate(train_data):
        logits = net.forward(data)  # 前向计算结果（预测结果）
        loss = criteon(logits, target)  # 计算损失
        train_losses=loss.detach().numpy()
        optimizer.zero_grad()  # 梯度清零
        loss.backward()  # 后向传递过程
        optimizer.step()  # 优化权重与偏差矩阵
    train_loss.append(train_losses) # 记录历史测试误差(每代)
 
    logit = []  # 这个是验证集，可以根据验证集的结果进行调参，这里根据验证集的结果选取最优的神经网络层数与神经元数目
    target = []
    net.eval()
    for data, targets in validation:  # 输出验证集的平均误差
        logits = net.forward(data).detach().numpy()
        targets=targets.detach().numpy()
        target.append(targets[0])
        logit.append(logits[0])
    average_loss= criteon(torch.tensor(logit),torch.tensor(target)).detach().numpy()  # 计算损失
    validation_loss.append(average_loss) # 记录历史验证误差（每代）
    print('\nTrain Epoch {0}: for the Average loss of VAL'.format(str(epoch)))
    
plt.figure()
plt.plot([x+1 for x in range(epochs)], validation_loss, color='black', linestyle='-',label='validation loss')
plt.plot([x+1 for x in range(epochs)], train_loss, color='red', linestyle='-',label='train loss')
plt.xlabel('epoches')
plt.ylabel('loss')
plt.legend()
plt.title('judge overfitting')
plt.show()
plt.savefig('loss.png')

prediction = []
test_x = []
test_y = []
net.eval()
for test_xs, test_ys in test:
#     print(test_xs)
    predictions = net(test_xs)
    predictions=predictions.detach().numpy()
    prediction.append(predictions[0])
    test_ys.detach().numpy()
    test_y.append(test_ys[0])
# prediction = Sscalery.inverse_transform(np.array(prediction).reshape(-1, 1))  # 将数据恢复至归一化之前
# test_y = Sscalery.inverse_transform(np.array(test_y).reshape(-1, 1))
# test_x = scalerx.inverse_transform(np.array(test_x).reshape(-1, 1))
# 均方误差计算
test_loss = criteon(torch.tensor(prediction ,dtype=torch.float32), torch.tensor(test_y, dtype=torch.float32))
print('测试集均方误差：',test_loss.detach().numpy())

# print(test_y)
# print(test_x)

# 可视化
# plt.figure()
# plt.scatter(test_x, test_y, color='yellow',s=1.)
# plt.scatter(test_x, prediction, color='red',s=1.)
# # plt.plot([-5, 200], [-5, 200], color='black', linestyle='-')
# plt.xlim([-5, 30])
# plt.ylim([-5, 200])
# # plt.xlabel('true')
# # plt.ylabel('prediction')
# # plt.title('true vs prection')
# plt.show()
# plt.savefig('test.png')

# 可视化
plt.figure()
plt.scatter(test_y, prediction, color='red',s=1.)
plt.plot([-5, 200], [-5, 200], color='black', linestyle='-')
plt.xlim([-5, 200])
plt.ylim([-5, 200])
plt.xlabel('true')
plt.ylabel('prediction')
plt.title('true vs prection')
plt.show()
plt.savefig('test.png')
