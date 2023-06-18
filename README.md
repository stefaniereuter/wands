# Wide Area Network Data Stream (wands)
UKAEA work with adios to transport data between fusion reactor and CSD3. This is a prototype and very much a work in progress. 

## Setup environment
<!-- The easiest way to run the code is to setup a conda environment and install adios2 as a conda package:

```bash
conda create -n <name> -c conda-forge adios2 numpy mpi4py h5py
```

Once the environment is created and all the packages are installed activate this environment:

```bash
conda activate <name>
``` -->

Dependencies:
Adios2: 
Wands requires Adios2 to send one dimensional arrays. https://github.com/ornladios/ADIOS2/pull/3545 fixed a bug that prevented using one dimensional arrays in python bindings of Adios2. To send data via wide area network, the Adios2's Dataman engine is used. If installed via spack both dataman and python need to be specified. 

Installation via Spack (in an environment):
```bash
spack env create <name>
spack env activate <name>
spack add adios2@2.9 +dataman +python
spack install
```

HDF5 and Boost are needed for for the CPP server and can, for example also be installed in the spack environment. 
```bash
spack add hdf5
spack add boost
spack install
```

To install wands it is recommended to create a virtual environment and use pip to install wands:
```bash
python -m venv <pip_env_name>
source <pip_env_name>/bin/activate
pip install -e .
```

It is possible to build and run only the cpp server on the data site. This means that the last pip environment step ins't needed. 
To run all pytests on the client side both, cpp server and python wands need to be built. 

## Testing the installation

To test the installation, run the test suite:

```bash
pytest
```

## Building and running  CPP Server

It is recommended to create a build directory in the server directory.
```bash
mkdir server/build
cd server/build
cmake ../
cmake --build .
./wands_server
```

## Running the prototype
CSD3 specific instructions to run the code:
1. start an interactive session on CSD3:

```bash 
salloc -t xx:xx:xx -Nx -ppnx -A <project-account> -p <partition> bash
```
2. inquire the IP adress of the allocated node:
``` bash
nslookup cpu-q-xxx.data.cluster
```
3. a) If you want to send data from a remote location to CSD3. At the moment this is done via ssh tunneling (started on remote machine)
```bash
ssh -R 12345:localhost:12345 -o ProxyJump=<login-node> <CSD3ID>@<IP from nslookup>
```

       
   b) Send data from CSD3 to remote machine also with an SSH tunnel (started on remote machine)
   
```bash
ssh -L 12345:localhost:12345 -o ProxyJump=<login-node> <CSD3ID>@<IP from nslookup>
```
  

    - Run server
```bash
cd <server/build> //or any other build directory chosen
./wands_server
```
    - Client code example 
```python
from wands import Wands

data_source = "file.h5"
signals = ["group1/dataset1","group2/dataset2"]

local_cache = "path/to/local/directory" # where signals will be saved for future requests
wo = Wands(local_cache, Port = "12345")
data_dict = wo.request(data_source, signals)

#use data
```
<!--         
   b) Send data from CSD3 to remote machine also with an SSH tunnel (started on remote machine)
   
```bash
ssh -L 12345:localhost:12345 -o ProxyJump=<login-node> <CSD3ID>@<IP from nslookup>
```
    - first start server on compute node: 
```bash
python dataman-server.py
```
    - then start receiver on remote host: 
```bash
python dataman-receiver.py -->
```
    
Note: Setting up an SSH tunnel with proxy jump requires two different TOTP tokens. 
