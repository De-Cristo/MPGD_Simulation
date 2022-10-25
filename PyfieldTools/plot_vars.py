import numpy as np

global_information =   ['Events', 
                        'ionization',
                       ]

incident_information =   ['Incident_xposition',
                          'Incident_yposition',
                          'Incident_zposition',
                          'Incident_energy',
                          'Incident_time',
                         ]

ionization_information = ['PrimaryElectron_number',
                          'PrimaryCluster_number',
                          'PrimaryElectron_xposition',
                          'PrimaryElectron_yposition',
                          'PrimaryElectron_zposition',
                          'PrimaryElectron_energy',
                          'PrimaryElectron_time',
                          'PrimaryElectron_number_inDrift',
                          'PrimaryElectron_number_inDrift_aval',
                          'PrimaryElectron_number_NotinDrift_aval',
                         ]

final_information = ['FinalElectron_number',
                     'Effective_Gain',
                    ]

all_information = global_information+incident_information+ionization_information+final_information

twod_list = ['primary_electron_xz',
             'primary_electron_yz',
            ]

twod_plots = {
    'primary_electron_xz': ['PrimaryElectron_xposition','PrimaryElectron_zposition', -0.05, 0.05, -0.1, 0.1],
    'primary_electron_yz': ['PrimaryElectron_yposition','PrimaryElectron_zposition', -0.5, 0.5, -0.1, 0.1]
}

plot_configs = {
    'Events'                       : {"bins": np.linspace(0, 100000, 2)    , "log": False ,                      },
    'ionization'                   : {"bins": np.linspace(0, 2, 3)         , "log": True  ,                      },
    'Incident_xposition'           : {"bins": np.linspace(-0.50, 0.50, 50) , "log": False ,                      },
    'Incident_yposition'           : {"bins": np.linspace(-0.50, 0.50, 50) , "log": False ,                      },
    'Incident_zposition'           : {"bins": np.linspace(-0.10, 0.10, 50) , "log": False ,                      },
    'Incident_energy'              : {"bins": np.linspace(0., 4e6, 100)    , "log": False ,                      },
    'Incident_time'                : {"bins": np.linspace(-0.50, 0.50, 50) , "log": False ,                      },
    'PrimaryElectron_number'       : {"bins": np.linspace(0, 200, 50)      , "log": False ,                      },
    'PrimaryCluster_number'        : {"bins": np.linspace(0, 20, 20)       , "log": False ,                      },
    'PrimaryElectron_energy'       : {"bins": np.linspace(0, 590, 50)      , "log": False ,    "underflow": -999.},
    'PrimaryElectron_time'         : {"bins": np.linspace(0, 0.05, 50)     , "log": False ,    "underflow": -999.},
    'PrimaryElectron_xposition'    : {"bins": np.linspace(-0.05, 0.05, 50) , "log": False ,    "underflow": -999.},
    'PrimaryElectron_yposition'    : {"bins": np.linspace(-0.05, 0.05, 50) , "log": False ,    "underflow": -999.},
    'PrimaryElectron_zposition'    : {"bins": np.linspace(-0.10, 0.10, 50) , "log": False ,    "underflow": -999.},
    'PrimaryElectron_number_inDrift':{"bins": np.linspace(0, 200, 50)      , "log": False ,       "underflow": 0.},
    'PrimaryElectron_number_inDrift_aval':{"bins": np.linspace(0, 200, 50)      , "log": False ,  "underflow": 0.},
    'PrimaryElectron_number_NotinDrift_aval':{"bins": np.linspace(0, 200, 50)   , "log": False ,  "underflow": 0.},
    'FinalElectron_number'         : {"bins": np.linspace(0, 1000, 50)     , "log": False ,       "underflow": 0.},
    'Effective_Gain'               : {"bins": np.linspace(0, 20, 50)       , "log": False ,    "underflow": -999.},
}



label_n_masks = {
    'ionized' : ['ionization'],
}