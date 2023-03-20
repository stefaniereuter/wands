import adios2
import numpy as np
from pathlib import Path
from .adios import AdiosObject

class DataCache:
    """
    Use the received Data to build a local database 
    - sets path to datacache
    """

    def __init__(self, path:str, link = "datacache", engine = "BP4",parameters = None):
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
        writer = self._adob.get_IO().Open(f"{bpfilename_path!s}",adios2.Mode.Append)

        writer.BeginStep()
        for var_name, data in data_dict.items():
            if self._adob.get_IO().InquireVariable(var_name):
                print(f" Debug: variable {var_name!s} exists already")
                continue
            
            shape = data.shape
            print(f"shape in send: {shape!s}")
            count = shape
            print(f"count in send {count!s}")
            start = (0,) * len(shape)
            print(f"start in send {start!s}")
            sendbuffer = self._adob.get_IO().DefineVariable(var_name, data, shape, start, count, adios2.ConstantDims )
            #writer.Put(sendbuf, data_dict[var_name], adios2.Mode.Deferred)
            writer.Put(sendbuffer,data,adios2.Mode.Sync)
            #raise ValueError("Variable definition failed")
        
        writer.EndStep()
        writer.Close()

    def check_availability(self, filename:str, data_list:list):
        """       
        Check if data is available in data cache. Return the local data if available and a list with signals that need to be requested remotely
        Parameters
        ----------

        returns
        --------
        
        """
        #print( type(filename.replace('.h5','.bp')))
        #print(self._path)
        #print(type(self._path))
        bpfilename_path = self._path / filename.replace('.h5','.bp')
        #print(type(bpfilename_path))
        #print(f"check av: data type data_list: {type(data_list)}")
        print(f"Check availability")
        local_list = []
        remote_list = []
        #print(f"trying to open {bpfilename_path}")
        if bpfilename_path.exists():
            reader = self._adob.get_IO().Open(f"{bpfilename_path!s}", adios2.Mode.Read)
            if reader:
                #returns a Dict[str,Dict[str,str]] e.g. variable['signal'] = {'Shape':'200','Type':'double'}
                variables = self._adob.get_IO().AvailableVariables() 
                for signal in data_list:
                    if signal in variables:
                        local_list.append(signal)
                    else:
                        remote_list.append(signal)
            else: 
                remote_list = data_list
            reader.Close()
        else:
            remote_list = data_list
    
        return (remote_list,local_list) 
    

    def load_from_cache(self, filename:str, local_list:list):

        bpfilename_path = self._path / filename.replace('.h5','.bp')

        local_dict = {}
        if local_list:
            if bpfilename_path.exists():
                reader = self._adob.get_IO().Open(f"{bpfilename_path!s}", adios2.Mode.Read)
                if reader:
                    #TODO ideally only read from last step. but needs to be checked if all variables are present in the last step

                    while True:
                        stepStatus = reader.BeginStep()
                        if stepStatus == adios2.StepStatus.OK:
                            
                            for signal in local_list:
                                if signal not in local_dict:
                                    variable = self._adob.get_IO().InquireVariable(signal)
                                    if variable:
                                        data = np.zeros(variable.Shape(), dtype=variable.Type())
                                        reader.Get(variable,data,adios2.Mode.Deferred)
                                        local_dict[signal] = data
                        elif stepStatus == adios2.StepStatus.EndOfStream:
                            break
                        else:
                            raise StopIteration(f"next step failed to initiate {stepStatus!s}")
                        
                        reader.EndStep()
                reader.Close()
            else:
                print(f" file {bpfilename_path} not found")


        #CHECK if all signals have been loaded
        for signal in local_list:
            if signal not in local_dict:
                raise KeyError(f"load_from_cache: Signal {signal} marked as locally available but not found ")
        return local_dict
    
