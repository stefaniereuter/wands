
import numpy as np
from multiprocessing import Process, Pipe
import logging
import adios2

"""
Different test data arrays. 
"""


print("====================================")

#data2 = np.arange(3) #receives wrong data
#data2 = np.arange(3,dtype=np.float32) # receives wrong data
#data2 = np.arange(3,dtype=np.float64) # works
data2 = np.arange(3,dtype=np.float128) #receives wrong data
#data2 = np.arange(3,dtype=int) # receives wrong data
#data2 = np.random.randint(2, size=10) #receives wrong data
print(f"data dtypes: {data2.dtype!s}")


adios_io = adios2.ADIOS()
wan = adios_io.DeclareIO("Client")
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
            data_r = np.ones(bufshape)
            #print(f"data before Get: \n{data!s}")
            reader.Get(recvar,data_r,adios2.Mode.Sync)
            #print(f"data right after get This might be not right as data might not have been sent yet \n: {data!s}")
        else:
            raise ValueError(f"InquireVariable failed")
        recstr = wan.InquireVariable("stringdata")
        if recstr: 
          
            data_s = ""
            #print(f"data before Get: \n{data!s}")
            reader.Get(recvar,data_s)
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

print(f"received data = {data_r}")
print(f"Received string: {data_s}")
assert np.array_equal(data2, data_r)
