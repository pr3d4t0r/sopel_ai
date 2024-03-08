# See:  https://raw.githubcontent.com/pr3d4t0r/sopel_ai/master/LICENSE.txt


import importlib.metadata


__VERSION__ = importlib.metadata.version('sopel-ai')
"""
@public
"""

__moduleInfo__ = 'module info'
"""
@public
The sopel_ai core functions have no dependencies on the Sopel API and may be
invoked from any stand-alone program or from other plugins.  The only
prerrequisite is that a valid LLM provider is defined.

**Perplexity AI** is the default provider for this version.


---
### Users manual

The instructions on how to install sopel_ai and the commands list are available
in the <a href='https://github.com/pr3d4t0r/sopel_ai/' target='_blank'>sopel_ai README.md</a>
file.  If sopel_ai was installed through Homebrew, apt, or other package manager
the documentation is available as a manpage via `man sopel_ai`.


---
### Resources

- **<a href='https://github.com/pr3d4t0r/sopel_ai/' target='_blank'>sopel_ai GitHub repository</a>**
- <a href='https://www.perplexity.ai' target='_blank'>Perplexity AI</a>
-  **<a href='https://pypi.org/project/perplexipy' target='_blank'>PerplexiPy</a>** on PyPi
- The **<a href='https://sopel.chat' target='_blank'>Sopel</a>** bot documentation


---
### License

The **Sopel AI** Sopel plug-in, package, documentation, and examples are
licensed under the <a href='https://github.com/pr3d4t0r/sopel_ai/blob/master/LICENSE.txt' target='_blank'>BSD-3 open source license</a>.


---
### Implementation

The `core` module is the main funcionality provider for this API.  The other
modules support operations in `core` or for interacting with the bot.

The `plugin` module defines the sopel_ai bot commands and integrates them with
the bot.  It's not documented here because its functionality is considered to
be internal use only, and subject to change in response to changes to Sopel.
Those changes are independent of the sopel_ai core functionality.


---
### User database

Users can customize which LLM they use for their query.  `runQuery()` will use
a different model to produce responses for users `alice` and `bob` if each set
a desired model using the `setModelForUser()` function.  Values are stored
in a JSON document database referenced by the `fileNameDB` variable in the
calls to these functions.  The `DEFAULT_LLM` will be used if a user didn't
change the model choice.

There are no restrictions on where `fileNameDB` can exist in the file system.
This implementation defaults to `$HOME/.sopel/sopel_ai-DB.json`, future versions
may use the `appdir` module instead.
"""

