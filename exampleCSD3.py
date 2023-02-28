#ON CSD3
from wands import AdiosWands
import numpy as np

params={
    "IPAddress": "127.0.0.1",
    "Port": "12306",
    "Timeout": "5",
    "TransportMode": "reliable", 
    "RendezvousReaderCount": "1",
}

ads = AdiosWands(link="Stream_data", parameters=params)
print("adios object created")
file = "/home/stefanie/work/adios/adiosnetwork/data/30420.h5"
#req_var = ['xax/XAX_CHFS/2_PRELOAD','xbt/XBT/CHANNEL16']
req_var = 'xax/XAX_CHFS/2_PRELOAD'
#req_var = np.random.rand(4,6)
#req_var = np.ascontiguousarray(req_var)
reqvar_as_bytes = bytearray(req_var,"utf-8")
#req_var = np.array('xax/XAX_CHFS/2_PRELOAD')
print(type(req_var))
#data = ads.request_remote_data(req_data=req_var,data_source=file)
ads.send(eng_name= "IO1", var_name = "req_list",data=req_var)
print("data sent")
# print(data[0])
# print(data[1])
