% sopel_ai(1) Version 1.0.12 chatbot plugin

Name
====

**Sopel AI** - AI query/response plugin


Synopsis
========
Enable Sopel to respond to queries using a Perplexity AI back-end, featuring the
ability to plug different LLMs on a per-user basis.

```
pip install -U sopel_ai

sopel configure
sopel
```

From a channel where Sopel AI is present enter a query:

`.q Summarize the plot of The Martian by Andy Weir.`

**This plugin requires an API key issued by the service provider.**


Installation
============
```zsh
pip install -U sopel_ai
```

The installation assumes that the Sopel chatbot is already installed in the
target system and in the same environment as the `pip` installation.

Confirm the installed package and version:

```zsh
echo "import sopel_ai ; print(sopel_ai.__VERSION__)" | python
```


Commands
========
Listed in order of frequency of use:

|Command|Arguments|Effect|
|-------|---------|------|
|`.q`|Some question|The model produces a response|
|`.qpm`|Some question|Same as `.q` but in private message|
|`.models`|n/a|Lists all models that Sopel AI supports|
|`.mymodel`|number|Request or set the model to use for the current /nick|
|`.req`|n/a|Return the GitHub URL for Sopel AI feature requests|
|`.bug`|n/a|Same as `.req`|

Other available commands if the standard Sopen infobot plugins are enabled:

|Command|Arguments|Effect|
|-------|---------|------|
|`.search`|Some question|Search using Bing or DuckDuckGo|
|`.dict`|Word|Get a dictionary definition if one is available|
|`.tr`|Word of phrase|Translate to English|
|`.w`|Word or topic|Search Wikipedia for articles|


Usage
=====
The most common usage is to enter a query in-channel or private message, and
wait for the bot to respond.

`.q Quote the Three Law of Robotics as a list and without details.`

Users may check the current model used for producing their responses by issuing:

`.mymodel`

The bot produces a numbered list of supported models by issuing:

`.models`

Users are welcome to change the default model to one of those listed by issuing
the `.mymodel` command followed by the item number for the desired model from the
list:

`.mymodel 1`

Users may request private instead of in-channel responses:

`.qpm Quote the Three Laws of Robotics and give me examples.`

Users can query the bot plugin and AI provider using:

`.mver`


AI providers
============
The current version uses the Perplexity AI models and API.  Future versions may
support other providers.


API Key
=======
All AI services providers require an API key for access.  This version of
Sopel AI uses one environment variable and two mechanisms for resolving it:

`export PERPLEXITY_API_KEY="pplx-2a45baaf"`

Or use the `.env` file to store this and other secretes.  The underlying
PerplexiPy module uses `dotenv` package for secrets resolution.


License
=======
The **Sopel AI** Sopel plugin, package, documentation, and examples are licensed
under the BSD-3 open source license at https://github.com/pr3d4t0r/sopel_ai/blob/master/LICENSE.txt.


See also
========
- Sopel AI API documentation at https://pr3d4t0r.github.io/sopel_ai
- PerplexiPy high level API interface to Perplexity AI https://pypi.org/project/perplexipy
- Sopel commands:  https://sopel.chat/usage/commands/
- Sopel bot home page:  https://sopel.chat/


Bugs
====
Feature requests and bug reports:

https://github.com/pr3d4t0r/sopel_ai/issues

