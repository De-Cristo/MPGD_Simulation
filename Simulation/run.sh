#!/bin/bash

# for i in {1..100}
# do
#     # echo $i
#     nohup python Simulation.py -c Full_SIM_config.txt -n xray_$i -e 1000 >>out_xray_$i.log 2>& 1 &
#     sleep 1m
# done

for i in {1..50}
do
    echo "uploading job $i of 50"
    nohup python Simulation.py -c Full_SIM_config.txt -n 150GeVMuon_v3_nodelta_$i -e 100 >>150GeVMuon_v3_nodelta_$i.log 2>& 1 &
    sleep 20s
done
