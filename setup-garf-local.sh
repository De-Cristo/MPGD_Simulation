export GARFIELD_HOME=/home/pku/zhanglic/public/Garfield++
export HEED_DATABASE=$GARFIELD_HOME/Heed/heed++/database

source /cvmfs/sft.cern.ch/lcg/releases/LCG_96/CMake/3.14.3/x86_64-slc6-gcc8-opt/CMake-env.sh
source /cvmfs/sft.cern.ch/lcg/releases/LCG_96/ROOT/6.18.00/x86_64-slc6-gcc8-opt/ROOT-env.sh

alias garfcmake="cmake -DCMAKE_PREFIX_PATH=$GARFIELD_HOME"
