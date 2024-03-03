# See:  https://raw.githubcontent.com/pr3d4t0r/m0toko/master/LICENSE.txt

from sopel import formatting
from sopel import plugin
from sopel.bot import Sopel
from sopel.bot import SopelWrapper
from sopel.config import Config
from sopel.trigger import Trigger
from sopel_motoko import DEFAULT_LLM
from sopel_motoko import DEFAULT_LLM_PROVIDER
from sopel_motoko import DEFAULT_LLM_SERVICE
from sopel_motoko import DEFAULT_LOG_LEVEL
from sopel_motoko import GITHUB_NEW_ISSUE_URL
from sopel_motoko import USER_DB_FILE
from sopel_motoko import __VERSION__
from sopel_motoko.config import M0tokoSection


# +++ constants +++

PLUGIN_OUTPUT_PREFIX = '[m0toko] '


# +++ implementation +++

def configure(config: Config) -> None:
    config.define_section('m0toko', M0tokoSection)
    config.m0toko.configure_setting('llm_engine', 'Set the LLM engine', default = DEFAULT_LLM)
    config.m0toko.configure_setting('llm_provider', 'Set the LLM provider name', default = DEFAULT_LLM_PROVIDER)
    config.m0toko.configure_setting('llm_service', 'Set the LLM service URL', default = DEFAULT_LLM_SERVICE)
    config.m0toko.configure_setting('logLevel', 'Set the log level', default = DEFAULT_LOG_LEVEL)


def setup(bot: Sopel) -> None:
    bot.config.define_section('m0toko', M0tokoSection)


@plugin.commands('q', 'llmq', 'lookup')
@plugin.example('.lookup|.q|.llmq Some question about anything')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _queryCommand(bot: SopelWrapper, trigger: Trigger) -> None:
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
def _versionCommand(bot: SopelWrapper, trigger: Trigger) -> None:
    bot.reply(versionInfo())


@plugin.commands('models')
@plugin.example('.models - lists the models available')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
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
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
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
        effectiveModel = setModelForUser(effectiveModelID, trigger.nick, USER_DB_FILE)
        bot.reply('All your future interactions will use the %s model.' % effectiveModel)


@plugin.commands('getmodel')
@plugin.example('.getmodel Get the model used in your queries')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _getModelCommand(bot: SopelWrapper, trigger: Trigger) -> None:
    bot.reply(getModelForUser(trigger.nick, USER_DB_FILE))


@plugin.commands('mymodel')
@plugin.example('.mymodel [n] Get or set the model used in your queries; n ::= intefer, see .models for value range for n')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _myModelCommand(bot: SopelWrapper, trigger: Trigger) -> None:
    if not trigger.group(2):
        _getModelCommand(bot, trigger)
    else:
        _setModelCommand(bot, trigger)


@plugin.commands('bug', 'feature', 'req')
@plugin.example('.bug|.feature|.req Displays the URL for opening a GitHub issues request')
@plugin.output_prefix(PLUGIN_OUTPUT_PREFIX)
@plugin.require_account(message = 'You must be a registered  to use this command.', reply = True)
@plugin.thread(True)
def _reqCommand(bot: SopelWrapper, trigger: Trigger) -> None:
    locator = formatting.bold(GITHUB_NEW_ISSUE_URL)
    bot.reply('M0toko version %s. Enter your bug report or feature request at this URL:  %s' % (__VERSION__, locator))

