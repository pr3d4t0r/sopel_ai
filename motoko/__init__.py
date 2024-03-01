# See:  https://raw.githubusercontent.com/pr3d4t0r/m0toko/master/LICENSE.txt

"""
# m0toko - a bot for querying LLMs and getting quick answers.
"""


from perplexipy import PERPLEXITY_API_URL
from perplexipy import PerplexityClient
from sopel import config
from sopel import formatting
from sopel import plugin

import logging
import os
import sys


__VERSION__ = '1.0.5'


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


def _checkClientInstance():
    global _client

    if not _client:
        _client = PerplexityClient(endpoint = PERPLEXITY_API_URL)
        # TODO:  Make this selectable; see:  https://github.com/pr3d4t0r/m0toko/issues/4
        _client.model = 'mistral-7b-instruct'


def runQuery(query: str) -> str:
    """
    Run a query against the LLM engine using the PerpleipyClient, and return the
    query result in a string.

    Arguments
    ---------
        query
    A string with the user's query in English, Spanish, Russian, French, or any
    other mainstream language.

        serviceHost
    The URL to the host serving the LLM results.

    Returns
    -------
    A string with the response if the service found a reasonable and convenient
    one, or the text of an Error and the possible cause, as reported by the
    Python run-time.
    """

    # TODO:  Implement through dynamic loading in a future version.
    _checkClientInstance()

    try:
        if not query:
            raise M0tokoError('query parameter cannot be empty')
        query = 'Brief answer in %s characters or less to: "%s". Include one URL in the response and strip off all Markdown and hashtags.' % (MAX_RESPONSE_LENGTH, query)

        LOGGER.info('{ "query": "%s" }' % query)
        result = _client.query(query).replace('\n', '')
    except Exception as e:
        result = '%s = %s' % (str(type(e)), e)

    return result


def modelsList() -> list:
    """
    Returns a list of all available models so that they can be used for
    requesting a specific one in another command.

    Returns
    -------
    A list of model names supported by the underlying API service.
    """
    _checkClientInstance()

    return list(_client.models.keys())


def versionInfo():
    _checkClientInstance()
    return 'm0toko v%s using %s' % (__VERSION__, '.'.join([_client.__class__.__module__, _client.__class__.__name__]))


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
def queryCommand(bot, trigger):
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
@plugin.require_account(message = 'You must be a registered user to use this command.', reply = True)
@plugin.thread(True)
def versionCommand(bot, trigger):
    bot.reply(versionInfo())


@plugin.commands('models')
@plugin.example(".models - lists the models available")
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered user to use this command.', reply = True)
@plugin.thread(True)
def modelsCommand(bot, trigger):
    models = sorted(modelsList())
    bot.reply('Available models: '+', '.join(models))


@plugin.commands('bug', 'feature', 'req')
@plugin.example('.bug|.feature|.req Displays the URL for opening a GitHub issues request')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered user to use this command.', reply = True)
@plugin.thread(True)
def reqCommand(bot, trigger):
    locator = formatting.bold(GITHUB_NEW_ISSUE_URL)
    bot.reply('M0toko version %s. Enter your bug report or feature request at this URL:  %s' % (__VERSION__, locator))


if '__main__' == __name__:
    main()

