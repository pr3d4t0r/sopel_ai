# See:  https://raw.githubcontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt

from sopel import config
from sopel_ai.config import SopelAISection
from sopel_ai.core import DEFAULT_API_KEY
from sopel_ai.core import DEFAULT_LLM
from sopel_ai.core import DEFAULT_LLM_PROVIDER
from sopel_ai.core import DEFAULT_LLM_SERVICE
from sopel_ai.core import DEFAULT_LOG_LEVEL


# +++ tests +++

def test_SopelAISection():
    assert SopelAISection.__dict__.__getitem__('llm_engine').default == DEFAULT_LLM
    assert SopelAISection.__dict__.__getitem__('llm_key').default == DEFAULT_API_KEY
    assert SopelAISection.__dict__.__getitem__('llm_provider').default == DEFAULT_LLM_PROVIDER
    assert SopelAISection.__dict__.__getitem__('llm_service').default == DEFAULT_LLM_SERVICE

