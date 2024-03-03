# See:  https://raw.githubcontent.com/pr3d4t0r/m0toko/master/LICENSE.txt

from sopel import config
from sopel_motoko import DEFAULT_LLM
from sopel_motoko import DEFAULT_LLM_PROVIDER
from sopel_motoko import DEFAULT_LLM_SERVICE
from sopel_motoko import DEFAULT_LOG_LEVEL


class M0tokoSection(config.types.StaticSection):
    llm_engine = config.types.ValidatedAttribute('llm_engine', str, default = DEFAULT_LLM)
    llm_provider = config.types.ValidatedAttribute('llm_provider', str, default = DEFAULT_LLM_PROVIDER)
    llm_service = config.types.ValidatedAttribute('llm_service', str, default = DEFAULT_LLM_SERVICE)
    logLevel = config.types.ValidatedAttribute('logLevel', str, default = DEFAULT_LOG_LEVEL)

