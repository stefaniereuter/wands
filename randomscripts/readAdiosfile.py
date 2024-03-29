# modified the example found on https://adios2.readthedocs.io/en/latest/api_high/api_high.html#python-high-level-api
import numpy as np
import adios2


with adios2.open("Matrix.bp", "r") as fh:
    for fstep in fh:
        # inspect variables in current step
        step_vars = fstep.available_variables()

        # print variables information
        for name, info in step_vars.items():
            print("variable_name: " + name)
            for key, value in info.items():
                print("\t" + key + ": " + value)
            print("\n")

        # track current step
        step = fstep.current_step()
        if step == 0:
            size_in = fstep.read("size")

    # read variables return a numpy array with corresponding selection
    data = fstep.read("bpMatrixglobal")

print(data)
