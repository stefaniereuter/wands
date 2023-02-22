"""
    Adios access api
"""
#for now numpy import 
import numpy as np
import adios2




#IO object (only one per application) therefore a global variable within this module 
adios_io = None

class AdiosWands:
    """
    Stream data via Adios Dataman
    """


    def __init__(self, link: str, engine="Dataman", parameters=None):
        """
        Declare IO set relevant parameters

        Parameters
        ----------
        link : str
            Name to connect to
        engine : str
            Engine to request data through. Default : Dataman
        **parameters
            Parameters to pass to the engine for initialisation.
            expects IPAddress, Port, Timeout parameter, TransportMode
        """
        # only call once
        global adios_io
        if adios_io is None:
            adios_io = adios2.ADIOS()
        self._link = link
        self._engine = engine
        try:
            self._io = adios_io.DeclareIO(self._link)
        except ValueError as ex:
            raise ValueError("IO declared twice") from ex
        self._io.SetEngine(self._engine)
        if parameters:
            self._parameters = parameters
            self.set_parameters(self._parameters)
        else:
            self._parameters = None

    def __str__(self):
        """
        Retruns
        String to describe IO Object
        """
        new_line = '\n'
        return f"Declared IO Name: {self._link} {new_line}Engine: {self._engine}{new_line}Set Parameters: {self._parameters}{new_line}"

    def set_parameters(self, parameters) -> None:
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
        #todo consider checking if parameters are usefull or test what happens
        # if for example Transportmode = fast is misspelled
        print(type(parameters))
        self._parameters = parameters
        self._io.SetParameters(parameters)

    def send(self, io_name:str, var_name:str, data, writer="data_writer"):
        writer = self._io.Open(io_name, adios2.Mode.Write )
        # name – unique variable identifier
        # shape – global dimension
        # start – local offset
        # count – local dimension
        # constantDims – true: shape, start, count won’t change, false: shape, start, count will change after definition
        shape = data.shape
        count = shape
        start = (0,) * len(shape)
        
        sendbuffer = self._io.DefineVariable(var_name, data, shape, start, count, adios2.ConstantDims )
        if sendbuffer:
            writer.BeginStep()
            writer.Put(sendbuffer, data)
            writer.EndStep()
        else:
            raise ValueError("Variable definition failed")
        
        writer.Close()

    def receive(self, io_name:str, variable_name:str, reader="data_reader"):
        reader = self._io.Open(io_name, adios2.Mode.Read)
        while True:
            stepStatus = reader.BeginStep()
            if stepStatus == adios2.StepStatus.OK:
                #inquire for variable
                recvar = self._io.InquireVariable(variable_name)
                if recvar:
                    # determine the shape of the data that will be sent
                    bufshape = recvar.Shape()
                    # allocate buffer for now numpy
                    data = np.zeros(bufshape)
                    reader.Get(recvar,data,adios2.Mode.Sync)
                    currentStep = reader.CurrentStep()
                    reader.EndStep()
                else:
                    raise ValueError("InquireVariable failed")
            elif stepStatus == adios2.StepStatus.EndOfStream:
                break
        reader.Close()
        return data

#move those functions out of the class
    def getIPAddress(self):
        if self._parameters["IPAddress"] is not None:
            return self._parameters["IPAddress"]
        else:
            raise ValueError(" IP Address not specified yet")

    def getPort(self):
        if self._parameters["Port"] is not None:
            return self._parameters["Port"]
        else:
            raise ValueError(" Port not specified yet")

    def getTimeout(self):
        if self._parameters["Timeout"] is not None:
            return self._parameters["Timeout"]
        else:
            raise ValueError(" Timeout parameter not specified yet")

    def getTransportMode(self):
        if self._parameters["TransportMode"] is not None:
            return self._parameters["TransportMode"]
        else:
            raise ValueError(" Transportmode not specified yet")


# class AdiosSend:
#     """
#     Send data through ADIOS.
#     """
#     #for now do it from AdiosWands object. Factory second step
#     def __init__(self, Variablename:str, IO_Object:AdiosWands)


#    # @classmethod
#    # def fromAdiosobj(AdiosWands)

#    #@classmethod
#    # def fromParameters(Parameters)
#     # first create Adiosobj