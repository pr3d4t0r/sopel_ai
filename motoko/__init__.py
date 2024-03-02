# See:  https://raw.githubcontent.com/pr3d4t0r/m0toko/master/LICENSE.txt

"""
# m0toko - a bot for querying LLMs and getting quick answers.
"""


# from motoko.errors import M0tokoError
from perplexipy import PERPLEXITY_API_KEY
from perplexipy import PERPLEXITY_API_URL
from perplexipy import PERPLEXITY_DEFAULT_MODEL
from perplexipy import PerplexityClient
from sopel import config
from sopel import formatting
from sopel import plugin
from tinydb import Query
from tinydb import TinyDB

import logging
import os
import sys


__VERSION__ = '1.0.6'


# +++ constants +++

CONFIG_FILE = os.path.join('/', os.environ['HOME'], '.sopel/default.cfg')
DEFAULT_LLM = PERPLEXITY_DEFAULT_MODEL
DEFAULT_LLM_PROVIDER = 'PerplexityAI'
DEFAULT_LLM_SERVICE = PERPLEXITY_API_URL
DEFAULT_LOG_LEVEL = 'info'
GITHUB_NEW_ISSUE_URL = 'https://github.com/pr3d4t0r/m0toko/issues/new'
LOGGER = logging.getLogger(__name__)
MAX_RESPONSE_LENGTH = 448
PLUGIN_OUTPUT_PREFIX = '[m0toko] '
USER_DB_FILE = os.path.join('/', os.environ['HOME'], '.sopel/m0toko-DB.json')


# +++ globals +++

_client = None
_clientCache = dict()
_database = None


# +++ implementation +++

class M0tokoError(Exception):
    def __init__(self, exceptionInfo):
        super().__init__(exceptionInfo)

class M0tokoSection(config.types.StaticSection):
    llm_engine = config.types.ValidatedAttribute('llm_engine', str, default = DEFAULT_LLM)
    llm_provider = config.types.ValidatedAttribute('llm_provider', str, default = DEFAULT_LLM_PROVIDER)
    llm_service = config.types.ValidatedAttribute('llm_service', str, default = DEFAULT_LLM_SERVICE)
    logLevel = config.types.ValidatedAttribute('logLevel', str, default = DEFAULT_LOG_LEVEL)


def configure(config):
    config.define_section('m0toko', M0tokoSection)
    config.m0toko.configure_setting('llm_engine', 'Set the LLM engine', default = DEFAULT_LLM)
    config.m0toko.configure_setting('llm_provider', 'Set the LLM provider name', default = DEFAULT_LLM_PROVIDER)
    config.m0toko.configure_setting('llm_service', 'Set the LLM service URL', default = DEFAULT_LLM_SERVICE)
    config.m0toko.configure_setting('logLevel', 'Set the log level', default = DEFAULT_LOG_LEVEL)


def _checkDB(fileName: str = USER_DB_FILE):
    # Checks if DB exists; if not, it creates it
    global _database

    if not _database:
        _database = TinyDB(fileName)

    return _database


def setup(bot):
    bot.config.define_section('m0toko', M0tokoSection)
    _checkDB(USER_DB_FILE)
    LOGGER.info('started')


def shutdown(bot):
    pass


def _checkClientInstance():
    global _client

    if not _client:
        _client = PerplexityClient(key = PERPLEXITY_API_KEY, endpoint = PERPLEXITY_API_URL)
        # TODO:  Make this selectable; see:  https://github.com/pr3d4t0r/m0toko/issues/4
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

    if not nick or getModelForUser(nick, USER_DB_FILE) == DEFAULT_LLM:
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


def versionInfo():
    _checkClientInstance()
    return 'm0toko v%s using %s' % (__VERSION__, '.'.join([_client.__class__.__module__, _client.__class__.__name__]))


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


def main():
    LOGGER.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    LOGGER.addHandler(handler)
    LOGGER.info('Let us see some output:')
    LOGGER.info(runQuery('Tell me about Taylor Swift.'))


@plugin.commands('q', 'llmq', 'lookup')
@plugin.example('.lookup|.q|.llmq Some question about anything')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _queryCommand(bot, trigger):
    if not trigger.group(2):
        # TODO:  Log this
        bot.reply('No search term. Usage: {}lookup Some question about anything'.format(bot.config.core.help_prefix))
        return

    # TODO:  Log this
    # TODO:  Fix this with dynamic model loading:
    bot.reply(runQuery(trigger.group(2)))


@plugin.commands('mver')
@plugin.example(".mver displays the current 'bot version")
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _versionCommand(bot, trigger):
    bot.reply(versionInfo())


@plugin.commands('models')
@plugin.example('.models - lists the models available')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _modelsCommand(bot, trigger):
    models = sorted(modelsList())
    s = ''
    for index in range(len(models)):
        s += '[%d] %s;  ' % (index+1, models[index])
    bot.reply('Available models: %s' % s)


@plugin.commands('setmodel')
@plugin.example('.setmodel 3 Sets the LLM to option 3 from the models list')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _setModelCommand(bot, trigger):
    try:
        modelID = int(trigger.group(2))
    except:
        modelID = -1
    models = modelsList()
    if modelID not in range(1, len(models)+1):
        message = 'Invalid model ID; must be in range %s. Usage: {}setmodel n, where n ::= integer' % ('1 - %d' % len(models))
        bot.reply(message.format(bot.config.core.help_prefix))
    else:
        effectiveModelID = modelID-1
        effectiveModel = setModelForUser(effectiveModelID, trigger.nick, USER_DB_FILE)
        bot.reply('All your future interactions will use the %s model.' % effectiveModel)


@plugin.commands('getmodel')
@plugin.example('.getmodel Get the model used in your queries')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _getModelCommand(bot, trigger):
    bot.reply(getModelForUser(trigger.nick, USER_DB_FILE))


@plugin.commands('mymodel')
@plugin.example('.mymodel [n] Get or set the model used in your queries; n ::= intefer, see .models for value range for n')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _myModelCommand(bot, trigger):
    if not trigger.group(2):
        _getModelCommand(bot, trigger)
    else:
        _setModelCommand(bot, trigger)


@plugin.commands('bug', 'feature', 'req')
@plugin.example('.bug|.feature|.req Displays the URL for opening a GitHub issues request')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _reqCommand(bot, trigger):
    locator = formatting.bold(GITHUB_NEW_ISSUE_URL)
    bot.reply('M0toko version %s. Enter your bug report or feature request at this URL:  %s' % (__VERSION__, locator))


if '__main__' == __name__:
    main()

