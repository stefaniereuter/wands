"""
Tests to test the adios access api of wands
"""
import pytest
import numpy as np

from wands import AdiosWands

def test_init():
    params = {
        "IPAddress": "0.0.0.0",
        "Port": "12306",
        "Timeout": "5",
        "TransportMode": "reliable",
    }
    obj = AdiosWands(link = "testIO1", engine="Dataman",parameters=params)
    assert obj is not None
    assert obj._engine is "Dataman"
    assert obj._link is "testIO1"
    assert obj._io is not None
    assert obj.getIPAddress() == "0.0.0.0"
    assert obj.getPort() == "12306"
    assert obj.getTimeout() == "5"
    assert obj.getTransportMode() == "reliable"
    with pytest.raises(ValueError):
        obj = AdiosWands(link = "testIO1", engine="Dataman",parameters=params)
    
def test_init_seperateParameters():
    params = {
        "IPAddress": "0.0.0.3",
        "Port": "12345",
        "Timeout": "6",
        "TransportMode": "fast",
    }
    obj2 = AdiosWands(link = "testIO2")
    obj2.set_parameters(params)
    assert obj2 is not None
    assert obj2._engine is "Dataman"
    assert obj2._link is "testIO2"
    assert obj2._io is not None
    assert obj2.getIPAddress() == "0.0.0.3"
    assert obj2.getPort() == "12345"
    assert obj2.getTimeout() == "6"
    assert obj2.getTransportMode() == "fast"

# @pytest.fixture(autouse=True)
# def resetglobalIOperTest():
#     from wands.adios import adios_io
#     adios_io = None


#import logging
#import time
#import concurrent.futures

def thread_send(name:str):
# assert name == "sender_proc"
    paramssend = {
        "IPAddress": "127.0.0.1",
        "Port": "12307",
        "Timeout": "6",
        "TransportMode": "reliable",
        "RendezvousReaderCount": "1",
    }
    data = name.recv()
    #print(f"data on sender side \n{data!s}")
    #data = np.arange(20).reshape(4,5)
    #logging.info(f"Sender: creating Adiosobject")
    adios_s = AdiosWands(link="Sender",parameters=paramssend)
    #logging.info(f"Sender: initiating sending")
    adios_s.send("IOS", "testdata", data)
    #logging.info(f"Sender: sending finished")


def thread_receive(name:str):
   # assert name == "receiver_proc"
    paramsrec =  {
        "IPAddress": "127.0.0.1",
        "Port": "12307",
        "Timeout": "6",
        "TransportMode": "reliable",
        "RendezvousReaderCount": "1",
    }       
    #logging.info(f" Receiver: creating Adiosobject ")
    adios_r = AdiosWands(link="Reader",parameters=paramsrec)
    #logging.info(f" Receiver: initiating receiving ")
    data_r = adios_r.receive("IOS","testdata")
    #logging.info(f" Receiver: finished receiving",)
    print(f"data on recv side \n{data_r!s}")
    name.send(data_r)

@pytest.mark.timeout(20)
def test_send():
    from multiprocessing import Process, Pipe
    """
    Different test data arrays. 
    """
    #data = np.random.rand(1,20) #no but doesn't even override the initialized data array therefore result is all 1. Does not receive data at all?
    #data = np.arange(1,20) # receives random 0s
    #data = np.arange(1,21).reshape(4,5) # compared to the random array reshape does not help here still receives random 0s
    #data = np.full([4,5],7) # receives random 0s

    #data = np.random.rand(1,20).reshape(4,5) #works
    #data = np.ones([20,1])*7 #works
    #data = np.ones([4,5])
    data = np.random.rand(4,5) #works
    #format = "%(asctime)s: %(message)s"
    #logging.basicConfig(format=format, level=logging.INFO,
    #                    datefmt="%H:%M:%S")
    master_proc, receiver_proc = Pipe()
    sender_proc, master_proc2 = Pipe()
    #sender_proc, receiver_proc = None, None
    s = Process(target=thread_send, args=[sender_proc])
    r = Process(target=thread_receive,args=[receiver_proc])
    s.start()
    r.start()
    master_proc2.send(data)
    data_r = master_proc.recv()
    #data_r = None
    print(f"data in master \n{data_r!s}")
    r.join()
    s.join()
    assert np.array_equal(data, data_r)



## TODO test two declared IOs