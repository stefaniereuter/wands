
import numpy as np
from multiprocessing import Process, Pipe
import logging
import adios2

def thread_send(name:str):

    data = name.recv() #receive data from main thread
    shape = data.shape
    count = shape
    start = (0,)*len(shape)
    print(f"data on sender side \n{data!s}")

    adios_io = adios2.ADIOS()
    sstIO = adios_io.DeclareIO("Server")
    sstIO.SetEngine("SST")

    logging.info(f"Sender: initiating sending")
    writer = sstIO.Open("testdatafile", adios2.Mode.Write)
    sendbuffer = sstIO.DefineVariable("np_data",data, shape, start, count, adios2.ConstantDims)
    if sendbuffer:
        writer.BeginStep()
        writer.Put(sendbuffer,data,adios2.Mode.Sync)
        writer.EndStep()
    else:
        raise ValueError("DefineVariable failed")
    
    writer.Close()
  
    logging.info(f"Sender: sending finished")

def thread_receive(name:str):

    adios_io = adios2.ADIOS()
    wan = adios_io.DeclareIO("Client")
    wan.SetEngine("SST")
 
    logging.info(f" Receiver: initiating receiving ")
    reader = wan.Open("testdatafile", adios2.Mode.Read)
    while True:
        stepStatus = reader.BeginStep()
        if stepStatus == adios2.StepStatus.OK:
            #inquire for variable
            recvar = wan.InquireVariable("np_data")
            if recvar:
                # determine the shape of the data that will be sent
                bufshape = recvar.Shape()
                # allocate buffer for now numpy
                data = np.ones(bufshape)
                #print(f"data before Get: \n{data!s}")
                reader.Get(recvar,data,adios2.Mode.Sync)
                #print(f"data right after get This might be not right as data might not have been sent yet \n: {data!s}")
            else:
                raise ValueError(f"InquireVariable failed")
        elif stepStatus == adios2.StepStatus.EndOfStream:
            break
        else: 
            raise StopIteration(f"next step failed to initiate {stepStatus!s}")
        reader.EndStep()
        #print(f"After end step \n{data!s}")
    reader.Close()
    #print(f"after close \n {data!s}")
    logging.info(f" Receiver: finished receiving",)
    name.send(data)

"""
Different test data arrays. 
"""
#data = np.random.rand(1,3) #no but doesn't even override the initialized data array therefore result is all 1. Does not receive data at all?
# data = np.random.rand(3)
# print("====================================")
# print(f"Dimension of data: {data.ndim!s}")
# print(f"Shape of data: {data.shape!s}")
# print(f"type {type(data)!s}")
# print(f"data base: {data.base!s}")
# print(f"ctypes: {data.ctypes!s}")
# print(f"data dtypes: {data.dtype!s}")
# print(f"data flags: {data.flags!s}")
# print(f"data flat: {data.flat!s}")
# print(f"data imag: {data.imag!s}")
# print(f"data itemsize: {data.itemsize!s}")
# print(f"data nbytes:  {data.nbytes!s}")
# print(f"data real: {data.real!s}")
# print(f"data size: {data.size!s}")
# print(f"data strides: {data.strides!s}")
# print(f"data T: {data.T!s}")

print("====================================")

#data2 = np.arange(3) #receives wrong data
#data2 = np.arange(3,dtype=np.float32) # receives wrong data
data2 = np.arange(3,dtype=np.float64) # works
#data2 = np.arange(3,dtype=np.float128) #receives wrong data
#data2 = np.arange(3,dtype=int) # receives wrong data
#data2 = np.random.randint(2, size=10) #receives wrong data
print(f"Dimension of data: {data2.ndim!s}")
print(f"Shape of data: {data2.shape!s}")
print(f"type {type(data2)!s}")
print(f"data base: {data2.base!s}")
print(f"ctypes: {data2.ctypes!s}")
print(f"data dtypes: {data2.dtype!s}")
print(f"data flags: {data2.flags!s}")
print(f"data flat: {data2.flat!s}")
print(f"data imag: {data2.imag!s}")
print(f"data itemsize: {data2.itemsize!s}")
print(f"data nbytes:  {data2.nbytes!s}")
print(f"data real: {data2.real!s}")
print(f"data size: {data2.size!s}")
print(f"data strides: {data2.strides!s}")
print(f"data T: {data2.T!s}")

#data = np.arange(1,21).reshape(4,5) # compared to the random array reshape does not help here still receives random 0s
#data = np.full([4,5],7) # receives random 0s

#data = np.random.rand(1,20).reshape(4,5) #works
#data = np.ones([20,1])*7 #works
#data = np.ones([4,5]) #works
#data = np.random.rand(4,5) #works
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO,
                    datefmt="%H:%M:%S")
master_proc, receiver_proc = Pipe()
sender_proc, master_proc2 = Pipe()
s = Process(target=thread_send, args=[sender_proc])
r = Process(target=thread_receive,args=[receiver_proc])
s.start()
r.start()
master_proc2.send(data2)
data_r = master_proc.recv()
#data_r = None
print(f"data in master \n{data_r!s}")
r.join()
s.join()
assert np.array_equal(data2, data_r)
