# See:  https://raw.githubcontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt
"""
This module is intended for interfacing with Sopel and there are no
user-callable objects, functions defined in it.  If in doubt, user the Force and
read the Source.
"""

from sopel.bot import Sopel
from sopel.bot import SopelWrapper
from sopel.config import Config
from sopel import formatting
from sopel import plugin
from sopel.trigger import Trigger
from sopel_ai.config import SopelAISection
from sopel_ai.core import DEFAULT_LLM
from sopel_ai.core import DEFAULT_LLM_PROVIDER
from sopel_ai.core import DEFAULT_LLM_SERVICE
from sopel_ai.core import DEFAULT_LOG_LEVEL
from sopel_ai.core import GITHUB_NEW_ISSUE_URL
from sopel_ai.core import __VERSION__
from sopel_ai.core import getModelForUser
from sopel_ai.core import modelsList
from sopel_ai.core import runQuery
from sopel_ai.core import setModelForUser
from sopel_ai.core import versionInfo

import os


# +++ constants +++

_PLUGIN_OUTPUT_PREFIX = '[sopel_ai] '
_PRIVATE_MESSAGE_RESPONSE_LENGTH = 12*1024
_USER_DB_FILE = os.path.join('/', os.environ['HOME'], '.sopel/sopel_ai-DB.json')


# +++ implementation +++

def setup(bot: Sopel) -> None:
    """
    @private
    """
    bot.config.define_section('sopel_ai', SopelAISection)


def configure(config: Config) -> None:
    """
    @private
    """
    config.define_section('sopel_ai', SopelAISection)
    config.sopel_ai.configure_setting('llm_engine', 'Set the LLM engine', default = DEFAULT_LLM)
    config.sopel_ai.configure_setting('llm_provider', 'Set the LLM provider name', default = DEFAULT_LLM_PROVIDER)
    config.sopel_ai.configure_setting('llm_service', 'Set the LLM service URL', default = DEFAULT_LLM_SERVICE)
    config.sopel_ai.configure_setting('logLevel', 'Set the log level', default = DEFAULT_LOG_LEVEL)


@plugin.commands('q', 'llmq')
@plugin.example('.q|.llmq Some question about anything')
@plugin.output_prefix(_PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _queryCommand(bot: SopelWrapper, trigger: Trigger) -> None:
    if not trigger.group(2):
        # TODO:  Log this
        bot.reply('No search term. Usage: {}q Some question about anything'.format(bot.config.core.help_prefix))
        return

    # TODO:  Log this
    bot.reply(runQuery(trigger.group(2), trigger.nick, fileNameDB = _USER_DB_FILE))


@plugin.commands('qpm', 'llmqpm')
@plugin.example('.qpm|.llmqpm Some question about anything; I will reply to you in a private message')
@plugin.output_prefix(_PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _queryCommandPrivateMessage(bot: SopelWrapper, trigger: Trigger) -> None:
    if not trigger.group(2):
        # TODO:  Log this
        bot.reply('No search term. Usage: {}qpm Some question about anything'.format(bot.config.core.help_prefix))
        return

    bot.say(runQuery(trigger.group(2), trigger.nick), trigger.nick, fileNameDB = _USER_DB_FILE, responseLength = _PRIVATE_MESSAGE_RESPONSE_LENGTH)


@plugin.commands('mver')
@plugin.example(".mver displays the current 'bot version")
@plugin.output_prefix(_PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _versionCommand(bot: SopelWrapper, trigger: Trigger) -> None:
    bot.reply(versionInfo())


@plugin.commands('models')
@plugin.example('.models - lists the models available')
@plugin.output_prefix(_PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _modelsCommand(bot: SopelWrapper, trigger: Trigger) -> None:
    models = sorted(modelsList())
    s = ''
    for index in range(len(models)):
        s += '[%d] %s;  ' % (index+1, models[index])
    bot.reply('Available models: %s' % s)


@plugin.commands('setmodel')
@plugin.example('.setmodel 3 Sets the LLM to option 3 from the models list')
@plugin.output_prefix(_PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _setModelCommand(bot: SopelWrapper, trigger: Trigger) -> None:
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
        effectiveModel = setModelForUser(effectiveModelID, trigger.nick, _USER_DB_FILE)
        bot.reply('All your future interactions will use the %s model.' % effectiveModel)


@plugin.commands('getmodel')
@plugin.example('.getmodel Get the model used in your queries')
@plugin.output_prefix(_PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _getModelCommand(bot: SopelWrapper, trigger: Trigger) -> None:
    bot.reply(getModelForUser(trigger.nick, _USER_DB_FILE))


@plugin.commands('mymodel')
@plugin.example('.mymodel [n] Get or set the model used in your queries; n ::= intefer, see .models for value range for n')
@plugin.output_prefix(_PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _myModelCommand(bot: SopelWrapper, trigger: Trigger) -> None:
    if not trigger.group(2):
        _getModelCommand(bot, trigger)
    else:
        _setModelCommand(bot, trigger)


@plugin.commands('bug', 'feature', 'req')
@plugin.example('.bug|.feature|.req Displays the URL for opening a GitHub issues request')
@plugin.output_prefix(_PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _reqCommand(bot: SopelWrapper, trigger: Trigger) -> None:
    locator = formatting.bold(GITHUB_NEW_ISSUE_URL)
    bot.reply('SopelAI version %s. Enter your bug report or feature request at this URL:  %s' % (__VERSION__, locator))

