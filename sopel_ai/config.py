# See:  https://raw.githubcontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt

from sopel import config
from sopel_ai.core import DEFAULT_API_KEY
from sopel_ai.core import DEFAULT_LLM
from sopel_ai.core import DEFAULT_LLM_PROVIDER
from sopel_ai.core import DEFAULT_LLM_SERVICE
from sopel_ai.core import DEFAULT_LOG_LEVEL


class SopelAISection(config.types.StaticSection):
    llm_engine = config.types.ValidatedAttribute('llm_engine', str, default = DEFAULT_LLM)
    llm_key = config.types.ValidatedAttribute('llm_key', str, default = DEFAULT_API_KEY, is_secret = True)
    llm_provider = config.types.ValidatedAttribute('llm_provider', str, default = DEFAULT_LLM_PROVIDER)
    llm_service = config.types.ValidatedAttribute('llm_service', str, default = DEFAULT_LLM_SERVICE)
    logLevel = config.types.ValidatedAttribute('logLevel', str, default = DEFAULT_LOG_LEVEL)

