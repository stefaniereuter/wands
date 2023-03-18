import adios2
import numpy as np
from pathlib import Path
from .adios import AdiosObject

class DataCache:
    """
    Use the received Data to build a local database 
    - sets path to datacache
    """

    def __init__(self, path:str, link = "datacache", engine = "BP5",parameters = None):
        """
        Set a path to a local data cache folder
        """
        self._adob = AdiosObject(link,engine,parameters)
        print(type(path))
        self._path = path


    def __str__(self):
        """
        Returns: string to print Datacache object
        """
        return f"Location: {self._path!s}"
        
    def path_str(self):
            return f"{self._path!s}"

    def write(self, filename:str, data_dict:dict):
        """
        Write data to file
        Parameters
        ----------

        filename: str 
            Name to file in database

        data_dict: dict
            Dictorionary of data with names added to file
        """
        if data_dict is None:
            raise TypeError("Dictionary is empty")
            
        #modify string to delete .hdf5 with string find
        bpfilename_path = self._path / filename.replace('.h5','.bp')
        print(bpfilename_path)
        writer = self._adob.getIO().Open(f"{bpfilename_path!s}",adios2.Mode.Write)

        writer.BeginStep()
        for var_name, data in data_dict.items():
            if self._adob.getIO().InquireVariable(var_name):
                print(f" Debug: variable {var_name!s} exists already")
                continue
            
            shape = data.shape
            print(f"shape in send: {shape!s}")
            count = shape
            print(f"count in send {count!s}")
            start = (0,) * len(shape)
            print(f"start in send {start!s}")
            sendbuffer = self._adob.getIO().DefineVariable(var_name, data, shape, start, count, adios2.ConstantDims )
            #writer.Put(sendbuf, data_dict[var_name], adios2.Mode.Deferred)
            writer.Put(sendbuffer,data,adios2.Mode.Deferred)
            #raise ValueError("Variable definition failed")
        
        writer.EndStep()
        writer.Close()

    def check_availability(self, filename:str, data_list:list) -> dict:
        """       
        Check if data is available in data cache. Return the local data if available and a list with signals that need to be requested remotely
        Parameters
        ----------

        returns
        --------
        
        """
        print( type(filename.replace('.h5','.bp')))
        print(self._path)
        print(type(self._path))
        bpfilename_path = self._path / filename.replace('.h5','.bp')
        print(type(bpfilename_path))
        print(f"check av: data type data_list: {type(data_list)}")
        #koennte probleme geben wenn nicht data and time als eigenes signal da sind
        print(f"Check availability")
        local_dict = {}
        remote_list = []
        print(f"trying to open {bpfilename_path}")
        if bpfilename_path.exists():
            reader = self._adob.getIO().Open(f"{bpfilename_path!s}", adios2.Mode.Read)
            print(f" after reader {reader!s}")
            if reader:
                print(f"found file {filename}")
                stepStatus = reader.BeginStep()
                if stepStatus == adios2.StepStatus.OK:
                
                    for signal in data_list:
                        variable = self._adob.getIO().InquireVariable(signal)
                        if variable:
                            print(f"found {signal} locally")
                            local_dict[signal] = variable
                        else:
                            print(f"{signal} added to remote request list")
                            remote_list.append(variable)
                else:
                    raise KeyError(f"Checking availability failed ")
                #send remote list to parallel process
                #call load from cache
                
                local_dict = self.read(reader, local_dict)
                reader.EndStep()
            reader.Close()
        else:
            print(f" file {bpfilename_path} not found")
            remote_list = data_list
            print(f"check av convert to remote list data type: {type(remote_list)}")
        return (remote_list,local_dict)
    
    def read(self, reader_obj, local_dict) -> dict:
        data_dict = {}
        for signal_name, variable in local_dict.items():

            data = np.zeros(variable.Shape(), dtype=variable.Type())
            reader_obj.Get(variable,data,adios2.Mode.Deferred)
            data_dict[signal_name] = data
        return data_dict
