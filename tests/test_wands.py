import os
from tempfile import TemporaryDirectory
from pathlib import Path
import subprocess as sub
import signal
import asyncio
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


@pytest_asyncio.fixture(name="server")
async def fixture_server(server_srcdir, server_builddir):
    Path("stdio").write_text("Before configure")
    # Configure
    sub.run(["cmake", str(server_srcdir)], cwd=str(server_builddir)).check_returncode()
    # Build
    sub.run(["cmake", "--build", "."], cwd=str(server_builddir)).check_returncode()
    # Launch server
    proc = await asyncio.create_subprocess_exec(
        str(server_builddir / "wands_server"),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    yield proc.pid
    proc.send_signal(signal.SIGINT)
    await proc.wait()


@pytest.mark.asyncio
async def test_request(server):
    breakpoint()
    assert True

    # current_dir = os.getcwd()
    # #create build directory via path
    # serverbuilddir = Path(current_dir+"/tests/serverbuilddir")
    # if not serverbuilddir.exists():
    #     serverbuilddir.mkdir(parents=True,exist_ok=True)
    # # cmake from  build directory to server cmake
    # serversourcedir = current_dir + "/server"
    # #serversourcedir = current_dir + "/server"
    # assert sub.run(["cmake","../"]).check_returncode() == 0

    # #make sure I don't need a busy wait sync block
    # # make in Path
    # makestring = str(serverbuilddir)+"/make"
    # assert sub.run(["makestring"]).check_returncode() == 0

    # #make sure I don't need a busy wait sync block
    # # run server
    # #serverproc = await asyncio.create_subprocess_exec('')
    # #kill sobald daten da sind
