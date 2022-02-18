#export GARFIELD_HOME=/afs/cern.ch/user/l/lichengz/public/Garfield++
#export HEED_DATABASE=$GARFIELDPP_HOME/Heed/heed++/database

# source /cvmfs/sft.cern.ch/lcg/releases/LCG_96/CMake/3.14.3/x86_64-slc6-gcc8-opt/CMake-env.sh
# source /cvmfs/sft.cern.ch/lcg/releases/LCG_96/ROOT/6.18.00/x86_64-slc6-gcc8-opt/ROOT-env.sh
# source /cvmfs/sft.cern.ch/lcg/releases/LCG_96/Garfield++/759b148a/x86_64-slc6-gcc8-opt/Garfield++-env.sh

source /cvmfs/sft.cern.ch/lcg/views/LCG_98python3/x86_64-centos7-clang10-opt/setup.sh
export HEED_DATABASE=$GARFIELD_HOME/Heed/heed++/database
alias garfcmake="cmake -DCMAKE_PREFIX_PATH=$GARFIELD_HOME"
