# See:  https://raw.githubusercontent.com/pr3d4t0r/m0toko/master/LICENSE.txt

from tempfile import mkstemp

from motoko import M0tokoError
from motoko import _checkDB
from motoko import modelsList
from motoko import runQuery
from motoko import setModelForUser
from motoko import versionInfo
from tinydb import TinyDB

import os

import pytest


# +++ fixtures +++
@pytest.fixture
def testDatabasePath(request):
    def finalizer():
        try:
            os.unlink(databasePath)
        except:
            pass

    if request:
        request.addfinalizer(finalizer)
    databasePath = mkstemp(suffix = '.json', text = True)[1]
    return databasePath


# +++ tests +++

def test_runQuery():
    query = 'What is a large language model?'

    result = runQuery(query)
    assert type(result) == str
    assert 'M0tokoError' not in result


def test_modelsList():
    models = modelsList()

    assert isinstance(models, list)
    assert isinstance(models[0], str)


def test_versionInfo():
    info = versionInfo()

    assert isinstance(info, str)
    assert 'Client' in info


def test__checkDB(testDatabasePath):
    assert isinstance(_checkDB(testDatabasePath), TinyDB)


def test_setModelForUser(testDatabasePath):
    _checkDB(testDatabasePath)

    # New user:
    model = setModelForUser(0, 'joe', testDatabasePath)
    assert model == modelsList()[0]

    # Existing user:
    model = setModelForUser(1, 'joe', testDatabasePath)
    assert model == modelsList()[1]

    # Model out of range:
    with pytest.raises(M0tokoError):
        setModelForUser(99, 'joe', testDatabasePath)


# databasePath = mkstemp(suffix = '.json', text = True)[1]
# test_setModelForUser(databasePath)

