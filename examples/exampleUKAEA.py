###TEST1 send one Raw data struct
from wands import AdiosWands, HDF5

params = {
    "IPAddress": "127.0.0.1",
    "Port": "12307",
    "Timeout": "6",
    "TransportMode": "reliable",
    "RendezvousReaderCount": "1",
}

hdf5f = "../data/30420.h5"
axis = "/xmc/XMC/ACQ196_143/CH01"
h5obj = HDF5(hdf5f)
rdo = h5obj.getaxis(axis)

adios_s = AdiosWands(link="Sender", parameters=params)
adios_s.send("IOS", "testdata", rdo)

print(rdo)
