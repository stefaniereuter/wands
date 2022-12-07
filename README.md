# adiosnetwork
UKAEA work with adios to transport data between fusion reactor and CSD3. This is a prototype and very much a work in progress. 

## setup environment

To run the code: 
Create a conda environment: 
    '''conda create -n <name> -c conda-forge adios2 numpy mpi4py'''

activate/create that environment on every host either server or receiver code is suppposed to run on. 

## running the prototype
1. start an interactive session on CSD3:
    ''' salloc -t xx:xx:xx -Nx -ppnx -A <project-account> -p <partition> bash'''
2. inquire the IP adress of allocated node:
    '''nslookup cpu-q-xxx.data.cluster'''
3. a) If you want to send data from  remote location to csd3 atm via ssh tunnel (started on remote machine)
    '''ssh -R 12345:localhost:12345 0o ProxyJump=<CSD3SSHAlias> <CSD3ID>@<IP from nslookup>'''
    - first start server on remote machine: '''python dataman-server.py'''
    - then start receiver on CSD3 node: '''python dataman-receiver.py'''
b) Send data from CSD3 to remote machine also with an SSH tunnel (started on remote machine) :
    '''ssh -L 12345:localhost:12345 -o ProxyJump=<CSD3SSHAlias> <CSD3ID>@<IP from nslookup>'''
    - first start server on compute node: '''python dataman-receiver.py'''
    - then start receiver on remote host: '''python dataman-receiver.py'''