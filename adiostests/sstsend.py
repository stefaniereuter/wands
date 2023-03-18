
import numpy as np
from multiprocessing import Process, Pipe
import logging
import adios2


"""
Different test data arrays. 
"""
#data2 = np.arange(3) #receives wrong data
#data2 = np.arange(3,dtype=np.float32) # receives wrong data
#data2 = np.arange(3,dtype=np.float64) # works
data2 = np.arange(3,dtype=np.float128) #receives wrong data
#data2 = np.arange(3,dtype=int) # receives wrong data
#data2 = np.random.randint(2, size=10) #receives wrong data
print(f"data dtypes: {data2.dtype!s}")
stringdata = "hello receiver"

 #receive data from main thread
shape = data2.shape
count = shape
start = (0,)*len(shape)
print(f"data on sender side \n{data2!s}")

adios_io = adios2.ADIOS()
wan = adios_io.DeclareIO("Server")
wan.SetEngine("SST")

wan.SetParameters(
    {
        # "IPAddress": "0.0.0.0",
        # "Port": "12306",
        # "Timeout": "5",
        # "TransportMode": "reliable",
        "RendezvousReaderCount":"1",
    }
)
logging.info(f"Sender: initiating sending")
writer = wan.Open("testdatafile", adios2.Mode.Write)
sendbuffernp = wan.DefineVariable("np_data",data2, shape, start, count, adios2.ConstantDims)

sendbufferstr = wan.DefineVariable("stringdata")

writer.BeginStep()
writer.Put(sendbuffernp,data2,adios2.Mode.Sync)
writer.Put(sendbufferstr,stringdata)
writer.EndStep()


writer.Close()

logging.info(f"Sender: sending finished")


