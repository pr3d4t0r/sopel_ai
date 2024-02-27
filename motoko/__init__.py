# See:  https://raw.githubusercontent.com/pr3d4t0r/m0toko/master/LICENSE.txt

"""
# m0toko - a bot for querying LLMs and getting quick answers.
"""


from ollama import Client as OllamaClient
from perplexipy import PerplexityClient
from perplexipy import PERPLEXITY_API_KEY
from sopel import config
from sopel import formatting
from sopel import plugin

import logging
import os
import sys

import ollama


__VERSION__ = '1.0.3'


# +++ constants +++

CONFIG_FILE = os.path.join('/', os.environ['HOME'], '.sopel/default.cfg')
DEFAULT_LLM = 'mistral'
DEFAULT_LLM_PROVIDER = 'ollama'
DEFAULT_LLM_SERVICE = 'http://localhost:11434/api/generate'
GITHUB_NEW_ISSUE_URL = 'https://github.com/pr3d4t0r/m0toko/issues/new'
LOGGER = logging.getLogger(__name__)
MAX_RESPONSE_LENGTH = 448
PLUGIN_OUTPUT_PREFIX = '[m0toko] '


# +++ globals +++

_client = None


# +++ implementation +++

class M0tokoError(Exception):
    def __init__(self, obj):
        super().__init__(obj)


class M0tokoSection(config.types.StaticSection):
    llm_engine = config.types.ValidatedAttribute('llm_engine', str, default = DEFAULT_LLM)
    llm_provider = config.types.ValidatedAttribute('llm_provider', str, default = DEFAULT_LLM_PROVIDER)
    llm_service = config.types.ValidatedAttribute('llm_service', str, default = DEFAULT_LLM_SERVICE)


def configure(config):
    config.define_section('m0toko', M0tokoSection)
    config.m0toko.configure_setting('llm_engine', 'Set the LLM engine', default = DEFAULT_LLM)
    config.m0toko.configure_setting('llm_provider', 'Set the LLM provider name', default = DEFAULT_LLM_PROVIDER)
    config.m0toko.configure_setting('llm_service', 'Set the LLM service URL', default = DEFAULT_LLM_SERVICE)


def setup(bot):
    bot.config.define_section('m0toko', M0tokoSection)
    LOGGER.info('started')


def shutdown(bot):
    pass


def _runQueryOllama(query: str, serviceHost: str, model: str = DEFAULT_LLM) -> str:
    """
    Experimental.
    """
    queryData = {
        'role': 'user',
        'content': 'Brief answer in %s characters or less to: "%s". Include one URL in the response and strip off all Markdown and hashtags.' % (MAX_RESPONSE_LENGTH, query),
    }
    try:
        if not query:
            raise M0tokoError('query parameter cannot be empty')

        LOGGER.info('{ "query": "%s" }' % query)
        client = OllamaClient(host = serviceHost)
        response = client.chat(model = model, messages = [ queryData, ])
        result = response['message']['content'].strip()
    except Exception as e:
        result = '%s = %s' % (str(type(e)), e)

    return result


def runQuery(query: str, serviceHost: str, model: str = DEFAULT_LLM) -> str:
    """
    Run a query against the LLM engine using the OllamaClient, and return the
    query result in a string.

    Arguments
    ---------
        query
    A string with the user's query in English, Spanish, Russian, French, or any
    other mainstream language.

        serviceHost
    The URL to the host serving the LLM results.

        model
    The model's name (no version) to use for the query.

    Returns
    -------
    A string with the response if the service found a reasonable and convenient
    one, or the text of an Error and the possible cause, as reported by the
    Python run-time.
    """
    global _client

    if not _client:
        _client = PerplexityClient()

    try:
        if not query:
            raise M0tokoError('query parameter cannot be empty')

        LOGGER.info('{ "query": "%s" }' % query)
        result = _client.query(query)
    except Exception as e:
        result = '%s = %s' % (str(type(e)), e)

    return result


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
@plugin.require_account(message = 'You must be a registered user to use this command.', reply = True)
@plugin.thread(True)
def lookupCommand(bot, trigger):
    if not trigger.group(2):
        # TODO:  Log this
        bot.reply('No search term. Usage: {}lookup Some question about anything'.format(bot.config.core.help_prefix))
        return

    # TODO:  Log this
    serviceHost = config.Config(CONFIG_FILE).m0toko.llm_service
    model = config.Config(CONFIG_FILE).m0toko.llm_engine
    bot.reply(runQuery(trigger.group(2), serviceHost, model))


@plugin.commands('.mversion')
@plugin.example(".mversion displays the current 'bot version")
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered user to use this command.', reply = True)
@plugin.thread(True)
def versionCommand(bot, trigger):
    bot.reply('m0toko v%s' % __VERSION__)


@plugin.commands('models')
@plugin.example(".models - lists the models available")
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered user to use this command.', reply = True)
@plugin.thread(True)
def listModels(bot, trigger):
    models = sorted(e['name'].replace(':latest', '') for e in ollama.list()['models'])

    bot.reply('Available models: '+', '.join(models))


@plugin.commands('bug', 'feature', 'req')
@plugin.example('.bug|.feature|.req Displays the URL for opening a GitHub issues request')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered user to use this command.', reply = True)
@plugin.thread(True)
def reqCommand(bot, trigger):
    locator = formatting.bold(GITHUB_NEW_ISSUE_URL)
    bot.reply('M0toko version %s. Enter your bug report or feature request at this URL:  %s' % (__VERSION__, locator))

