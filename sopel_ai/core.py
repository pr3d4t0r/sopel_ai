# See:  https://raw.githubcontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt

from perplexipy import PERPLEXITY_API_URL
from perplexipy import PERPLEXITY_DEFAULT_MODEL
from perplexipy import PerplexityClient
from sopel_ai import __VERSION__
from sopel_ai.errors import SopelAIError
from tinydb import Query
from tinydb import TinyDB

# import logging


# +++ constants +++

DEFAULT_API_KEY = 'pplx-3a45enterthekeyhere'
DEFAULT_LLM = PERPLEXITY_DEFAULT_MODEL
DEFAULT_LLM_PROVIDER = 'PerplexityAI'
DEFAULT_LLM_SERVICE = PERPLEXITY_API_URL
DEFAULT_LOG_LEVEL = 'info'
GITHUB_NEW_ISSUE_URL = 'https://github.com/pr3d4t0r/sopel_ai/issues/new'
MAX_RESPONSE_LENGTH = 480
"""
---
`MAX_RESPONSE_LENGTH` ircv3 supports responses of up to 512 characters, including any IRC commands.
This is set to a comfortable maximum.  The API output some times chops the
output at this length in the middle of a word if it was unable to summarize
the resonse.

"""


# +++ initializations +++

# logging.basicConfig(format = '%(asctime)s %(clientip)-15s %(user)-8s %(message)s', encoding = 'utf-8', level = logging.INFO)



# +++ globals +++

# Initialized here to prevent exposing build-dependent paths.

_client = None
_clientCache = dict()
_database = None
# _log = logging.getLogger(__name__)


# +++ implementation +++

def _checkDB(fileName: str) -> TinyDB:
    # Checks if DB exists; if not, it creates it
    global _database

    if not _database:
        _database = TinyDB(fileName)
        _database.table('_default', cache_size = 0)

    return _database


def _checkClientInstance(key: str) -> None:
    global _client

    if not _client:
        _client = PerplexityClient(key = key, endpoint = PERPLEXITY_API_URL)
        _client.model = PERPLEXITY_DEFAULT_MODEL


def runQuery(query: str, nick: str = None, fileNameDB: str = None, responseLength: int = MAX_RESPONSE_LENGTH, key: str = None) -> str:
    """
    Run a query against the LLM engine using the PerplexipyClient, and return the
    query result in a string.

    Arguments
    ---------
        query
    A string with query from `nick` in English, Spanish, Russian, French, or any
    other mainstream language.

        nick
    The nick on whose behalf this query will run.  The plug-in caches specific
    clients for users who requested to use a specific model.

        fileNameDB
    The path to the database in the file system.  Can be absolute or relative.

        responseLength
    The maximum response length requested from the AI provider.  See `MAX_RESPONSE_LENGTH`.

        key
    The LLM service provider API key.

    Returns
    -------
    A string with the response if the service found a reasonable and convenient
    one, or the text of an Error and the possible cause, as reported by the
    Python run-time.

    Raises
    ------
    `SopelAIError` if the `key` is empty or if the query is invalid.  The string
    message in the error reflects the cause.

    ---
    """
    if not key:
        raise SopelAIError('key argument cannot be empty - set the LLM service API key')

    _checkDB(fileNameDB)
    model = getModelForUser(nick, fileNameDB, key)
    if not nick or model == DEFAULT_LLM:
        _checkClientInstance(key)
        client = _client
    else:
        client = _clientCache[nick]

    try:
        if not query:
            raise SopelAIError('query parameter cannot be empty')
        query = 'Brief answer in %s characters or less to: "%s". Include one URL in the response and strip off all Markdown and hashtags.' % (responseLength, query)
        result = client.query(query).replace('\n', '')
    except Exception as e:
        result = '%s = %s' % (str(type(e)), e)

    return result


def modelsList(key: str = None) -> list:
    """
    Returns a list of all available models so that they can be used for
    requesting a specific one in another command.

    Returns
    -------
    An ordered list of model names supported by the underlying API service.  The
    order depends on what the underlying API reports, and it's unlikely to
    change between calls.

    Other SopelAI functions will use the index to refer to a model in the
    collection.

    Raises
    ------
    `SopelAIError` if the `key` is empty or if the query is invalid.  The string
    message in the error reflects the cause.

    ---
    """
    if not key:
        raise SopelAIError('key argument cannot be empty - set the LLM service API key')

    _checkClientInstance(key)

    return sorted(list(_client.models.keys()))


def versionInfo(key: str = None) -> str:
    if not key:
        raise SopelAIError('key argument cannot be empty - set the LLM service API key')

    _checkClientInstance(key)
    return 'sopel_ai v%s using %s' % (__VERSION__, '.'.join([_client.__class__.__module__, _client.__class__.__name__]))


def setModelForUser(modelID: int, nick: str, fileNameDB: str, key = None) -> str:
    """
    Set the model associated with `modelID` for processing requests from `nick`.
    The `modelID` is the index into the `models` object returned by
    `sopel_ai.modelsList()`, from zero.

    Arguments
    ---------
        modelID
    An integer corresponding to the model's occurrence in the models list.


        nick
    A string corresponding to a  nick.

        fileNameDB
    The path to the database in the file system.  Can be absolute or relative.

        key
    The LLM service provider API key.

    The function assumes that `nick` represents a valid user /nick because Sopel
    enforces that the  exists and is registered in the server.

    Returns
    -------
    The model name as a string.

    Raises
    ------
    `sopel_ai.errors.SopelAIError` if the arguments are invalid or out of range.

    ---
    """
    _checkDB(fileNameDB)
    models= modelsList(key)
    if modelID not in range(len(models)):
        raise SopelAIError('modelID outside of available models index range')

    query = Query()

    if _database.search(query.nick == nick):
        _database.update({ 'model': models[modelID], }, query.nick == nick)
    else:
        _database.insert({ 'nick': nick, 'model': models[modelID], })

    return models[modelID]


def getModelForUser(nick: str, fileNameDB: str, key = None) -> str:
    """
    Get the model name for the user with `nick`.

    Arguments
    ---------
        nick
    A string corresponging to a nick.

        fileNameDB
    The path to the database in the file system.  Can be absolute or relative.

        key
    The LLM service provider API key.

    Returns
    -------
    A string representing the model name, if one exists in the database
    associated with the user, `sopel_ai.DEFAULT_LLM` otherwise.

    Raises
    ------
    `sopel_ai.errors.SopelAIError` if the arguments are invalid or out of range.

    ---
    """
    if not key:
        raise SopelAIError('key argument cannot be empty - set the LLM service API key')

    _checkDB(fileNameDB)
    Preference = Query()
    preference = _database.search(Preference.nick == nick)
    if preference:
        client = PerplexityClient(key = key, endpoint = PERPLEXITY_API_URL)
        model = preference[0]['model']
        # TODO: Implement unit test for this case.
        if model not in client.models.keys():
            model = tuple(client.models.keys())[0]
        client.model = model
        _clientCache[nick] = client
        return model
    else:
        return DEFAULT_LLM

