import numpy as np
import adios2

# import socket

Nx = 4
Ny = 4
adios = adios2.ADIOS()

datamanIO = adios.DeclareIO("Fluesterpost")
# specify engine Dataman receive Data from dataman server program BP5 read data that was previously written.
datamanIO.SetEngine("Dataman")
# datamanIO.SetEngine("BP5")

# specify parameters for dataman connection
# specify the IP of the host that is receiving the data. Either specified prior or uncomment import socket and inquire IP via gethostbyaddr.
# datamanIO.SetParameters({"IPAddress":"10.43.78.89" , "Port":"12306", "Timeout":"5", "TransportMode":"reliable" })
# IP 127.0.0.1 if on same host as server code
datamanIO.SetParameters(
    {
        "IPAddress": "127.0.0.1",
        "Port": "12306",
        "Timeout": "5",
        "TransportMode": "reliable",
    }
)
# datamanIO.SetParameters({"IPAddress":socket.gethostbyaddr("cpu-q-526.data.cluster")[2][0]  , "Port":"12306", "Timeout":"5", "TransportMode":"reliable" })


# datamanRec = datamanIO.Open("Fluesterpost_matrix1",adios2.Mode.Read)
# print("waiting to receive fist matrix")
# data1 = datamanIO.InquireVariable("matrix1")
# if data1:
#     # rec_type = data_matrix1.Type()
#     # print(rec_type)
#     # rec_size = data_matrix1.SelectionSize()
#     # print(rec_size)
#     receivebuffer1 = np.zeros(Nx*Ny)
#     datamanRec.Get(data1, receivebuffer1, adios2.Mode.Sync)
#     datamanRec.Close()
# else:
#     print("Nullpointer data1")


# Send all data in one step: Size is known beforehand

# preallocate data variable is possible here if size is constant over every step and if size is known
receivedMatrix = np.zeros(Nx * Ny)
# InquireVariable needs to happen within the step environment as it will return a nullpointer otherwise.
# todo: the return of nullpointer outside of a step environment might be a bug and needs to be investigated.

datamanReader = datamanIO.Open("Fluesterpost", adios2.Mode.Read)
while True:
    stepStatus = datamanReader.BeginStep()
    if stepStatus == adios2.StepStatus.OK:
        data1 = datamanIO.InquireVariable("amc")
        if data1:
            datamanReader.Get(data1, receivedMatrix, adios2.Mode.Sync)
            currentStep = datamanReader.CurrentStep()
            datamanReader.EndStep()
            print("Step", currentStep, receivedMatrix)
        else:
            print("Nullpointer check failed for matrix1")
    elif stepStatus == adios2.StepStatus.EndOfStream:
        print("Done Dataset 1")
        break
datamanReader.Close()

print("------------------")
print(receivedMatrix)
print("maximum entry: ", receivedMatrix.max())
print("data mean: ", receivedMatrix.mean())
print("minimum entry: ", receivedMatrix.min())


# Data is sent in multiple steps. Each step has a different matrix size Currently only the last step will be saved in received matrix.
datamanReader = datamanIO.Open("Fluesterpost_matrix", adios2.Mode.Read)
while True:
    stepStatus = datamanReader.BeginStep()
    if stepStatus == adios2.StepStatus.OK:
        # inquire for matrix 2
        data2 = datamanIO.InquireVariable("matrix2")
        if data2:
            # determin the shape of the data that will be sent
            buffersize = data2.Shape()
            # allocate the buffer
            receivedMatrix2 = np.zeros(buffersize)
            # print(np.prod(buffersize))
            # todo inquire size via metadata
            datamanReader.Get(data2, receivedMatrix2, adios2.Mode.Sync)
            currentStep = datamanReader.CurrentStep()
            datamanReader.EndStep()
        else:
            print("Nullpointer check failed for matrix2")

        print("Step", currentStep, receivedMatrix2)
    elif stepStatus == adios2.StepStatus.EndOfStream:
        print("Done Dataset 2")
        break
datamanReader.Close()
