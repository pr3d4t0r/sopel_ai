# See:  https://raw.githubusercontent.com/pr3d4t0r/m0toko/master/LICENSE.txt

from motoko import runQuery
from motoko import modelsList
from motoko import versionInfo

import pytest


# +++ constants +++

TEST_SERVICEOLLAMA_LOCALHOST = 'http://localhost:11434/api/generate'
TEST_MODEL = 'mistral'



# +++ fixtures +++

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


test_versionInfo()

