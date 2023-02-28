###TEST 1: Send data RAW data (time, data, error)

from wands import AdiosWands, RawData

params =  {
    "IPAddress": "127.0.0.1",
    "Port": "12307",
    "Timeout": "6",
    "TransportMode": "reliable",
    "RendezvousReaderCount": "1",
}       
axis = "/xmc/XMC/ACQ196_143/CH01"

adios_r = AdiosWands(link="Reader",parameters=params)
data_r = adios_r.receive("IOS","testdata")

rdo_r = RawData(axis)
rdo_r.convert_to_rawdata(data_r)
print(rdo_r)