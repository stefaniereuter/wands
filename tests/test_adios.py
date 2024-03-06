"""
Tests to test the adios access api of wands
"""
import pytest
import numpy as np
import adios2
from wands import AdiosObject


def test_init():
    params = {
        "IPAddress": "0.0.0.0",
        "Port": "12306",
        "Timeout": "5",
        "TransportMode": "reliable",
    }
    obj = AdiosObject(link="testIO1", engine="Dataman", parameters=params)
    assert obj is not None
    assert obj.get_engine() == "Dataman"
    assert obj.get_link() == "testIO1"
    assert obj.get_IO() is not None
    assert obj.get_parameters() is params
    assert type(obj.get_adios()) is adios2.adios2.ADIOS
    # assert obj.getPort() == "12306"
    # assert obj.getTimeout() == "5"
    # assert obj.getTransportMode() == "reliable"
    params = {
        "IPAddress": "0.1.2.3",
        "Port": " 12345",
        "Timeout": "4",
        "TransportMode": "reliable",
        "RendezvousReaderCount": "1",
    }
    obj = AdiosObject(link="testIO1", engine="Dataman", parameters=params)
    assert obj.get_parameters() is params


def test_init_seperateParameters():
    params = {
        "IPAddress": "0.0.0.3",
        "Port": "12345",
        "Timeout": "6",
        "TransportMode": "fast",
    }
    obj2 = AdiosObject(link="testIO2", engine="Dataman")
    obj2.set_parameters(params)
    assert obj2 is not None
    assert obj2.get_engine() == "Dataman"
    assert obj2.get_link() == "testIO2"
    assert obj2.get_IO() is not None
    assert obj2.get_parameters() is params
    # assert obj2.getIPAddress() == "0.0.0.3"
    # assert obj2.getPort() == "12345"
    # assert obj2.getTimeout() == "6"
    # assert obj2.getTransportMode() == "fast"
