import sys
from mpi4py import MPI
import numpy as np
import adios2
#TODO FIX MPI PARLLEL DATA INCORRECT
# User data

nxlocal = 2


# global MPI stats
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
nsteps = 10

#create cartesian topology
# number of dims each direction
size2d = int(size**0.5)
#Cart_create(old communicator, dims, #dims each direction, periodic each direction, reorder)
comm2d = comm.Create_cart(dims=[ size2d, size2d], periods=[False,False], reorder=False) 
rank2d = comm2d.Get_coords(rank) 
print("in 2d topology processor ", rank, " has coordinates ", rank2d)
print(" number of processses", size)

#calculate global number of entries in per direction
Nx = 2
Ny = 2
count = [Nx, Ny]
start = [rank2d[0]*Nx, rank2d[1]*Ny]
shape = [size2d*Nx, size2d*Ny]
print("start: ",start)
data = np.zeros(Nx*Ny, int)

for i in range(0,Nx):
    iglob = rank*100+i*10

    for j in range(0,Ny):
        value = iglob + j
        data[i*Nx+j] = value
        print(str(i)+","+str(j)+","+str(value))

print("------------------")
print(data)
adios = adios2.ADIOS(comm)

# ADIOS IO
datamanIO = adios.DeclareIO("randomBPfile")
datamanIO.SetEngine('Dataman')
datamanIO.SetParameters({"IPAddress":"127.0.0.1" , "Port":"12306", "Timeout":"5", "TransportMode":"reliable" })



# fileID = bpIO.AddTransport('File', {'Library': 'fstream'})

#mymatrix = np.ones((nxlocal,nxlocal))*(rank+1) #np.random.rand(nxlocal,nxlocal)
#print(mymatrix)
#print("start offset ",(rank2d[0]*nxlocal,rank2d[1]*nxlocal))
# ADIOS Variable name, shape, start, offset, constant dims

#ioVAR = bpIO.DefineVariable(
#    "bpMatrixglobal",mymatrix, (Nx,Ny), (rank2d[0]*nxlocal,rank2d[1]*nxlocal), (nxlocal,nxlocal))

ioglobalVar = datamanIO.DefineVariable("matrix",data,shape,start,count,adios2.ConstantDims)

# ADIOS Engine
datamanWriter = datamanIO.Open("Fluesterpost_matrix", adios2.Mode.Write)
for i in range(0,nsteps):
    data = data + 1
    print("step: ", i, data)
    datamanWriter.BeginStep()
    datamanWriter.Put(ioglobalVar, data)
    datamanWriter.EndStep()

datamanWriter.Close()




