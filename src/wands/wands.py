import requests
from pathlib import Path
from .wan import WandsWAN
from .data_cache import DataCache

class Wands:
    """
    Entry class to wands
    """
    def __init__(self,data_cache_path:str, IPAddress = "127.0.0.1", 
                 Port = "8081" , Timeout = "6", TransportMode= "reliable",RendezvousReaderCount="1",
                 webaddress = "http://localhost:8080/data"):
        self._Adiosparams = {
            "IPAddress": IPAddress,
            "Port": Port,
            "Timeout": Timeout,
            "TransportMode" : TransportMode,
            "RendezvousReaderCount": RendezvousReaderCount,
        }
        self._webaddress = webaddress
        self._dataCache_obj = DataCache(Path(data_cache_path))

    def cache_location(self):
        return self._dataCache_obj.path_str()
    
    def request(self,filename:str, data_list: list) -> dict:
        """
        Request the needed data. This function will check if the data is available locally
        and otherwise request the data remotely.
        """
        #
        #remove locally available datasets from list
        #TODO change to pass the empty dicts to check availability 
        print(f"request: type datalist: {type(data_list)}")
        data_from_remote = {}
        remote_list,data_from_cache_dict = self._dataCache_obj.check_availability(filename=filename,data_list=data_list)

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
            print("CHANGE SERVER TO SINGLE SIGNAL")
            self._dataCache_obj.write(filename=filename,data_dict = data_from_remote)
        return data_from_remote | data_from_cache_dict