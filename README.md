# MPGD_Simulation
MPGD Simulation codes

## Introduction
This is a repo for MPGD simulation relevant studies.

### Environment
```shell
source setup-garf-pku.sh # on PKU farm
source setup-garf-lxplus.sh # on LXPLUS clusters
```
**note**: you can use the garfield compiled by Licheng, or you can compile for yourself according to the official [recommending](https://garfieldpp.web.cern.ch/garfieldpp/).

<!-- TOC -->

- [ANSYS](#ansys)
- [PyfieldTools](#pyfieldtools)
- [Simulation](#simulation)
- [Analysis](#analysis)
- [NN implementation](#nn-iplementation)

<!-- /TOC -->

### ANSYS
**note**: People can always use ANSYS of any version to do anything via their PC.
    **ANSYS APDL on LXPLUS**
    Last updated on 13 Oct 2022.
    **Login and Set Enviroment**
    After got accounts and certifications on LXPLUS servers.You can use computer cluster for simulation works.
    For more details about **account** and **certifications** can be found at [CERN](https://account.cern.ch/account/).
    Also, you need prepare **account** and **basic skills** about [HTCondor](https://batchdocs.web.cern.ch/index.html) and [EOS](https://cern.service-now.com/service-portal%3Fid=kb_article&n=KB0001998).
    * * *
    You can Login LXPLUS via `ssh -Y` for GUI. For example,
    ```shell
    ssh -Y loginNAME@lxplus.cern.ch
    ```
    * * *
    After login, some enviroment setting is aquired.
    **Login to LXPLUS**
    Login to `lxplus` using your NICE account.
    Run `kinit username` to get a kerberos token for your NICE credentials (Note that kerberos tokens expire after 24h, so re-run this command if needed)
    * * * 
    **Launch a real simulation**
    **Prepare your Ansys Classic script**
    Create a script called, for instance, `my_script.sh` with the following content(which is modified based on [KB](https://cern.service-now.com/service-portal?id=kb_article&n=KB0006082)) and more details at [twiki](https://twiki.cern.ch/twiki/bin/view/CAE/AnsysService):

### PyfieldTools

### Simulation

### Analysis

### NN implementation
