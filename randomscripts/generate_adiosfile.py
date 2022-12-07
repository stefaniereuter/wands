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
nsteps = 1

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
bpIO = adios.DeclareIO("randomBPfile")
bpIO.SetEngine('bp5')


# fileID = bpIO.AddTransport('File', {'Library': 'fstream'})

#mymatrix = np.ones((nxlocal,nxlocal))*(rank+1) #np.random.rand(nxlocal,nxlocal)
#print(mymatrix)
#print("start offset ",(rank2d[0]*nxlocal,rank2d[1]*nxlocal))
# ADIOS Variable name, shape, start, offset, constant dims

#ioVAR = bpIO.DefineVariable(
#    "bpMatrixglobal",mymatrix, (Nx,Ny), (rank2d[0]*nxlocal,rank2d[1]*nxlocal), (nxlocal,nxlocal))

ioglobalVar = bpIO.DefineVariable("bpMatrixglobal",data,shape,start,count,adios2.ConstantDims)

# ADIOS Engine
bpFileWriter = bpIO.Open("Matrix.bp", adios2.Mode.Write)

bpFileWriter.Put(ioglobalVar, data, adios2.Mode.Sync)

bpFileWriter.Close()


# if rank == 0:
#     bpIOin = adios.DeclareIO("IOReader")
#     bpFileReader = bpIOin.Open("Matrix.bp", adios2.Mode.Read)

#     data_in = bpIOin.InquireVariable("bpMatrixglobal")
#     print(data_in.Name())
    
#     #shape = data_in.Shape()
#     #print(shape)
#         # matrixdata = np.zeros(np.prod(shape), int)
#         # print("Matrix dimension: ", str(np.prod(shape)))
        
#         # bpFileReader.Get(data_in,matrixdata, adios2.Mode.Sync)

#     #bpFileReader.Close()
#     #print(matrixdata)





