import pytest

from wands import RandomData

def test_randomdata_simple():
    obj = RandomData([2,3])
    assert obj._data is not None
    assert obj._data.shape==(2,3)
    assert isinstance(str(obj), str)
    assert obj[1,2].size ==1
    assert obj[1,:].size ==3

