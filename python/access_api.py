import numpy as np
import adios2

class AdiosData:
    """
    Access in-memory data from ADIOS DataSpaces.

    databases_server must be running.
    """
    _adios = None
    _parameters = None
    _dataman_io = None
    def __init__(self, link: str, variable: str, **parameters):
        self._adios = adios2.ADIOS()
        self._dataman_io = adios.DeclareIO(self.link:=link)
        self._dataman_io.SetEngine("Dataman")
        self.set_parameters(parameters)

    def __getitem__(self, axis: str):
        """
        """
        # Send name of axis across
        axis_writer = self._dataman_io.Open("axis", adios2.Mode.Write)

        axis_as_bytes = bytearray(axis, "utf-8")
        
        sendbuffer = self._dataman_io.DefineVariable(axis,
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
        data_reader = self._dataman_io.Open(self.link, adois2.Mode.Read)
        
        data_in = self._dataman_io.InquireVariable(axis)
        receveived_data = np.zeros(data_in.Shape())

        while (status := data_reader.BeginStep()) == adios2.StepStatus.OK:
            if data_in:
                data_reader.Get(data_in, received_data, adios2.Mode.Sync)
                data_reader.EndStep()
            if status == adios2.StepStatus.EndOfStream:
                break

        return received_data

    def set_parameters(self, **parameters):
        dataman_io.SetParameters(self._parameters:=parameters)

    def _to_dataspaces(self, axis):
        pass

    def _from_dataspaces(self, axis):
        pass


class AdiosServer:
    def __init__(self):        
