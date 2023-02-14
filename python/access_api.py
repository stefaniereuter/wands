import numpy as np
import adios2
import h5py

from typing import Iterable

class ADIOSData:
    """
    Access data through ADIOS.

    Class to allow connection to ADIOSServer classes via a specified engine.
    """
    _adios = None
    _parameters = None
    _io = None
    _link = None
    _engine = None

    def __init__(self,
                 link: str,
                 engine="Dataman",
                 **parameters):
        """
        Parameters
        ----------
        link : str
            Name to connect to
        engine : str
            Engine to request data through. Default : Dataman
        **parameters
            Parameters to pass to the engine for initialisation.

        """
        self._adios = adios2.ADIOS()
        self._io = adios.DeclareIO(self._link:=link)
        self._io.SetEngine(self._engine:=engine)
        if parameters:
            self.set_parameters(self._parameters:=parameters)

    def __getitem__(self,
                    axis: str)->Iterable:
        """
        Request a given HDF5 axis from the specified link.

        Parameters
        ----------
        axis : str
            Name to request from the known HDF5 file. Indexed against
            the HDF5 file object by the connected ADIOSServer instance.

            Collected like: file_object[axis]

            Therefore axis values may include / to specify sub elements
            in the HDF5 heirarchy.

        Returns
        -------
        Iterable
            np.ndarray or similar of the requested data.

        Raises
        ------
        KeyError
            If axis is not found when indexed against the HDF5 source.
        """
        # TODO implement raise KeyError
        # Send name of axis across
        axis_writer = self._io.Open("axis" + self._link, adios2.Mode.Write)

        axis_as_bytes = bytearray(axis, "utf-8")

        sendbuffer = self._io.DefineVariable("axis",
                                             axis_as_bytes,
                                             shape:=len(axis_as_bytes),
                                             0,
                                             shape,
                                             adios2.ConstantDims)
        axis_writer.BeginStep()
        axis_writer.Put(sendbuffer, data)
        axis_writer.EndStep()
        axis_writer.Close()

        # Now get the data
        data_reader = self._io.Open(self._link, adios2.Mode.Read)
        
        data_in = self._io.InquireVariable(axis)
        receveived_data = np.zeros(data_in.Shape())

        while (status := data_reader.BeginStep()) == adios2.StepStatus.OK:
            if data_in:
                data_reader.Get(data_in, received_data, adios2.Mode.Sync)
                data_reader.EndStep()
            if status == adios2.StepStatus.EndOfStream:
                break

        data_reader.Close()

        return received_data

    def set_parameters(self,
                       **parameters)->None:
        """
        Set the parameters for the engine.

        Parameters
        ----------
        **parameters
            Key-value pair parameters to set for the engine.

        Returns
        -------
        None
        """
        self._io.SetParameters(parameters)


class ADIOSServer:
    """
    Send data through ADIOS.
    """
    _adios = None
    _io = None
    _parameters = None
    _link = None
    _axis = None
    _source = None
    _engine = None
    _axis_received = False

    def __init__(self,
                 link: str,
                 source: str,
                 engine="Dataman",
                 **parameters):
        """
        Parameters
        ----------
        link : str
            Name to connect to.
        source : str
            Data source - path to an HDF5 file.
        engine : str
            Engine to send data through. Default : Dataman.
        **parameters
            Parameters to pass to the engine for initialisation.
        """
        self._adios = adios2.ADIOS()
        self._io = adios.DeclareIO(self._link:=link)
        self._io.SetEngine(self._engine:=engine)
        if parameters:
            self.set_parameters(self._parameters:=parameters)

        self._source = source

    def _receive_axis(self)->None:
        """
        Receive a name of an axis to send.
        
        Returns
        -------
        None
        """
        axis_reader = self._io.Open("axis" + self._link, adios2.Mode.Read)
        axis = self._io.InquireVariable("axis")

        axis_reader.BeginStep()
        received_axis = np.zeros(axis.Shape())
        axis_reader.Get(axis, received_axis, adios2.Mode.Sync)
        axis_reader.EndStep()
        axis_reader.Close()

        self._axis = bytes(list(received_axis)).decode("utf-8")
        self._axis_received = True

    def _send_data(self,
                   steps: int =1
                   )->None:
        """
        Send requested data

        Parameters
        ----------
        steps : int
            Send the data in steps. Default : 1.

        Returns
        -------
        None

        Raises
        ------
        KeyError
            If axis is not found when indexed against the HDF5 source.
        """
        data_writer = self._io.Open(self._link, adios2.Mode.Write)
        
        with h5py.File(self._source, 'r') as h5file:
            data = h5file[axis]  # This can raise KeyError.
            # Would be better to pass the error to the ADIOSData
            # instance to raise.
            sendbuffer = self._io.DefineVariable(self._axis,
                                                 data,
                                                 shape:=data.shape,
                                                 0,
                                                 shape,
                                                 adios2.ConstantDims)

            data_writer.BeginStep()
            data_writer.Put(sendbuffer, h5file[axis])
            data_writer.EndStep()

        data_writer.Close()

        self._axis = None
        self._axis_received = False

    def chill(self)->None:
        """
        Chill out and wait for someone to ask for data.

        Returns
        -------
        None
        """
        while True:
            self._receive_axis()
            if self._axis_received:
                self._send_data()
