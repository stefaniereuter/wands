"""
    Adios access api
"""

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

        self._io = adios_io.DeclareIO(self._link)
        self._io.SetEngine(self._engine)
        if parameters:
            self._parameters = parameters
            self.set_parameters(self._parameters)
        else:
            self._parameters = None

    def __str__(self):
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
        print(type(parameters))
        self._parameters = parameters
        self._io.SetParameters(parameters)