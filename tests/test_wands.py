import concurrent
import os
import shutil
from tempfile import TemporaryDirectory
from pathlib import Path
import subprocess as sub
import signal
import asyncio
import numpy as np
from wands import Wands
import pytest
import pytest_asyncio


def test_init():
    current_dir = os.getcwd()
    cache_dir = current_dir + "/tests/test_cache"
    wo = Wands(cache_dir, Port="12345")
    assert wo is not None
    assert wo.cache_location() == cache_dir


@pytest.fixture(name="server_srcdir")
def fixture_server_srcdir():
    return Path(__file__).parent.parent / "server"


@pytest.fixture(name="server_builddir")
def fixture_server_builddir():
    with TemporaryDirectory(prefix="wands_server") as directory:
        yield Path(directory)

@pytest.fixture(name="cache_dir")
def fixture_cache_dir():
    return Path(__file__).parent / "test_cache"

@pytest_asyncio.fixture(name="server")
async def fixture_server(server_srcdir, server_builddir):
    Path("stdio").write_text("Before configure")
    # Configure
    sub.run(["cmake", str(server_srcdir)], cwd=str(server_builddir)).check_returncode()
    # Build
    sub.run(["cmake", "--build", "."], cwd=str(server_builddir)).check_returncode()
    # Launch server
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.subprocess_exec(
        asyncio.SubprocessProtocol,
        str(server_builddir / "wands_server"),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    yield transport.get_pid()
    transport.send_signal(signal.SIGINT)
    print('signal sent')
    transport.close()
    print('transport closed')


def send_request(cache_dir,testdatasource):
    #testsource = "test_data.h5"
    signals = ["FP/float",
               "FP/double"]
    
# TODO "testdataint/int", should be added once integers are supported
    wo = Wands(cache_dir,Port="12345")
    data_dict = wo.request(testdatasource,signals)
    return data_dict



@pytest.mark.asyncio
@pytest.mark.xfail
async def test_request(server, cache_dir):
   # breakpoint()
    testdatasource = "test_data.h5"
    loop = asyncio.get_running_loop()
    with concurrent.futures.ProcessPoolExecutor() as pool:
        data_dict = await loop.run_in_executor(pool, send_request, cache_dir,testdatasource)
    

    numpyfloat =np.arange(1,10,dtype = np.single)
    numpydouble = np.arange(1,10,dtype= np.double)    #breakpoint()
    
    # TODO xfail assert data_dict["FP/float"][0].dtype == np.float32

    #This assert will fail while all datatypes are cast to double
    assert data_dict["FP/float"][0].dtype == np.float32
    assert data_dict["FP/double"][0].dtype == np.float64
    assert sum(data_dict["FP/double"]) == 45.0
    assert sum(data_dict["FP/float"]) == 45.0
    assert np.isclose(data_dict["FP/double"].all(), numpydouble.all())
    assert np.isclose(data_dict["FP/float"].all(),numpyfloat.all())
    
    shutil.rmtree(cache_dir)



