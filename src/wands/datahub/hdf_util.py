# all hdf5 file operations

import h5py
import numpy as np
import warnings


class RawData_fusion:
    """
    Dataclass for Raw Fusion Data
    contsisting of Name _name
    Time array _time
    Data array _data
    Error array _error
    Attributes for group: _group_attr
    Attributes for time: _time_attr
    """

    def __init__(self, name: str):
        """
        Parameters:
            name: Name of data
        """
        self._name = name
        self._data = None
        self._time = None
        self._errors = None
        self._time_attr = {}
        self._group_attr = {}

    def __str__(self):
        return f"{self.get_name()!s}: \n data = {self.get_data()} \n time = {self.get_time()} \n time attributes {self.get_time_attr()} \n errors = {self.get_errors()} \n group attributes = {self.get_group_attr()}  "

    def set_data(self, data):
        self._data = data

    def get_data(self):
        return self._data

    def set_time(self, time):
        self._time = time

    def get_time(self):
        return self._time

    def set_errors(self, errors):
        self._errors = errors

    def get_errors(self):
        return self._errors

    def get_name(self):
        return self._name

    def set_time_attr(self, time_attr):
        self._time_attr = time_attr

    def get_time_attr(self):
        return self._time_attr

    def set_group_attr(self, group_attr):
        self._group_attr = group_attr

    def get_group_attr(self):
        return self._group_attr

    def convert_to_rawdata_fusion(self, nd_array):
        convert_nd_to_rawdata_fusion(nd_array, self)


class HDF5_fusion:
    """
    HDF5 utils, includes, request special dataset

    """

    def __init__(self, filename: str, h5mode="r"):
        """
        Creates a H5 object while opening the H5 file

        Parameter:
            filename: HDF5 file to open

            h5mode: Modus in which file will be opened refer to valid file modes in h5py (r,r+,w,w-,x,a)
                default: read only
        """

        self._file = h5py.File(filename)
        if not self._file:
            raise KeyError(f"Opening of {filename!s} failed")

    def getsignal(self, axis: str):
        """
        Request a set of raw data (time, error ,data array)

        Parameters
        ----------
        axis : str
            Name to request from the known HDF5 file. Indexed against
            the HDF5 file object by the connected ADIOSServer instance.

            Collected like: file_object[axis]

            Therefore axis values may include / to specify sub elements
            in the HDF5 hierarchy.

            We query for the different entities like errors, data, and times

        Return
        ----------
        A raw data object
        """
        raw_data = RawData_fusion(axis)
        try:
            raw_data.set_data(self._file.get(axis + "/data")[()])
        except:
            # don't raise an error as this might be expected behaviour as not always all three components are available
            warnings.warn(
                f"Dataset {axis!s}/data could not be loaded. This might be expected behaviour"
            )

        try:
            raw_data.set_errors(self._file.get(axis + "/errors")[()])
        except:
            # don't raise an error as this might be expected behaviour as not always all three components are available
            warnings.warn(
                f"Dataset {axis!s}/errors could not be loaded. This might be expected behaviour"
            )

        try:
            raw_data.set_time(self._file.get(axis + "/time")[()])
        except:
            # don't raise an error as this might be expected behaviour as not always all three components are available
            warnings.warn(
                f"Dataset {axis!s}/time could not be loaded. This might be expected behaviour"
            )

        try:
            time_attr = {}
            for k in self._file.get(axis + "/time").attrs.keys():
                time_attr[k] = self._file.get(axis + "/time").attrs[k]
            raw_data.set_time_attr(time_attr)
            time_attr = None
        except:
            raise KeyError(f"Reading the attributes for {axis!s}/time failed")

        try:
            group_attr = {}
            for k in self._file.get(axis).attrs.keys():
                group_attr[k] = self._file.get(axis).attrs[k]
            raw_data.set_group_attr(group_attr)
            group_attr = None
        except:
            raise KeyError(f"Reading the attributes for {axis!s} failed")

        return raw_data


# Needed because of a potential bug in adios. data can't be sent in a 1d array and afterwards needs to be converted back
# this is very buggy as I assume that if it's a 1xelements array it's [time] 2xelements it's [time,data] 3xelements it's [time,data,error]
# this is only a temporary fix as ideally the data should be sent seperately
def convert_nd_to_rawdata_fusion(recarray, raw_data_object: RawData_fusion):
    shape = recarray.shape
    if shape[0] == 3:
        raw_data_object.set_time(recarray[0, :])
        raw_data_object.set_data(recarray[1, :])
        raw_data_object.set_errors(recarray[2, :])
    elif shape[0] == 2:
        raw_data_object.set_time(recarray[0, :])
        raw_data_object.set_data(recarray[1, :])
    elif shape[0] == 1:
        raw_data_object.set_time(recarray[0, :])
    else:
        raise ValueError("unsupported shape of data array")
