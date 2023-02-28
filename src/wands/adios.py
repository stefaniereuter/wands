"""
    Adios access api
"""
#for now numpy import 
import numpy as np
import warnings
import adios2
from .datahub.hdf_util import RawData, get_req_data





#IO object (only one per application) therefore a global variable within this module 
adios_io = None
#maybe add a counter for number of declared io. To finalize adiosobject in the sense if all declared Io are finalized adios_io can be reset to None. ToBeDiscussed
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
        #print(type(parameters))
        self._parameters = parameters
        self._io.SetParameters(parameters)

    def send(self, eng_name:str, var_name:str, data):
        """
        Send data via adios. Currently supported ndarray or RawData

        Parameters
        -----------
        eng_name
            unique String to name the Writing Engine

        var_name
            unique name for the variable to be send. This will be queried by the receiver

        data
            Data to be sent

        Returns
        -------
        None

        """
        if isinstance(data,np.ndarray):
            self.send_array(eng_name,var_name,data)
        if isinstance(data,RawData):
            self.send_rawdata(eng_name,var_name,data)


    def send_array(self, eng_name:str, var_name:str, data:np.ndarray):
        """
        Send Array Data in one step

        Parameters
        ----------
        eng_name
            unique String to name the Writing Engine

        var_name
            unique name for the variable to be send. This will be queried by the receiver

        data
            Data to be sent

        Returns
        -------
        None
        """
        writer = self._io.Open(eng_name, adios2.Mode.Write )
        # name – unique variable identifier
        # shape – global dimension
        # start – local offset
        # count – local dimension
        # constantDims – true: shape, start, count won’t change, false: shape, start, count will change after definition
        shape = data.shape
        print(f"shape in send: {shape!s}")
        count = shape
        print(f"count in send {count!s}")
        start = (0,) * len(shape)
        print(f"start in send {start!s}")
        
        sendbuffer = self._io.DefineVariable(var_name, data, shape, start, count, adios2.ConstantDims )
        if sendbuffer:
            writer.BeginStep()
            writer.Put(sendbuffer, data, adios2.Mode.Deferred)
            writer.EndStep()
        else:
            raise ValueError("Variable definition failed")
        
        writer.Close()


    def send_rawdata(self, eng_name:str, var_name:str, data:RawData):
        """
        Send Array Data in one step

        Parameters
        ----------
        eng_name
            unique String to name the Writing Engine

        var_name
            unique name for the variable to be send. This will be queried by the receiver

        data
            Data to be sent

        Returns
        -------
        None
        """

        # At the moment there seems to be a potentioal bug if trying to send one dimensional arrays. 
        # See https://github.com/ornladios/ADIOS2/issues/3503 
        # For that reason we add time, data, errors to one big array and send in one. 
        # It would be great to send three individual arrays in one step it should give a performance benefit.
        sendmatrix = []
        #send time if not None
        time = data.get_time()
        if time is not None:
            sendmatrix.append(time)
        else: 
            warnings.warn(f"could not retrieve time array for {var_name!s}, will not be sent")

        
        #send data if not None
        data_array = data.get_data()
        if data is not None:
            sendmatrix.append(data_array)
        else:
            warnings.warn(f"could not retrieve data array for {var_name!s}, will not be sent")

        #send error if not None (see if it's possible to also check if all entries are zero and avoid sending the data)
        error = data.get_errors()
        if error is not None:
            sendmatrix.append(error)
        else:
            warnings.warn(f"could not retrieve error array for {var_name!s}, will not be sent")

        #self.send_array(eng_name,var_name,np.array(sendmatrix))
        sendmatrix = np.array(sendmatrix)
        ## copy send routine in here to test attributes
        writer = self._io.Open(eng_name, adios2.Mode.Write )
        # name – unique variable identifier
        # shape – global dimension
        # start – local offset
        # count – local dimension
        # constantDims – true: shape, start, count won’t change, false: shape, start, count will change after definition
        shape = sendmatrix.shape
        print(f"shape in send: {shape!s}")
        count = shape
        print(f"count in send {count!s}")
        start = (0,) * len(shape)
        print(f"start in send {start!s}")


        #DefineAttribute(self: adios2.IO, name: str, array: array, variable_name: str=’’, separator: str=’/’) -> adios2::py11::Attribute
        #DefineAttribute(self: adios2.IO, name: str, stringValue: str, variable_name: str=’’, separator: str=’/’) -> adios2::py11::Attribute
        #DefineAttribute(self: adios2.IO, name: str, strings: List[str], variable_name: str=’’, separator: str=’/’) -> adios2::py11::Attribute

        sendbuffer = self._io.DefineVariable(var_name, sendmatrix, shape, start, count, adios2.ConstantDims )
        self._io.DefineAttribute(name='name',stringValue=data.get_name(),variable_name=var_name)
        for k, v in data.get_group_attr().items():
            self._io.DefineAttribute(name = k,stringValue = str(v),variable_name = var_name)
        if sendbuffer:
            writer.BeginStep()
            writer.Put(sendbuffer, sendmatrix, adios2.Mode.Deferred)
            writer.EndStep()
        else:
            raise ValueError("Variable definition failed")
        
        writer.Close()
    def send_steps(self, eng_name:str, var_name:str, data, chunks):
        """
        Send Data in multiple steps

        Parameters
        ----------
        io_name
            unique String to name the Writing Engine

        var_name
            unique name for the variable to be send. This will be queried by the receiver

        data
            Data to be sent

        chunks
            number of elements per chunk to be send: at the moment it needs the explicit form of a tuple to account for all elements 
            for example ((2,2,1),(2,2,2)) for a matrix in the shape of shape = (5,6) -> (2,2,1) is for the first dimension (5 elements) and (2,2,2) accounts for the second dimension (6 elements) 
            therefore the data will be send in blocks of 6 blocks of (2x2) elements and 3 blocks of (1x2) elements  
            At the moment the user is responsible for making sure that all data is accounted for in these chunks (This will be changed later on)

        Returns
        -------
        None
        """
        
        # Sort chunks:
        # ATM it  needs the correct form but should be handles similar to normalize_chunks in dask.array.core
        raise KeyError(f"sending in steps not yet implemented")
    

        writer = self._io.Open(eng_name, adios2.Mode.Write )
        # name – unique variable identifier
        # shape – global dimension
        # start – local offset
        # count – local dimension
        # constantDims – true: shape, start, count won’t change, false: shape, start, count will change after definition
        shape = data.shape
        print(f"shape in send: {shape!s}")
        count = shape
        print(f"count in send {count!s}")
        start = (0,) * len(shape)
        print(f"start in send {start!s}")
        
        sendbuffer = self._io.DefineVariable(var_name, data, shape, start, count, adios2.ConstantDims )
        if sendbuffer:
            writer.BeginStep()
            writer.Put(sendbuffer, data, adios2.Mode.Deferred)
            writer.EndStep()
        else:
            raise ValueError("Variable definition failed")
        
        writer.Close()

    def receive(self, eng_name:str, variable_name:str):
        import logging
        """
        Receive Data

        Parameters
        ----------
        io_name
            unique String to name the Reading Engine

        var_name
            unique name for the variable to be received.


        Returns
        -------
        data
        """
        #logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
        #logging.info(f"in receive")
        #print("just got into receive")
        reader = self._io.Open(eng_name, adios2.Mode.Read)
        #print(f"after open")
        #logging.info(f"opened")

        #logging.info("Attribute")
        #logging.info(self._io.InquireAttribute(variable_name+'/name').Data())
        # ### Old version
        # while True:
        #     stepStatus = reader.BeginStep()
        #     print(f"required stepStatus: {stepStatus}")
        #     logging.info(f"required stepstatus")
        #     if stepStatus == adios2.StepStatus.OK:
        #         #inquire for variable
        #         print(f"Inquire Variable {variable_name!s}")
        #         logging.info(f"inquire var")
        #         recvar = self._io.InquireVariable(variable_name)
        #         print(f"successfull")
        #         print(f"successfull")
        #         if recvar:
        #             # determine the shape of the data that will be sent
        #             bufshape = recvar.Shape()
        #             # allocate buffer for now numpy
        #             data = np.ones(bufshape)
        #             #print(f"data before Get: \n{data!s}")
        #             print(f" before get0")
        #             reader.Get(recvar,data,adios2.Mode.Deferred)
        #             print(f" after get")
        #             #print(f"data right after get This might be not right as data might not have been sent yet \n: {data!s}")
        #             #currentStep = reader.CurrentStep()
        #         else:
        #             raise ValueError(f"InquireVariable failed {variable_name!s}")
        #     elif stepStatus == adios2.StepStatus.EndOfStream:
        #         break
        #     else: 
        #         raise StopIteration(f"next step failed to initiate {stepStatus!s}")
        #     reader.EndStep()
        #     #print(f"After end step \n{data!s}")
        ### new version TODO consider removing the while loop but it needs to be tested
        stepStatus = reader.BeginStep()
        if stepStatus == adios2.StepStatus.OK:
            #inquire for variable
            recvar = self._io.InquireVariable(variable_name)
            if recvar:
                # determine the shape of the data that will be sent
                bufshape = recvar.Shape()
                # allocate buffer for now numpy
                data = np.ones(bufshape)
                #print(f"data before Get: \n{data!s}")
                reader.Get(recvar,data,adios2.Mode.Deferred)
                #print(f"data right after get This might be not right as data might not have been sent yet \n: {data!s}")
                #currentStep = reader.CurrentStep()
            else:
                raise ValueError(f"InquireVariable failed {variable_name!s}")
        
        reader.EndStep()
    
        reader.Close()
        #print(f"after close \n {data!s}")
        return data
        # reader = self._io.Open(eng_name, adios2.Mode.Read)
        # recvar = self._io.InquireVariable(variable_name)
        # step_status = reader.BeginStep()
        # if step_status == adios2.StepStatus.OK:
        #     if recvar:
        #         data = np.zeros(recvar.Shape())
        #         reader.Get(recvar,data,adios2.Mode.Deferred)
        #     else:
        #         raise ValueError(f"InquireVariable failed {variable_name!s}")
        # else: 
        #     raise StopIteration(f" next step failed")
        # reader.EndStep()
        # reader.Close()
        # return data
    def send_requested_data(self, request_list, eng_name = 'srd', filename=None):
        """
        Request a number of datasets that need to be sent
        Parameters
        ---------
        var_names: a list of names or a string of a name that needs to be retrieved from an HDF5 file. 
        
        eng_name: a unique name for engine

        filename: the name of the path and name to the HDF5 file optional as can also be specified from the requesting process
        """
        # if isinstance(var_names,str):
        #     var_names = [var_names]
        
        raw_data_list = get_req_data(filename,request_list)

        for k in raw_data_list:
            print(f"this will be send now: {k}")
            self.send(eng_name,k.get_name(),k)
            
    #is it more convenient to have a dictionary as a return type ?
    #TODO cannot send string array needs to be fixed
    def request_remote_data(self,req_data, data_source = None, eng_name='rrd', var_name='var_names')-> list[RawData]:
        """
        Request data from remote source
        Parameters
        -----------
        req_data:
            the list of variable names where a group is requested
        
        filename: at the moment this is needed because all data will come from a HDF5 file

        eng_name: optional specify a unique name for the engine

        var_name: optional specify a unique name for the data (the same name needs to be queried at the remote site)
        """
        
        # if data_source specifies a hdf5 file add it as a variable in the list
        # TODO consider sending it as attribute
        if '.h5' in data_source: 
            req_data = [data_source, req_data]
        
        # send
        print(f" Request the following data: {req_data}")
        print(type(req_data))
        req_data = np.ascontiguousarray(req_data)
        self.send(eng_name,var_name,req_data)
        print(f"Request sent waiting for data")
        req_data.remove(data_source)

        rd_list = []
        # this needs to be unstructured. Ideally the data can be sent in any order and received in any order. Rewrite send-array and receive array. 
        # Can this cause data congestion?
        for k in req_data:
            data = self.receive(eng_name,k)
            RawData_temp = RawData(k)
            rd_list.append(RawData_temp.convert_to_rawdata(data))

        return rd_list
    
    def receive_multiple_datasets(self,eng_name = "rdo",req_data=None) -> list[RawData]:
        """
        Request data from remote source
        Parameters
        -----------
        eng_name: optional specify a unique name for the engine

        var_name: optional specify a unique name for the data (the same name needs to be queried at the remote site)

        req_data: the same array that is requested on the data site
        """
        rd_list = []
        # this needs to be unstructured. Ideally the data can be sent in any order and received in any order. Rewrite send-array and receive array. 
        # Can this cause data congestion?
        for k in req_data:
            data = self.receive(eng_name,k)
            print(f"this data was received {data}")
            RawData_temp = RawData(k)
            rd_list.append(RawData_temp.convert_to_rawdata(data))

        return rd_list
    
    #TODO cannot send string array needs to be fixed
    def request_handler(self, var_names='var_names',eng_name='rrd', filename = None):
        """
        Request data from remote source
        Parameters
        -----------

        eng_name: optional specify a unique name for the engine 
            required if individual name specified on requester site

        var_name: optional specify a unique name for the data (the same name needs to be queried at the remote site)
            required if individual name specified on requester site
        
        filename: the filename can bei either sent or specified here. If a filename is sent this will be used
        """    
        try:
            print(f"waiting to get data")
            request_list = self.receive(eng_name, var_names)
        except: #TODO add correct exceptions here
            raise ValueError(f"receiving data failed in request_handler")
        
        print("Received the request: {request_list!s}")
        print("looking for the data now to send")
        filename_req = None
        if '.h5' in request_list[0]:
            filename_req = request_list[0]
            request_list.remove(filename_req)
        if filename_req is None:
            if filename is None:
                raise ValueError(f"A filename is missing: Either specify it directly to request_handler or in request_remote_data")
            else:
                self.send_requested_data( request_list,eng_name=eng_name,var_name=var_names ,filename = filename )
        else:
            self.send_requested_data( request_list,eng_name=eng_name,var_name=var_names ,filename = filename_req)

    def request_data_onsite(self,filename:str, req_list:list, var_name='var_name', eng_name='rdo'):
        """
        Initiate from data site: to avoid sending the initial request array
        Parameters
        -----------
        req_list: list with required datasets
        eng_name: optional specify a unique name for the engine 
            required if individual name specified on requester site

        var_name: optional specify a unique name for the data (the same name needs to be queried at the remote site)
            required if individual name specified on requester site
        
        filename: the filename can bei either sent or specified here. If a filename is sent this will be used
        """
        try:
            self.send_requested_data(request_list=req_list, eng_name=eng_name, filename=filename)
        except:
            raise ValueError("Could not send requested data")


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