//########################################################################################
// This project is based on Garfield++(CERN) & ROOT(CERN).                               #
// This certain code is to simulate Fe55 X-Ray test.                                     #
// First contributed by PKU-CMS GEM group 2020-9-18 Licheng ZHANG & Aera JUNG & Yue WANG #
// Author: contact L.C.ZHANG (licheng.zhang@cern.ch)                                     #
//########################################################################################

#include "Full_SIM.hh"

using namespace Garfield;
using namespace ROOT;

//#########################################################################################################
//Set the signal transfer function. (Please change the T.F. accordingly.)
//#########################################################################################################
double transfer(double t)
{
    const double tau = 100.;
    return pow((t / tau),3)* exp(-3 * t / tau);
}

//##########################################################################
// Main Function.
//##########################################################################
int main(int argc, char *argv[])
{
//     TFile * full_sim_result = new TFile("full_sim_result.root","RECREATE");
//     TTree * simu_tree = new TTree("tree","tree");
//     simu_tree->Write();
    Float_t a;
    simu_tree->Branch("a",&a,"a/F");
    for (Int_t i=0; i<100; i++){
        a = i*2;
        simu_tree->Fill();
    }
    simu_tree->Write();
    full_sim_result->Close();
    
    return 1;
}
// The end;

// TFile * full_sim_result = new TFile::TFile("full_sim_result.root","RECREATE");
// full_sim_result->Close();