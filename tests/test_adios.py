"""
Tests to test the adios access api of wands
"""
import pytest

from wands import AdiosWands

def test_init():
    params = {
        "IPAddress": "0.0.0.0",
        "Port": "12306",
        "Timeout": "5",
        "TransportMode": "reliable",
    }
    obj = AdiosWands(link = "testIO1", engine="Dataman",parameters=params)
    assert obj is not None
    assert obj._engine is "Dataman"
    assert obj._link is "testIO1"
    assert obj._io is not None
    assert obj.getIPAddress() == "0.0.0.0"
    assert obj.getPort() == "12306"
    assert obj.getTimeout() == "5"
    assert obj.getTransportMode() == "reliable"
    with pytest.raises(ValueError):
        obj = AdiosWands(link = "testIO1", engine="Dataman",parameters=params)
    
def test_init_seperateParameters():
    params = {
        "IPAddress": "0.0.0.3",
        "Port": "12345",
        "Timeout": "6",
        "TransportMode": "fast",
    }
    obj2 = AdiosWands(link = "testIO2")
    obj2.set_parameters(params)
    assert obj2 is not None
    assert obj2._engine is "Dataman"
    assert obj2._link is "testIO2"
    assert obj2._io is not None
    assert obj2.getIPAddress() == "0.0.0.3"
    assert obj2.getPort() == "12345"
    assert obj2.getTimeout() == "6"
    assert obj2.getTransportMode() == "fast"

# @pytest.fixture(autouse=True)
# def resetglobalIOperTest():
#     from wands.adios import adios_io
#     adios_io = None