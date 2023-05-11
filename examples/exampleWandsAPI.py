###Rest Server

from wands import Wands

# data = {
#     'uri': '30420.h5',
#     'signals': ["/xmc/XMC/ACQ196_143/CH01",
#                 "/xtb/XTB_201_1"],
# }
# data = {
#     'uri': '30420.h5',
#     'signals': ['/amc/AMC_PLASMA CURRENT'],
# }
#data = {
#     'uri': 'small_test_data.h5',
#     'signals': ['/signal1'],
#}
#data = {
#    'uri': '7000_1234_data.h5',
#    'signals': ['/signal1'],
#}
# data = {
#     'uri': '30420.h5',
#     'signals': ['/xtb/XTB_201_1'],
# }
# data = {
#    'uri': 'arraytest2.h5',
#    'signals': ['/signal1'],
# }

filename = "30420.h5"
# signals = ["/xmc/XMC/ACQ196_143/CH01/data",
#            "/xmc/XMC/ACQ196_143/CH01/time",
#            "/xtb/XTB_201_1/data",
#            "/xtb/XTB_201_1/time"]
signals = ["/xmc/XMC/ACQ196_143/CH01/data",
           "/xyc/XYC/305/2/BACKGROUND/data",
           "/xmc/XMC/ACQ196_143/CH01/time",
           "/xtb/XTB_201_1/data",
           "/xtb/XTB_201_1/time",]

# filename = "small_test_data.h5"
# signals = ["signal1/data"]
#local_path = "/home/sr2003/rds/rds-hpc-support-5mCMIDBOkPU/sr2003/UKAEA/wands_cache"
local_path = "/home/stefanie/work/adios/adiosnetwork/local_cache"
              
wo = Wands(local_path, Port="12345")
print(f"exampelwands {type(signals)}")
data_dict = wo.request(filename,signals)
print(data_dict)
#rdo_r = RawData(axis)
#rdo_r.convert_to_rawdata(data_r)
#print(rdo_r)
