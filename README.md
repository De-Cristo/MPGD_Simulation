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
**note**: People can always use ANSYS of any version to do anything via their PC.<br />
**ANSYS APDL on LXPLUS**<br />
Last updated on 13 Oct 2022.<br />
**Login and Set Enviroment**<br />
After got accounts and certifications on LXPLUS servers.You can use computer cluster for simulation works.<br />
For more details about **account** and **certifications** can be found at [CERN](https://account.cern.ch/account/).<br />
Also, you need prepare **account** and **basic skills** about [HTCondor](https://batchdocs.web.cern.ch/index.html) and [EOS](https://cern.service-now.com/service-portal%3Fid=kb_article&n=KB0001998).<br />
***
You can Login LXPLUS via `ssh -Y` for GUI. For example,<br />
```shell
ssh -Y loginNAME@lxplus.cern.ch
```
***
After login, some enviroment setting is aquired.<br />
**Login to LXPLUS**<br />
Login to `lxplus` using your NICE account.<br />
Run `kinit username` to get a kerberos token for your NICE credentials (Note that kerberos tokens expire after 24h, so re-run this command if needed)<br />
***
**Launch a real simulation**<br />
**Prepare your Ansys Classic script**<br />
Create a script called, for instance, `my_script.sh` with the following content(which is modified based on [KB](https://cern.service-now.com/service-portal?id=kb_article&n=KB0006082)) and more details at [twiki](https://twiki.cern.ch/twiki/bin/view/CAE/AnsysService):<br />
```shell
. /afs/cern.ch/project/parc/ansys/19.2/cern/ansys192.shrc # this can be changed to whatever ANSYS version you like that existing.
/afs/cern.ch/project/parc/ansys/19.2/v192/ansys/bin/ansys192 -b nolist -np 8 -j myjob < inputfile.txt > ansys_stdout.txt
```
Note the following parameters used in the Ansys command:<br />
the -b option is essential, the 'nolist' keyword avoids echoing of the input file in the output file. the -np argument specifies the number of (SMP) "processors", and should correspond to the [RequestCpus](https://twiki.cern.ch/twiki/bin/edit/CAE/RequestCpus?topicparent=CAE.LinuxAnsys;nowysiwyg=1) in the HTCondor submit file, -p specifies the license type. the input file and the output file are specified through the < and > redirects. note that "output file" means : the standard output produced by Ansys APDL ; this is not to be confused with the standard output created by the batch job itself (its script) until further notice, it is recommended to stay away from Distributed Ansys (MPI) on HTCondor, and thus : do not use any of the -dis -machines -mpi -mpifile options, one shall not use the -acc option for GPU acceleration AA_R is short for ANSYS license ANSYS Academic Research Mechanical. (More information about ANSYS and licenses, please read the [twiki link](https://twiki.cern.ch/twiki/bin/view/CAE/AnsysService)).

***
**Prepare your HTCondor script**<br />
Create the following HTCondor job submission file that you can call, for example, `my_htcondor`:
```
executable           = my_script.sh
transfer_output_files = ""
output               = output/$(ClusterId).$(ProcId).out
error                = error/$(ClusterId).$(ProcId).err
log                  = log/$(ClusterId).log
+WCKey               = Ansys
queue
```

In the same folder as `my_htcondor` submission file, the folders output, error and log should be created (this is in AFS and not in EOS, don't get confussed!). You can create the folders using the command `mkdir`. i.e. `mkdir output`.<br />
Then run `condor_submit my_htcondor`.<br />
If your job was succesful, you can now proceed to the next section. If not, please, open a SNOW ticket describing your problems and we will help you.<br />
***
If you want to submit some large simulation works,<br />
Then, create an HTCondor job submission file `my_htcondor` in the following way:<br />
```
executable           = my_script.sh
RequestCpus          = 48
+BigMemJob           = True
+WCKey                = Ansys
+AccountingGroup     = "group_u_COMPUTING_GROUP.u_egroupname"
+JobFlavour          = "workday"
transfer_output_files = ""
output               = output/$(ClusterId).$(ProcId).out
error                = error/$(ClusterId).$(ProcId).err
log                  = log/$(ClusterId).log
queue
```
Then run `condor_submit my_htcondor`.

Please, note that:<br />
By default, the wall time limit of the job is 1h. Follow the instructions explained [here](http://batchdocs.web.cern.ch/batchdocs/local/submit.html) to define the proper `job flavour` according to your job needs. <br />
In the previous example, the job flavour `workday` has been selected. This defines a limit of 8h. Note that there is in principle no time limit to run on the cluster. <br />
There is no limit. If you want to go beyond 1 week (which is the maximum you could specify in the Job flavour), please, do not define the `JobFlavour` and define instead `+MaxRuntime = Number of seconds`.<br />

In this example, 48 cores have been selected. You will have to tune this parameter for your simulation. Make sure the number of cores specified in the HTCondor job submission file matches the parameter np in your script.<br />
Make sure you change the `group_u_COMPUTING_GROUP.u_egroupname` with a meaningful value like `group_u_EN.u_bigmem`. This information should be given to you by the IT team when granting access to the Big Memory nodes.<br />
***
**Useful HTCondor commands**<br />
Check the status of the job execution: `condor_q`<br />
Access the job's local files while it is running: `condor_ssh_to_job <jobid>`<br />
Check all the details about the job: `condor_q -better {job-id}`<br />
Check how the job was executed once it finishes: `condor_q JOBID -l`<br />
Check how long the job was running: `condor_history JOBID -limit 1 -af:h RemoteWallClockTime`<br />
Cancel a job: `condor_rm JOBID`<br />
For more information on using HTCondor, please check this [guide](http://batchdocs.web.cern.ch/batchdocs/index.html).<br />

### PyfieldTools
Tools based on python, Garfield++ and ROOT to make plots, etc.<br />
[checkFields.py](./PyfieldTools/checkFields.py): Make plots of eletric field or potential reading the electric field or potential lists get from ANSYS. (Example hard coding tool.)<br />

### Simulation

### Analysis

### NN implementation
