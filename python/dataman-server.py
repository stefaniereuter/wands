import sys
import h5py
import numpy as np
import adios2

# import socket

# User data

# calculate global number of entries in per direction
Nx = 4
Ny = 4

nsteps = Ny
#count = [Nx, Ny]
#start = [0, 0]
#shape = [Nx, Ny]
#data = np.random.rand(Nx, Ny)
#

axis = "amc"
h5file = h5py.File("test.h5", 'r')
data = h5file[axis]
shape = data.shape
count = shape
# use io.BYtes to stream ?


print("------------------")
print(data)
print("maximum entry: ", data.max())
print("data mean: ", data.mean())
print("minimum entry: ", data.min())
adios = adios2.ADIOS()

# ADIOS IO
datamanServer = adios.DeclareIO("Server1")
# specify the used Engine BP5 writes a file Dataman sends data to waiting receiver code
# datamanServer.SetEngine('BP5')
datamanServer.SetEngine("Dataman")

# necessary parameters for dataman engine
# # print(socket.gethostbyaddr("cpu-q-526.data.cluster")[2][0] )

# IP: 0.0.0.0 "listens" to all incoming IPs on specified ports, Timeout is for the put get call after connection is established, Transport mode reliable is that all data is collected (fast would potentially loose some steps)
datamanServer.SetParameters(
    {
        "IPAddress": "0.0.0.0",
        "Port": "12306",
        "Timeout": "5",
        "TransportMode": "reliable",
    }
)


# ADIOS Engine
datamanWriter = datamanServer.Open("data1", adios2.Mode.Write)
sendbuffer = datamanServer.DefineVariable(
    axis, data, shape, start, count, adios2.ConstantDims
)
if sendbuffer:
    datamanWriter.BeginStep()
    datamanWriter.Put(sendbuffer, data)
    datamanWriter.EndStep()

datamanWriter.Close()


# #Compress data before send:
# sendbuffer2 = datamanServer.DefineVariable("matrix3",data,shape,start,count,adios2.ConstantDims)
# #{"accuracy":"0.01"}.type()
# sendbuffer2.AddOperation("zfp",{{"accuracy":"0.1"}})
# datamanWriter2 = datamanServer.Open("Fluesterpost_matrix", adios2.Mode.Write)
# datamanWriter.Put(sendbuffer2, data)
# datamanWriter2.Close()


# Send data in steps
datamanWriter3 = datamanServer.Open("Fluesterpost_matrix", adios2.Mode.Write)
data2 = np.random.rand(1, Nx)
sendbuffer3 = datamanServer.DefineVariable("matrix2", data2, [Nx, 1], [0, 0], [Nx, 1])
if sendbuffer3:
    for i in range(0, nsteps):
        stepdatasize = Nx + i
        data2 = np.random.rand(1, stepdatasize)
        sendbuffer3.SetShape([stepdatasize, 1])
        sendbuffer3.SetSelection([[0, 0], [stepdatasize, 1]])
        # sendbuffer3 = datamanServer.DefineVariable("matrix2",data2,[stepdatasize,1],[0,0],[stepdatasize,1],adios2.ConstantDims)
        print("step data: ", data2[:])
        datamanWriter3.BeginStep()
        datamanWriter3.Put(sendbuffer3, data2)
        datamanWriter3.EndStep()

datamanWriter3.Close()
