import sys
from mpi4py import MPI
import numpy as np
import adios2

# User data

nxlocal = 2


# global MPI stats
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
nsteps = 1;

#create cartesian topology
# number of dims each direction
size2d = int(size**0.5)
#Cart_create(old communicator, dims, #dims each direction, periodic each direction, reorder)
comm2d = comm.Create_cart(dims=[ size2d, size2d], periods=[False,False], reorder=False) 
rank2d = comm2d.Get_coords(rank) 
print("in 2d topology processor ", rank, " has coordinates ", rank2d)
print(" number of processses", size)

#calculate global number of entries in per direction
Nx = nxlocal*size2d
Ny = Nx

print("global size Nx= ",Nx)
adios = adios2.ADIOS(comm)

# ADIOS IO
bpIO = adios.DeclareIO("randomBPfile")
bpIO.SetEngine('bp5')


# fileID = bpIO.AddTransport('File', {'Library': 'fstream'})

#mymatrix = np.ones((nxlocal,nxlocal))*(rank+1) #np.random.rand(nxlocal,nxlocal)
#print(mymatrix)
print("start offset ",(rank2d[0]*nxlocal,rank2d[1]*nxlocal))
# ADIOS Variable name, shape, start, offset, constant dims

#ioVAR = bpIO.DefineVariable(
#    "bpMatrixglobal",mymatrix, (Nx,Ny), (rank2d[0]*nxlocal,rank2d[1]*nxlocal), (nxlocal,nxlocal))

ioglobalVar = bpIO.DefineVariable("bpMatrixglobal",np.ones((nxlocal,nxlocal)),(Nx,Ny), (rank2d[0]*nxlocal,rank2d[1]*nxlocal), (nxlocal,nxlocal))

# ADIOS Engine
bpFileWriter = bpIO.Open("Matrix.bp", adios2.Mode.Write)

for step in range(nsteps):
    bpFileWriter.BeginStep()
    mymatrix = np.ones((nxlocal,nxlocal))*(rank+1)+step #np.random.rand(nxlocal,nxlocal)
    print("local matrix ", mymatrix)
    bpFileWriter.Put(ioglobalVar, mymatrix, adios2.Mode.Sync)
    bpFileWriter.EndStep()

bpFileWriter.Close()


if rank == 0:
    bpIOin = adios.DeclareIO("IOReader")
    bpFileReader = bpIOin.Open("Matrix.bp", adios2.Mode.Read)

    matrix_in = bpIOin.InquireVariable("bpMatrixglobal")
    if matrix_in is not None:
        matrix_in.SetSelection([[2,2],[4,4]])
        matrixsize=matrix_in.SelectionSize()
        print("Matrix dimension: ", str(matrixsize))
        matrixdata = np.zeros(matrixsize)
        bpFileReader.Get(matrix_in,matrixdata, adios2.Mode.Sync)

    bpFileReader.Close()
    print(matrixdata)





