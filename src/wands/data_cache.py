import adios2
import re
import numpy as np
from pathlib import Path
from .adios import AdiosObject


class DataCache:
    """
    Use the received Data to build a local database
    - sets path to datacache
    """

    def __init__(self, path: str, link="datacache", engine="BP4", parameters=None):
        """
        Set a path to a local data cache folder
        """
        self._adob = AdiosObject(link, engine, parameters)
        if isinstance(path, str):
            self._path = Path(path)
        elif isinstance(path, Path):
            self._path = path
        else:
            raise TypeError("Path needs to be of type string or of type pathlib.Path")

        if not self._path.exists():
            self._path.mkdir(parents=True, exist_ok=True)

    def __str__(self):
        """
        Returns: string to print Datacache object
        """
        return f"{self._path!s}"

    def close(self):
        self._adob.close()

    def get_IOParams(self):
        return self._adob.__str__()

    # def path_str(self):
    #         return f"{self._path!s}"

    def write(self, filename: str, data_dict: dict):
        """
        Write data to file
        Parameters
        ----------

        filename: str
            Name to file in database

        data_dict: dict
            Dictorionary of data with names added to file
        """
        if not isinstance(data_dict, dict):
            raise TypeError("write(<dict>)")

        if not bool(data_dict):
            raise TypeError("data_dict is empty")

        # modify string to delete .hdf5 with string find
        bpfilename_path = self._path / filename.replace(".h5", ".bp")
        # print(bpfilename_path)
        writer = self._adob.get_IO().Open(f"{bpfilename_path!s}", adios2.Mode.Append)

        writer.BeginStep()
        for var_name, data in data_dict.items():
            # Test if the variable already exists
            if self._adob.get_IO().InquireVariable(var_name):
                print(f" Debug: variable {var_name!s} exists already")
                continue

            shape = data.shape
            # print(f"shape in send: {shape!s}")
            count = shape
            # print(f"count in send {count!s}")
            start = (0,) * len(shape)
            # print(f"start in send {start!s}")
            sendbuffer = self._adob.get_IO().DefineVariable(
                var_name, data, shape, start, count, adios2.ConstantDims
            )
            # writer.Put(sendbuf, data_dict[var_name], adios2.Mode.Deferred)
            writer.Put(sendbuffer, data, adios2.Mode.Sync)
            # raise ValueError("Variable definition failed")

        ## option if we want to write updates to the variables in steps. currently not planned
        # shape = data.shape
        # #print(f"shape in send: {shape!s}")
        # count = shape
        # #print(f"count in send {count!s}")
        # start = (0,) * len(shape)
        # #print(f"start in send {start!s}")

        # #Test if the variable already exists
        # variable = self._adob.get_IO().InquireVariable(var_name)
        # if not variable:
        #     variable = self._adob.get_IO().DefineVariable(var_name, data, shape, start, count, adios2.ConstantDims )
        # #sendbuffer = self._adob.get_IO().DefineVariable(var_name, data, shape, start, count, adios2.ConstantDims )
        # #writer.Put(sendbuf, data_dict[var_name], adios2.Mode.Deferred)
        # writer.Put(variable,data,adios2.Mode.Sync)
        # #raise ValueError("Variable definition failed")

        writer.EndStep()
        writer.Close()

    def check_availability(self, filename: str, data_list: list):
        """
        Check if data is available in data cache. Return the local data if available and a list with signals that need to be requested remotely
        Parameters
        ----------

        returns
        --------

        """

        bpfilename_path = self._path / re.sub(".\w+$", ".bp", filename)

        local_list = []
        remote_list = []
        # print(f"trying to open {bpfilename_path}")
        if bpfilename_path.exists():
            reader = self._adob.get_IO().Open(f"{bpfilename_path!s}", adios2.Mode.Read)
            if reader:
                # returns a Dict[str,Dict[str,str]] e.g. variable['signal'] = {'Shape':'200','Type':'double'}
                variables = self._adob.get_IO().AvailableVariables()
                for signal in data_list:
                    if signal in variables:
                        local_list.append(signal)
                    else:
                        remote_list.append(signal)
            else:
                # This should never happen since we checked before that the file exists
                print(
                    f"[WARNING] Even though the {bpfilename_path!s} exists WANDS was unable to open it. Requesting all datasets remotely"
                )
                remote_list = data_list
            reader.Close()
        else:
            remote_list = data_list

        return (remote_list, local_list)

    def load_from_cache(self, filename: str, local_list: list):
        bpfilename_path = self._path / filename.replace(".h5", ".bp")
        # print(f"beginning of cache: {local_list!s}")
        # self._adob.print_info()
        local_dict = {}
        if local_list:
            if bpfilename_path.exists():
                reader = self._adob.get_IO().Open(
                    f"{bpfilename_path!s}", adios2.Mode.Read
                )
                if reader:
                    # TODO at the moment only the first step is written and read

                    while True:
                        stepStatus = reader.BeginStep()
                        # print(stepStatus)
                        if stepStatus == adios2.StepStatus.OK:
                            # print(f"Current Step: {reader.CurrentStep()!s} reader Steps= {reader.Steps()!s} local dict = {local_dict!s} ")
                            for signal in local_list:
                                if signal not in local_dict:
                                    variable = self._adob.get_IO().InquireVariable(
                                        signal
                                    )
                                    if variable:
                                        # print(variable.Type())
                                        data = np.zeros(
                                            variable.Shape(), dtype=variable.Type()
                                        )
                                        reader.Get(variable, data, adios2.Mode.Deferred)
                                        local_dict[signal] = data
                        elif stepStatus == adios2.StepStatus.EndOfStream:
                            break
                        else:
                            raise StopIteration(
                                f"next step failed to initiate {stepStatus!s}"
                            )

                        reader.EndStep()
                # print(f"call close next")
                reader.Close()
                # print(f"{bpfilename_path!s} closed")
                # print(local_list)
            else:
                raise ValueError(f" file {bpfilename_path} not found")

        # CHECK if all signals have been loaded
        for signal in local_list:
            if signal not in local_dict:
                raise KeyError(
                    f"load_from_cache: Signal {signal} marked as locally available but not found "
                )
        return local_dict
