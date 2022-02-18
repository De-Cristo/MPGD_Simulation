#ifndef Full_SIM_h_
#define Full_SIM_h_

#include <iostream>
#include <string>
#include <cstring>
#include <fstream>
#include <sstream>
#include <cmath>
#include <unistd.h>
// std cpp class.
#include <TApplication.h>
#include <TH1F.h>
#include <TFile.h>
#include <TTree.h>
#include <TNtuple.h>
#include <TRandom3.h>
// ROOT class.
#include "Garfield/ComponentAnsys123.hh"
#include "Garfield/ViewField.hh"
#include "Garfield/TrackHeed.hh"
#include "Garfield/MediumMagboltz.hh"
#include "Garfield/Sensor.hh"
#include "Garfield/AvalancheMicroscopic.hh"
#include "Garfield/AvalancheMC.hh"
#include "Garfield/Random.hh"
#include "Garfield/ViewDrift.hh"
#include "Garfield/DriftLineRKF.hh"
#include "Garfield/ComponentAnalyticField.hh"
// Garfield++ class

// class Full_SIM {
// public :
//     Full_SIM();
//     virtual ~Full_SIM();
    
//     void Simulation();
    
//     int a;
//     TFile * full_sim_result;
// };
TFile * full_sim_result = new TFile("full_sim_result.root","RECREATE");
TTree * simu_tree = new TTree("tree","tree");
// TNtuple * ntuple = new TNtuple("ntuple","demo","a:i");

#endif