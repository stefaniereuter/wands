import requests
from pathlib import Path
from .wan import WandsWAN
from .data_cache import DataCache

class Wands:
    """
    Entry class to wands
    """
    def __init__(self,data_cache_path:str, IPAddress = "127.0.0.1", 
                 Port = "8081" , Timeout = "30", TransportMode= "reliable",RendezvousReaderCount="1",
                 webaddress = "http://localhost:8080/data"):
        self._Adiosparams = {
            "IPAddress": IPAddress,
            "Port": Port,
            "Timeout": Timeout,
            "TransportMode" : TransportMode,
            "RendezvousReaderCount": RendezvousReaderCount,
            "Threading": "true",
        }

        self._webaddress = webaddress
        self.dataCache = DataCache(Path(data_cache_path))

    def cache_location(self):
        return self.dataCache.path_str()
    
    def request(self,filename:str, data_list: list) -> dict:
        """
        Request the needed data. This function will check if the data is available locally
        and otherwise request the data remotely.
        """
        from time import time
        #
        #remove locally available datasets from list
        print(f"request: type datalist: {type(data_list)}")
        data_from_remote = {}
        timereq = time()
        remote_list, local_list = self.dataCache.check_availability(filename=filename,data_list=data_list)

        timecheckav = time() 
        data_from_cache = self.dataCache.load_from_cache(filename=filename,local_list=local_list)
        timedatalocal = time()
        print(f"Signals found locally: {local_list}")
        print(f"Signals to be requested remotely: {remote_list}")
        if remote_list:
            data = {
                'uri': filename,
                'signals': remote_list,
            }
            response = requests.post(self._webaddress,json=data)
            print(response.status_code)
            print(response.json())
            wandsWAN_obj = WandsWAN(parameters = self._Adiosparams)
            
            data_from_remote = wandsWAN_obj.receive(remote_list)
            timeremote = time()
            self.dataCache.write(filename=filename,data_dict = data_from_remote)
            timewrite = time()
        print(f"Timings:\n check av = {timecheckav-timereq}\n t_lfc = {timedatalocal-timecheckav}\n ")
        if remote_list:
              print(f"t_getremote = {timeremote-timedatalocal}\n t_toDB = {timewrite-timeremote}")
        return data_from_remote | data_from_cache