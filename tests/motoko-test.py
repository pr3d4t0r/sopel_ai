# See:  https://raw.githubusercontent.com/pr3d4t0r/m0toko/master/LICENSE.txt

from motoko import runQuery

import pytest


# +++ constants +++

TEST_SERVICEOLLAMA_LOCALHOST = 'http://localhost:11434/api/generate'
TEST_MODEL = 'mistral'



# +++ fixtures +++

@pytest.fixture
def serviceHost():
    return TEST_SERVICEOLLAMA_LOCALHOST


@pytest.fixture
def model():
    return TEST_MODEL


# +++ tests +++

def test_runQuery(serviceHost, model):
    query = 'What is an LLM?'

    result = runQuery(query, serviceHost, model)
    assert type(result) == str

    result = runQuery(None, serviceHost, model)
    assert 'M0tokoError' in result
    result = runQuery(query, 'http:', model)
    assert 'ConnectError' in result
    result = runQuery(query, serviceHost, 'bogus')
    assert 'ResponseError' in result

