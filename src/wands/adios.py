"""
    Adios access api
"""
#for now numpy import 
#import numpy as np
#import warnings
import adios2



#IO object (only one per application) therefore a global variable within this module 
adios_io = None


class AdiosObject:
    """
    Create an Adios object
    _io
    _engine
    _parameters
    """
    def __init__(self, link:str,engine:str,parameters = None):
        # only call once
        global adios_io
        if adios_io is None:
            adios_io = adios2.ADIOS()
        self._link = link
        self._engine = engine
        try:
            self._io = adios_io.DeclareIO(self._link)
        except ValueError as ex:
            try:
                self._io = adios_io.AtIO(self._link)
            except:  
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
        #print(type(parameters))
        self._parameters = parameters
        self._io.SetParameters(parameters)
    
    def get_parameters(self):
        return self._parameters

    def get_adios(self):
        return adios_io
    
    def get_engine(self):
        return self._engine
    
    def get_IO(self):
        return self._io
    
    def get_link(self):
        return self._link
# #move those functions out of the class
#     def getIPAddress(self):
#         if self._parameters["IPAddress"] is not None:
#             return self._parameters["IPAddress"]
#         else:
#             raise ValueError(" IP Address not specified yet")

#     def getPort(self):
#         if self._parameters["Port"] is not None:
#             return self._parameters["Port"]
#         else:
#             raise ValueError(" Port not specified yet")

#     def getTimeout(self):
#         if self._parameters["Timeout"] is not None:
#             return self._parameters["Timeout"]
#         else:
#             raise ValueError(" Timeout parameter not specified yet")

#     def getTransportMode(self):
#         if self._parameters["TransportMode"] is not None:
#             return self._parameters["TransportMode"]
#         else:
#             raise ValueError(" Transportmode not specified yet")
        

