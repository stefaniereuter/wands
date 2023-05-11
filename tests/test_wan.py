import numpy as np
from wands import WandsWAN
import pytest

# @pytest.fixture(autouse=True)
# def resetglobalIOperTest():
#     from wands.adios import adios_io
#     adios_io = None

def test_init():
    obj = WandsWAN()
    assert obj is not None

def test_string():
    obj = WandsWAN()
    assert type(obj.__str__()) is str


import time
import concurrent.futures

def thread_send(name:str):
    paramssend = {
        "IPAddress": "127.0.0.1",
        "Port": "12307",
        "Timeout": "6",
        "TransportMode": "reliable",
        "RendezvousReaderCount": "1",
    }
    data = name.recv()
    adios_s = WandsWAN(link="Sender",parameters=paramssend)
    adios_s.send( var_name="testdata", data = data, eng_name="WAN")

def thread_receive(name:str):
    paramsrec =  {
        "IPAddress": "127.0.0.1",
        "Port": "12307",
        "Timeout": "6",
        "TransportMode": "reliable",
        "RendezvousReaderCount": "1",
    }       
    adios_r = WandsWAN(link="Reader",parameters=paramsrec)
    data_r = adios_r.receive("testdata")
    name.send(data_r)

def test_send_randomMatrix():
    from multiprocessing import Process, Pipe
    """
    Different test data arrays. 
    """

    #data = np.random.rand(20,1) #no exact 0 or 1 depends about the value I set in adios.py to preallocate the array
    #data = np.random.rand(1,20).reshape(4,5) #workds
    #data = np.arange(1,20) # no random almost 0
    #data = np.arange(1,21).reshape(4,5) +1
    #data = np.full([4,5],7) # no random almost 0
    #data = np.ones([20,1,1])*7 #works
    data = np.random.rand(4,5) #works
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

def test_send_arange_vector():
    from multiprocessing import Process, Pipe
    """
    Different test data arrays. 
    """

    #data = np.random.rand(20,1) #no exact 0 or 1 depends about the value I set in adios.py to preallocate the array
    #data = np.random.rand(1,20).reshape(4,5) #workds
    data = np.arange(1,20) # no random almost 0

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

def test_send_randomvector():
    from multiprocessing import Process, Pipe
    """
    Different test data arrays. 
    """

    data = np.random.rand(20,1) 
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

    #TODO test sending multiple arrays