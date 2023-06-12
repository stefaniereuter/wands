import os
import pytest
from pathlib import Path
import shutil
import numpy as np

from wands import DataCache

def test_init():
    #current_dir = os.getcwd()
    current_dir  = os.path.dirname(os.path.abspath(__file__))
    cache_dir = current_dir+"/tests/test_cache"
    obj = DataCache(cache_dir)
    assert obj is not None
    assert cache_dir == obj.__str__()
    IOParams = obj.get_IOParams()
    assert "BP4" in IOParams
    assert Path(cache_dir).exists()
    Path(cache_dir).rmdir()

def test_init2():
    #current_dir = os.getcwd()
    current_dir  = os.path.dirname(os.path.abspath(__file__))
    cache_dir = current_dir+"/tests/test_cache"
    obj = DataCache(Path(cache_dir))
    assert obj is not None
    assert cache_dir == obj.__str__()
    IOParams = obj.get_IOParams()
    assert "BP4" in IOParams
    assert Path(cache_dir).exists()
    Path(cache_dir).rmdir()
   
def test_init3():
    cache_dir = 1234
    with pytest.raises(TypeError):
        obj = DataCache(cache_dir)
    
def test_write_wrong_datatype():
    current_dir = os.getcwd()
    cache_dir = current_dir+"/tests/test_cache"
    obj = DataCache(cache_dir)
    testlist = []
    with pytest.raises(TypeError):
        obj.write("testfile",testlist)

def test_write_empty_dict():
    current_dir = os.getcwd()
    cache_dir = current_dir+"/tests/test_cache"
    obj = DataCache(cache_dir)
    testdict = {}
    with pytest.raises(TypeError):
        obj.write("testfile",testdict)


def test_datacache():
    current_dir = os.getcwd()
    print(current_dir)
    cache_dir = current_dir+"/tests/test_cache"
    obj = DataCache(cache_dir)
    testdict = {}
    testdict["testdata"] = np.ones(3,"float")
    obj.write("testfile",testdict)

    assert Path(cache_dir+"/testfile").exists()
    requestlist = ["testdata","testdata1"]
    [remotelist,locallist] = obj.check_availability("testfile",requestlist)
    assert locallist == ["testdata"]
    assert remotelist == ["testdata1"]
    
    recdict = {}
    recdict = obj.load_from_cache(filename="testfile",local_list=locallist)
    assert np.array_equal(recdict["testdata"],np.ones(3,"float"),equal_nan=False)
    with pytest.raises(KeyError):
        obj.load_from_cache(filename="testfile",local_list=remotelist)
    shutil.rmtree(cache_dir)
    obj.close()


def test_datacache2():
    current_dir = os.getcwd()
    cache_dir = current_dir+"/tests/test_cache"
    obj = DataCache(cache_dir)
    testdict = {}
    testdict["testdata"] = np.random.rand(3,4)
    print(testdict)
    obj.write("testfile.h5",testdict)
    # #with pytest.raises(NotImplementedError):
    obj.write("testfile.h5",testdict)
    assert Path(cache_dir+"/testfile.bp").exists()
    requestlist = ["testdata","testdata1"]
    [remotelist,locallist] = obj.check_availability("testfile.bp",requestlist)
    assert locallist == ["testdata"]
    assert remotelist == ["testdata1"]

    recdict = {}
    recdict = obj.load_from_cache(filename="testfile.bp",local_list=locallist)
    assert np.array_equal(recdict["testdata"],testdict["testdata"],equal_nan=False)
    with pytest.raises(KeyError):
        obj.load_from_cache(filename="testfile.bp",local_list=remotelist)
    shutil.rmtree(cache_dir)
    obj.close()

def test_datacache_check_availability():
    current_dir = os.getcwd()
    print(current_dir)
    cache_dir = current_dir+"/tests/test_cache"
    obj = DataCache(cache_dir)
    testdict = {}
    testdict["testdata"] = np.random.rand(3,4)
    print(testdict)
    obj.write("testfile.h5",testdict)
    # #with pytest.raises(NotImplementedError):
    obj.write("testfile.h5",testdict)
    assert Path(cache_dir+"/testfile.bp").exists()
    requestlist = ["testdata","testdata1"]
    [remotelist,locallist] = obj.check_availability("doesnotexist.bp",requestlist)
    assert remotelist == requestlist
    assert len(locallist) == 0

    shutil.rmtree(cache_dir)
    obj.close()    

def test_datacache_load_from_cache():
    current_dir = os.getcwd()
    print(current_dir)
    cache_dir = current_dir+"/tests/test_cache"
    obj = DataCache(cache_dir)
   
    requestlist = ["testdata","testdata1"]
    
    with pytest.raises(ValueError):
        obj.load_from_cache(filename="doesntexist.h5",local_list=requestlist)
    
    shutil.rmtree(cache_dir)
    obj.close()    