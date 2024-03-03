# See:  https://raw.githubcontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt

"""
# sopel_ai - a bot plugin for querying LLMs and getting quick answers.
"""


from perplexipy import PERPLEXITY_API_KEY
from perplexipy import PERPLEXITY_API_URL
from perplexipy import PERPLEXITY_DEFAULT_MODEL
from perplexipy import PerplexityClient
from sopel_ai.errors import M0tokoError
from tinydb import Query
from tinydb import TinyDB

# import logging
import os


__VERSION__ = '1.0.10'


# +++ constants +++

CONFIG_FILE = os.path.join('/', os.environ['HOME'], '.sopel/default.cfg')
DEFAULT_LLM = PERPLEXITY_DEFAULT_MODEL
DEFAULT_LLM_PROVIDER = 'PerplexityAI'
DEFAULT_LLM_SERVICE = PERPLEXITY_API_URL
DEFAULT_LOG_LEVEL = 'info'
GITHUB_NEW_ISSUE_URL = 'https://github.com/pr3d4t0r/sopel_ai/issues/new'
MAX_RESPONSE_LENGTH = 448
USER_DB_FILE = os.path.join('/', os.environ['HOME'], '.sopel/sopel_ai-DB.json')


# +++ initializations +++

# logging.basicConfig(format = '%(asctime)s %(clientip)-15s %(user)-8s %(message)s', encoding = 'utf-8', level = logging.INFO)



# +++ globals +++

_client = None
_clientCache = dict()
_database = None
# _log = logging.getLogger(__name__)


# +++ implementation +++

def _checkDB(fileName: str = USER_DB_FILE) -> TinyDB:
    # Checks if DB exists; if not, it creates it
    global _database

    if not _database:
        _database = TinyDB(fileName)

    return _database


def _checkClientInstance() -> None:
    global _client

    if not _client:
        _client = PerplexityClient(key = PERPLEXITY_API_KEY, endpoint = PERPLEXITY_API_URL)
        _client.model = PERPLEXITY_DEFAULT_MODEL


def runQuery(query: str, nick: str = None) -> str:
    """
    Run a query against the LLM engine using the PerpleipyClient, and return the
    query result in a string.

    Arguments
    ---------
        query
    A string with the 's query in English, Spanish, Russian, French, or any
    other mainstream language.

        nick
    The nick on whose behalf this query will run.  The plug-in caches specific
    clients for users who requested to use a specific model.

    Returns
    -------
    A string with the response if the service found a reasonable and convenient
    one, or the text of an Error and the possible cause, as reported by the
    Python run-time.
    """

    model = getModelForUser(nick, USER_DB_FILE)
    print('*** nick = %s, query = %s, model = %s' % (nick, query, model))
    if not nick or model == DEFAULT_LLM:
        _checkClientInstance()
        client = _client
    else:
        client = _clientCache[nick]

    try:
        if not query:
            raise M0tokoError('query parameter cannot be empty')
        query = 'Brief answer in %s characters or less to: "%s". Include one URL in the response and strip off all Markdown and hashtags.' % (MAX_RESPONSE_LENGTH, query)
        result = client.query(query).replace('\n', '')
    except Exception as e:
        result = '%s = %s' % (str(type(e)), e)

    return result


def modelsList() -> list:
    """
    Returns a list of all available models so that they can be used for
    requesting a specific one in another command.

    Returns
    -------
    An ordered list of model names supported by the underlying API service.  The
    order depends on what the underlying API reports, and it's unlikely to
    change between calls.

    Other M0toko functions will use the index to refer to a model in the
    collection.
    """
    _checkClientInstance()

    return sorted(list(_client.models.keys()))


def versionInfo() -> str:
    _checkClientInstance()
    return 'sopel_ai v%s using %s' % (__VERSION__, '.'.join([_client.__class__.__module__, _client.__class__.__name__]))


def setModelForUser(modelID: int, nick: str, fileNameDB: str) -> str:
    """
    Set the model associated with `modelID` for processing requests from ``.
    The `modelID` is the index into the `models` object returned by
    `motoko.modelsList()`, from zero.

    Arguments
    ---------
        modelID
    An integer corresponding to the model's occurrence in the models list.


        nick
    A string corresponding to a  nick.

        fileNameDB
    The path to the database in the file system.  Can be absolute or relative.

    The function assumes that `` represents a valid user /nick because Sopel
    enforces that the  exists and is registered in the server.

    Returns
    -------
    The model name as a string.

    Raises
    ------
    `motoko.errors.M0tokoError` if the arguments are invalid or out of range.
    """
    _checkDB(fileNameDB)
    models= modelsList()
    if modelID not in range(len(models)):
        raise M0tokoError('modelID outside of available models index range')

    Preference = Query()

    if _database.search(Preference.nick == nick):
        _database.update({ 'model': models[modelID], }, Preference.nick == nick)
    else:
        _database.insert({ 'nick': nick, 'model': models[modelID], })

    return models[modelID]


def getModelForUser(nick: str, fileNameDB) -> str:
    """
    Get the model name for the user with `nick`.

    Arguments
    ---------
        nick
    A string corresponging to a nick.

        fileNameDB
    The path to the database in the file system.  Can be absolute or relative.

    Returns
    -------
    A string representing the model name, if one exists in the database
    associated with the user, `motoko.DEFAULT_LLM` otherwise.
    """
    _checkDB(fileNameDB)
    Preference = Query()
    preference = _database.search(Preference.nick == nick)
    if preference:
        model = preference[0]['model']
        client = PerplexityClient(key = PERPLEXITY_API_KEY, endpoint = PERPLEXITY_API_URL)
        client.model = model
        _clientCache[nick] = client
        return model
    else:
        return DEFAULT_LLM

