###Rest Server

from wands import WandsWAN, RawData
import requests

data = {
    "uri": "30420.h5",
    "signals": ["/xmc/XMC/ACQ196_143/CH01", "/xtb/XTB_201_1"],
}
# data = {
#     'uri': '30420.h5',
#     'signals': ['/amc/AMC_PLASMA CURRENT'],
# }
# data = {
#     'uri': 'small_test_data.h5',
#     'signals': ['/signal1'],
# }
# data = {
#    'uri': '7000_1234_data.h5',
#    'signals': ['/signal1'],
# }
# data = {
#     'uri': '30420.h5',
#     'signals': ['/xtb/XTB_201_1'],
# }
# data = {
#    'uri': 'arraytest2.h5',
#    'signals': ['/signal1'],
# }


response = requests.post("http://localhost:8080/data", json=data)

print(response.status_code)
print(response.json())

params = {
    "IPAddress": "127.0.0.1",
    "Port": "8081",
    "Timeout": "6",
    "TransportMode": "reliable",
    "RendezvousReaderCount": "1",
}

# axis = ["/xmc/XMC/ACQ196_143/CH01","xbt/XBT/CHANNEL16"]
# axis = ['A','B']
adios_r = WandsWAN(link="Reader", parameters=params)
data_dict = adios_r.receive_dict_arrays("IOS", data["signals"])
print(data_dict)
# rdo_r = RawData(axis)
# rdo_r.convert_to_rawdata(data_r)
# print(rdo_r)
