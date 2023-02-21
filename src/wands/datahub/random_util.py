"""
This module is used to generate data to test wands and to  show the usage of data hub. This is overengineered for numpy random data but should be seen as an 
example how datahub classes can be structured in general
"""
#from typing import Iterable
import dataclasses
import numpy as np

@dataclasses.dataclass
class RandomData:
    """
    Generate data
    """
    def __init__(self, shape):
        """
        Parameter: 
            shape: number of entries in each dimenstion
        Return:
            
        """
        self._data = np.random.rand(*shape)

        if not self._data.any():
            raise ValueError("No random array created")

    def __str__(self):
        return str(self._data)

    def __getitem__(self,index):
        return self._data[index]

    def shape(self):
        return self._data.shape

    