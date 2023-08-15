# for now numpy import
import numpy as np
import adios2
from .adios import AdiosObject
from .datahub import RawData_fusion
from .data_cache import DataCache

from logger import logger


# maybe add a counter for number of declared io. To finalize adiosobject in the sense if all declared Io are finalized adios_io can be reset to None. ToBeDiscussed
class WandsWAN:
    """
    Stream data via Adios Dataman
    """

    def __init__(self, link="WAN", engine="Dataman", parameters=None):
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
        # # only call once
        # global adios_io
        # if adios_io is None:
        #     adios_io = adios2.ADIOS()
        logger.info(parameters)
        self._adob = AdiosObject(link, engine, parameters)
        # add requests....

    def __str__(self):
        """
        Retruns
        String to describe IO Object
        """
        new_line = "\n"
        return f"{self._adob!s} "  # Declared IO Name: {self._link} {new_line}Engine: {self._engine}{new_line}Set Parameters: {self._parameters}{new_line}"

    def send(self, eng_name: str, var_name: str, data):
        """
        Send data via adios. Currently supported ndarray or RawData_fusion

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
        if isinstance(data, np.ndarray):
            self.send_array(eng_name, var_name, data)
        if isinstance(data, RawData_fusion):
            self.send_rawdata_fusion(eng_name, var_name, data)

    def send_array(self, eng_name: str, var_name: str, data: np.ndarray):
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
        writer = self._adob.get_IO().Open(eng_name, adios2.Mode.Write)
        # name – unique variable identifier
        # shape – global dimension
        # start – local offset
        # count – local dimension
        # constantDims – true: shape, start, count won’t change, false: shape, start, count will change after definition
        shape = data.shape
        logger.debug(f"shape in send: {shape!s}")
        count = shape
        logger.debug(f"count in send {count!s}")
        start = (0,) * len(shape)
        logger.debug(f"start in send {start!s}")

        sendbuffer = self._adob.get_IO().DefineVariable(
            var_name, data, shape, start, count, adios2.ConstantDims
        )
        # sendbuffer = self._io.DefineVariable(var_name, data, [], [], count, adios2.ConstantDims )

        if sendbuffer:
            writer.BeginStep()
            writer.Put(sendbuffer, data, adios2.Mode.Deferred)
            writer.EndStep()
        else:
            raise ValueError("Variable definition failed")

        writer.Close()

    def define_variables(self, data_dict: dict) -> dict:
        """
        Attach the variables to an IO object

        parameters:
        -----------
        data_dict: dictionary of names and data to be send

        returns:
        dict:
        Returns a dictionary containing the names and defined variables sendbuffer
        """
        defined_vars = {
            var_name: self._adob.get_IO().DefineVariable(
                var_name, data, [], [], data.shape, adios2.ConstantDims
            )
            for var_name, data in data_dict.items()
        }

        return defined_vars

    def send_dict_arrays(self, eng_name: str, data_dict: dict):
        """
        Send Array Data in one step
        Parameters
        ----------
        eng_name
            unique String to name the Writing Engine


        data dict . keys are names values are the arrays
            Data to be sent

        Returns
        -------
        None
        """
        # defined_vars = self.define_variables(data_dict)
        writer = self._adob.get_IO().Open(eng_name, adios2.Mode.Write)
        # name – unique variable identifier
        # shape – global dimension
        # start – local offset
        # count – local dimension
        # constantDims – true: shape, start, count won’t change, false: shape, start, count will change after definition

        writer.BeginStep()
        # for var_name ,sendbuf in defined_vars.items():
        for var_name, data in data_dict.items():
            shape = data.shape
            logger.debug(f"shape in send: {shape!s}")
            count = shape
            logger.debug(f"count in send {count!s}")
            start = (0,) * len(shape)
            logger.debug(f"start in send {start!s}")
            sendbuffer = self._adob.get_IO().DefineVariable(
                var_name, data, shape, start, count, adios2.ConstantDims
            )
            # writer.Put(sendbuf, data_dict[var_name], adios2.Mode.Deferred)
            writer.Put(sendbuffer, data, adios2.Mode.Deferred)
            # raise ValueError("Variable definition failed")

        writer.EndStep()
        writer.Close()

    def receive(self, request, engine_name="WAN"):
        """
        Send data via adios. Currently supported ndarray or RawData_fusion

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
        if isinstance(request, str):
            return self.receive_one_signal(engine_name, request)
        if isinstance(request, list):
            return self.receive_dict_arrays(engine_name, request)
        else:
            raise TypeError("only single strings or a list of strings can be requested")

    def receive_dict_arrays(self, eng_name: str, variable_list: list[str]) -> dict:
        """
        Receive Data

        Parameters
        ----------
        io_name
            unique String to name the Reading Engine

        var_list
            list of names that need to be received


        Returns
        -------
        data
        """
        logger.info(f"STATUS: receiving data from remote")
        data_dict = {}
        reader = self._adob.get_IO().Open(eng_name, adios2.Mode.Read)
        logger.info(f"Status: Handshake successfull")
        while True:
            stepStatus = reader.BeginStep()
            logger.debug(f"Stepstatus {stepStatus!s}")
            if stepStatus == adios2.StepStatus.OK:
                # inquire for variable
                for name in variable_list:
                    logger.debug(f"getting {name}")
                    recvar = self._adob.get_IO().InquireVariable(name)
                    logger.debug(f"Variable inqurired {recvar!s}")
                    if recvar:
                        # determine the shape of the data that will be sent
                        bufshape = recvar.Shape()
                        # allocate buffer for now numpy
                        # replace("_t","") necessary because
                        logger.debug(f"Received datatype {recvar.Type()}")
                        data = np.ones(bufshape, dtype=recvar.Type().replace("_t", ""))
                        logger.debug(f" in receive data {data!s}")
                        logger.debug(f"data before Get: \n{data!s}")
                        reader.Get(recvar, data, adios2.Mode.Deferred)
                        data_dict[name] = data
                        logger.debug(
                            f"data right after get This might be not right as data might not have been sent yet \n: {data!s}"
                        )
                        # currentStep = reader.CurrentStep()
                    else:
                        raise ValueError(f"InquireVariable failed {name!s}")
            elif stepStatus == adios2.StepStatus.EndOfStream:
                break
            else:
                raise StopIteration(f"next step failed to initiate {stepStatus!s}")
            reader.EndStep()
            logger.debug(f"After end step \n{data!s}")
        reader.Close()
        logger.debug(f"after close \n {data!s}")
        return data_dict

    def receive_list_save_only(
        self,
        eng_name: str,
        variable_list: list[str],
        path: str,
        filename: str,
        link="receive",
    ):
        """
        Receive Data

        Parameters
        ----------
        io_name
            unique String to name the Reading Engine

        var_list
            list of names that need to be received


        Returns
        -------

        """

        logger.info(
            f"STATUS: receiving data from remote not returned just saved in local data cache"
        )
        bpfilename = filename.replace(".h5", ".bp")  # TODO fix see issue #14
        bpfilename_path = f"{path}/{bpfilename}"

        reader = self._adob.get_IO().Open(eng_name, adios2.Mode.Read)

        dc_obj = DataCache(path=path, link=link)
        writer = dc_obj._adob.get_IO().Open(bpfilename_path, adios2.Mode.Append)

        logger.info(f"Status: Handshake successfull")
        while True:
            stepStatus = reader.BeginStep()
            logger.debug(f"Stepstatus {stepStatus!s}")
            if stepStatus == adios2.StepStatus.OK:
                # inquire for variable
                writer.BeginStep()
                for name in variable_list:
                    logger.debug(f"getting {name}")
                    recvar = self._adob.get_IO().InquireVariable(name)
                    logger.debug(f"Variable inqurired {recvar!s}")
                    if recvar:
                        # determine the shape of the data that will be sent
                        bufshape = recvar.Shape()
                        # allocate buffer for now numpy
                        # replace("_t","") necessary because
                        logger.debug(f"Datatype {recvar.Type()}")
                        data = np.ones(bufshape, dtype=recvar.Type().replace("_t", ""))
                        logger.debug(f" in receive data {data!s}")
                        logger.debug(f"data before Get: \n{data!s}")
                        reader.Get(recvar, data, adios2.Mode.Sync)
                        start = (0,) * len(bufshape)
                        if dc_obj._adob.get_IO().InquireVariable(name):
                            logger.info(f"Debug: variable {name} alrady in file")
                            continue
                        writebuffer = dc_obj._adob.get_IO().DefineVariable(
                            name, data, bufshape, start, bufshape, adios2.ConstantDims
                        )
                        writer.Put(writebuffer, data, adios2.Mode.Deferred)
                        logger.debug(
                            f"data right after get This might be not right as data might not have been sent yet \n: {data!s}"
                        )
                        # currentStep = reader.CurrentStep()
                    else:
                        raise ValueError(f"InquireVariable failed {name!s}")
            elif stepStatus == adios2.StepStatus.EndOfStream:
                break
            else:
                raise StopIteration(f"next step failed to initiate {stepStatus!s}")
            writer.EndStep()
            reader.EndStep()
            logger.debug(f"After end step \n{data!s}")
        writer.Close()
        reader.Close()
        logger.debug(f"after close \n {data!s}")

    # def receive_dict_arrays_multi_steps(self, eng_name:str, variable_list:list[str]):
    #     """
    #     Receive Data

    #     Parameters
    #     ----------
    #     io_name
    #         unique String to name the Reading Engine

    #     var_list
    #         list of names that need to be received

    #     Returns
    #     -------
    #     data
    #     """
    #     data_dict={}
    #     reader = self._adob.get_IO().Open(eng_name, adios2.Mode.Read)
    #     #while True:
    #     #inquire for variable
    #     for name in variable_list:

    #         stepStatus = reader.BeginStep()

    #         if stepStatus == adios2.StepStatus.OK:
    #             recvar = self._adob.get_IO().InquireVariable(name)
    #             if recvar:
    #                 print(f"name: {name}")
    #                 # determine the shape of the data that will be sent
    #                 bufshape = recvar.Shape()
    #                 # allocate buffer for now numpy
    #                 # #replace("_t","") necessary because
    #                 data = np.ones(bufshape,dtype=recvar.Type().replace("_t",""))
    #                 # print(f"data before Get: \n{data!s}")
    #                 reader.Get(recvar,data,adios2.Mode.Deferred)
    #                 data_dict[name] = data

    #             #print(f"data right after get This might be not right as data might not have been sent yet \n: {data!s}")
    #             #currentStep = reader.CurrentStep()
    #             else:
    #                 raise ValueError(f"InquireVariable failed {name!s}")
    #         elif stepStatus == adios2.StepStatus.EndOfStream:
    #             break
    #         else:
    #             raise StopIteration(f"next step failed to initiate {stepStatus!s}")
    #         #print(f"After end step \n{data!s}")
    #     reader.Close()
    #     #print(f"after close \n {data!s}")
    #     return data_dict

    def send_rawdata_fusion(self, eng_name: str, var_name: str, data: RawData_fusion):
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
        # send time if not None
        time = data.get_time()
        if time is not None:
            sendmatrix.append(time)
        else:
            logger.warn(
                f"could not retrieve time array for {var_name!s}, will not be sent"
            )

        # send data if not None
        data_array = data.get_data()
        if data is not None:
            sendmatrix.append(data_array)
        else:
            logger.warn(
                f"could not retrieve data array for {var_name!s}, will not be sent"
            )

        # send error if not None (see if it's possible to also check if all entries are zero and avoid sending the data)
        error = data.get_errors()
        if error is not None:
            sendmatrix.append(error)
        else:
            logger.warn(
                f"could not retrieve error array for {var_name!s}, will not be sent"
            )

        self.send_array(eng_name, var_name, np.array(sendmatrix))

    def send_rawdata_fusion_list(self, eng_name: str, rd_list: list[RawData_fusion]):
        """
        Send Array Data in one step
        Parameters
        ----------
        eng_name
            unique String to name the Writing Engine


        rd_list list of raw data

        Returns
        -------
        None
        """
        # defined_vars = self.define_variables(data_dict)
        logger.info(f"sending raw list")
        logger.debug(rd_list)
        writer = self._adob.get_IO().Open(eng_name, adios2.Mode.Write)
        # name – unique variable identifier
        # shape – global dimension
        # start – local offset
        # count – local dimension
        # constantDims – true: shape, start, count won’t change, false: shape, start, count will change after definition
        logger.debug(f"opened ")

        writer.BeginStep()
        # for var_name ,sendbuf in defined_vars.items():
        for rd in rd_list:
            logger.debug(rd)
            name = rd.get_name()
            logger.debug(f"Signal: {name}")
            sendmatrix = []
            # send time if not None
            time = rd.get_time()
            if time is not None:
                sendmatrix.append(time)
            else:
                logger.warn(
                    f"could not retrieve time array for {name!s}, will not be sent"
                )

            # send data if not None
            data = rd.get_data()
            if data is not None:
                sendmatrix.append(data)
            else:
                logger.warn(
                    f"could not retrieve data array for {name!s}, will not be sent"
                )

            # self.send_array(eng_name,name,np.array(sendmatrix))
            nd_matrix = np.array(sendmatrix)
            logger.debug(f"type matrix {type(nd_matrix)!s}")
            shape = nd_matrix.shape
            logger.debug(f"shape in send: {shape!s}")
            count = shape
            logger.debug(f"count in send {count!s}")
            start = (0,) * len(shape)
            logger.debug(f"start in send {start!s}")
            sendbuffer = self._adob.get_IO().DefineVariable(
                name, nd_matrix, shape, start, count, adios2.ConstantDims
            )
            # writer.Put(sendbuf, data_dict[var_name], adios2.Mode.Deferred)
            writer.Put(sendbuffer, data, adios2.Mode.Deferred)
            # raise ValueError("Variable definition failed")

        writer.EndStep()
        writer.Close()

    def receive_one_signal(self, eng_name: str, variable_name: str):
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
        reader = self._adob.get_IO().Open(eng_name, adios2.Mode.Read)
        while True:
            stepStatus = reader.BeginStep()
            if stepStatus == adios2.StepStatus.OK:
                # inquire for variable
                recvar = self._adob.get_IO().InquireVariable(variable_name)
                if recvar:
                    # determine the shape of the data that will be sent
                    bufshape = recvar.Shape()
                    # allocate buffer for now numpy Type() returns a cpp type e.g. int64_t
                    # replace("_t","") necessary because
                    data = np.ones(bufshape, dtype=recvar.Type().replace("_t", ""))
                    logger.debug(f"data before Get: \n{data!s}")
                    reader.Get(recvar, data, adios2.Mode.Deferred)
                    logger.debug(
                        f"data right after get This might be not right as data might not have been sent yet \n: {data!s}"
                    )
                    # currentStep = reader.CurrentStep()
                else:
                    raise ValueError(f"InquireVariable failed {variable_name!s}")
            elif stepStatus == adios2.StepStatus.EndOfStream:
                break
            else:
                raise StopIteration(f"next step failed to initiate {stepStatus!s}")
            reader.EndStep()
            logger.debug(f"After end step \n{data!s}")
        reader.Close()
        logger.debug(f"after close \n {data!s}")
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
