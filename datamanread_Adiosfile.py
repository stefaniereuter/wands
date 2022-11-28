#modified the example found on https://adios2.readthedocs.io/en/latest/api_high/api_high.html#python-high-level-api 
import numpy as np
import adios2

Nx = 2
Ny = 2
adios = adios2.ADIOS()

datamanIO = adios.DeclareIO("Fluesterpost")
datamanIO.SetEngine("Dataman")

datamanIO.SetParameters({"IPAddress":"127.0.0.1" , "Port":"12306", "Timeout":"5", "TransportMode":"reliable" })

datamanReader = datamanIO.Open("Fluesterpost_matrix",adios2.Mode.Read)
#preallocate data variable 
receivedMatrix = np.zeros(Nx*Ny, int)
while True:
    stepStatus = datamanReader.BeginStep()
    if stepStatus == adios2.StepStatus.OK:
        data = datamanIO.InquireVariable("matrix")
        #todo inquire size via metadata
        datamanReader.Get(data,receivedMatrix, adios2.Mode.Sync)
        currentStep =datamanReader.CurrentStep()
        datamanReader.EndStep()
        print("Step", currentStep, receivedMatrix)
    elif stepStatus == adios2.StepStatus.EndOfStream:
        print("Done")
        break
datamanReader.Close()

print(receivedMatrix)


# with adios2.open("Matrix.bp", "r") as fh:

#     for fstep in fh:

#         # inspect variables in current step
#         step_vars = fstep.available_variables()

#         # print variables information
#         for name, info in step_vars.items():
#             print("variable_name: " + name)
#             for key, value in info.items():
#                 print("\t" + key + ": " + value)
#             print("\n")

#         # track current step
#         step = fstep.current_step()
#         if( step == 0 ):
#             size_in = fstep.read("size")

#     # read variables return a numpy array with corresponding selection
#     data = fstep.read("bpMatrixglobal")

# print(data)