# See:  https://raw.githubusercontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt

from tempfile import mkstemp

from sopel.config import Config
from sopel_ai.core import DEFAULT_LLM
from sopel_ai.core import SopelAIError
from sopel_ai.core import _checkDB
from sopel_ai.core import getModelForUser
from sopel_ai.core import modelsList
from sopel_ai.core import runQuery
from sopel_ai.core import setModelForUser
from sopel_ai.core import versionInfo
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


@pytest.fixture
def testAPIKey():
    configfilename = os.path.join(os.environ['HOME'], '.sopel/default.cfg')
    return Config(configfilename).sopel_ai.llm_key


# +++ tests +++

def test_runQuery(testDatabasePath, testAPIKey):
    query = 'What is a large language model?'

    result = runQuery(query, fileNameDB = testDatabasePath, key = testAPIKey)
    assert type(result) == str
    assert 'SopelAIError' not in result


def test_modelsList(testAPIKey):
    models = modelsList(key = testAPIKey)

    assert isinstance(models, list)
    assert isinstance(models[0], str)


def test_versionInfo(testAPIKey):
    info = versionInfo(key = testAPIKey)

    assert isinstance(info, str)
    assert 'Client' in info


def test__checkDB(testDatabasePath):
    assert isinstance(_checkDB(testDatabasePath), TinyDB)


def test_setModelForUser(testDatabasePath, testAPIKey):
    # New user:
    model = setModelForUser(0, 'alice', testDatabasePath, testAPIKey)
    assert model == modelsList(key = testAPIKey)[0]

    # Existing user:
    lastModel = len(modelsList(testAPIKey))-1
    model = setModelForUser(lastModel, 'alice', testDatabasePath, testAPIKey)
    assert model == modelsList(key = testAPIKey)[lastModel]

    # Model out of range:
    with pytest.raises(SopelAIError):
        setModelForUser(99, 'alice', testDatabasePath)


def test_getModelForUser(testDatabasePath, testAPIKey):
    model = getModelForUser('alice', testDatabasePath, key = testAPIKey)
    assert isinstance(model, str)

    model = getModelForUser('bob', testDatabasePath, key = testAPIKey)
    assert model == DEFAULT_LLM


def test_runQueryForUser(testDatabasePath, testAPIKey):
    # Uses the database so it must run after the set/get
    # model tests.
    nick = 'alice'
    query = 'What is a large language model?'
    result = runQuery(query, nick, fileNameDB = testDatabasePath, key = testAPIKey)
    assert result


def test_runQueryResponseLength(testDatabasePath, testAPIKey):
    nick = 'alice'
    query = "Summarize the Three Laws of Robotics, items only, no additional information"
    shortResult = runQuery(query, nick, fileNameDB = testDatabasePath, key = testAPIKey)
    query = "Summarize Assimov's Three Laws of Robotics"
    longResult = runQuery(query, nick, fileNameDB = testDatabasePath, responseLength = 12*1024, key = testAPIKey)

    p = len(shortResult)
    q = len(longResult)
    assert p < q


# For the testing in the debugger
# databasePath = mkstemp(suffix = '.json', text = True)[1]
# configfilename = os.path.join(os.environ['HOME'], '.sopel/default.cfg')
# key = Config(configfilename).sopel_ai.llm_key
# test_runQuery(databasePath, key)
# test_setModelForUser(databasePath, key)
# test_getModelForUser(databasePath, key)
# # # test_runQueryResponseLength(databasePath)
#
