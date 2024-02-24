# ConCopilot

<span style="font-size: 24px">**_Benefit everyone from AI & LLM_**</span>

ConCopilot is designed to **CON**nect all **COPILOT**s by making "_functional parts_" **reusable**, **replaceable**, **portable**, and **flexible**, aiming to leverage all potential tasks by AI & LLM.

ConCopilot defines standards and common interfaces that would be helpful to make each part of a copilot **reusable**, **replaceable**, **portable**, and **flexible**.
Any contributions that can improve these features are welcome.

Other than that, ConCopilot do **NOT** provide specific implementation nor developing constrains to developers.
Instead, ConCopilot fully leave these freedom to developers and users.
Every component and configs can be changed during both developing and using,
and it is welcome to upload those new components into our repository so that others can be benefited from.

## Why ConCopilot

**_Based on Plugins, Driven by Messages_**

1. Everything can be a **Plugin**, connect everything to AI & LLM by **Messages**.
2. **General LLM Interface** and seamlessly LLM replacement.
3. **Decouple Businesses from Plugins and LLMs.**
4. **Decouple Plugins from Copilots, LLMs, and Resources.**
5. Component package management.
6. Convenient and Easy for Community to contribute.
7. Free and flexible in application developments.
8. Friendly to other developing tools.
9. Simple for end users.

**ConCopilot vs. LangChain vs. AutoGPT**

In one word, LangChain is a developing tools for LLM applications,
AutoGPT is one of those applications,
and ConCopilot defines standards and common interfaces to help application developers and end users to deal with components easily,
as well as to help products and services connect to LLMs.

As a result, using tools like LangChain, following ConCopilot interface, developing products like AutoGPT, benefit people around the world. 😆

## Resources

[Website](https://concopilot.org)
<br>
[GitHub](https://github.com/ConCopilot/concopilot)
<br>
[Documents](https://concopilot.readthedocs.io)

Please note that ConCopilot do **NOT** take the responsibility of any malicious and abuse of components.

## Example

See example source codes and configs [here](https://github.com/ConCopilot/concopilot-examples).

### Installation

```shell
pip install --upgrade concopilot
```

### For end users

#### Run a developed Copilot task

1. Find the Copilot information (group_id, artifact_id, and version) from this website.
2. Run the Copilot:

    ```shell
    conpack run
            --group-id=<copilot_group_id>
            --artifact-id=<copilot_artifact_id>
            --version=<copilot_version>
            # --config-file=<your_downloaded_file_path>
            # --working-directory=<your_working_directory>
    ```

##### Quick examples

You may like to download the config files and modify some parameters first, such as API keys, service ports, etc.
Run `conpack build` first, and then find the corresponding `config.yaml` file from the ".runtime" folder.
The directory path is composed by the components `group_id`, `artifact_id`, and `version`.

1. Simple Chat:

    ```shell
    conpack run
            --group-id=org.concopilot.example.copilot
            --artifact-id=basic-chat-copilot
            --version=<version>
            # --config-file=<config.yaml|config_glm.yaml|config_rwkv.yaml|config_web.yaml|config_web_glm.yaml|config_web_rwkv.yaml>
            # --working-directory=<your_working_directory>
            # --skip-setup
    ```

    [latest version](https://concopilot.org/component/org.concopilot.example.copilot/basic-chat-copilot)

    [component source](https://github.com/ConCopilot/concopilot-examples/blob/main/concopilot_examples/copilot/chat)

2. Chat with Tools:

    ```shell
    conpack run
            --group-id=org.concopilot.example.copilot
            --artifact-id=basic-chat-with-tool-copilot
            --version=<version>
            # --config-file=<config.yaml|config_ocr.yaml|config_ocr_glm.yaml>
            # --working-directory=<your_working_directory>
            # --skip-setup
    ```

    [latest version](https://concopilot.org/component/org.concopilot.example.copilot/basic-chat-with-tool-copilot)

    [component source](https://github.com/ConCopilot/concopilot-examples/blob/main/concopilot_examples/copilot/chatwithtool)

3. Simplified Auto-GPT like:

    ```shell
    conpack run
            --group-id=org.concopilot.example.copilot
            --artifact-id=basic-auto-copilot
            --version=<version>
            # --config-file=<config.yaml|config_web.yaml>
            # --working-directory=<your_working_directory>
            # --skip-setup
    ```

    [latest version](https://concopilot.org/component/org.concopilot.example.copilot/basic-auto-copilot)

    [component source](https://github.com/ConCopilot/concopilot-examples/blob/main/concopilot_examples/copilot/auto)

### For developers

#### Develop a Plugin

1. Directory structure

    ```
    root
    |-- .config
    |    |-- config.yaml
    |    |-- ... (other config files)
    |
    |-- __init__.py (expose a "constructor" method to construct your plugin)
    |-- ...
    ```

2. Extend `AbstractPlugin` for your plugin, and implement
    - the `__init__` method which receives only one `dict` parameter containing its configuration.
    - the `command` method which receives a command name `string` and a parameter (recommends in type `dict`) and returns its response (recommends in type `dict`, too).

    ```python
    from concopilot.framework.plugin import AbstractPlugin


    class YourPlugin(AbstractPlugin):
        def __init__(self, config: Dict):
            super(YourPlugin, self).__init__(config)
            # ...

        def command(self, command_name: str, param: Any, **kwargs) -> Any:
            # ...
    ```

3. Edit your plugin `config.yaml` under the `.config` folder. Don't forget to fill the `setup` section:

    ```yaml
    # in your plugin's config.yaml

    group_id: <group_id>
    artifact_id: <artifact_id>
    version: <version>

    # ...

    setup:
      pip:
        - <your_python_package>
      package: <package_of_the__init__py>

    #...
    ```

4. Edit the `__init__.py` in the package to expose a "constructor" method for plugin initialization like below:

    ```python
    from typing import Dict

    from your.plugin.package import YourPlugin


    def constructor(config: Dict):
        return YourPlugin(config)


    __all__=[
        'constructor'# Please make sure the method name is exactly "constructor"
    ]
    ```

5. Deploy your python package.

6. Deploy your plugin into our Plugin Repository so that others can use it:

    ```shell
    conpack deploy
            # --src-folder=<your_source_folder>
    ```

#### Develop a Copilot

1. Build the directory structure just the same as if you are developing a Plugin.

2. Generally there's no need to extend the `Copilot` interface, extend the `Interactor` instead.

    ```python
    from concopilot.framework.interactor import BasicInteractor


    class YourInteractor(BasicInteractor):
        def __init__(
            self,
            config: Dict,
            resource_manager: ResourceManager,
            cerebrum: Cerebrum,
            plugin_manager: PluginManager,
            message_manager: MessageManager
        ):
            super(BasicInteractor, self).__init__(
                config,
                resource_manager,
                cerebrum,
                plugin_manager,
                message_manager
            )
            # ...
    ```

3. Edit your interactor `config.yaml` under the `.config` folder. Don't forget to fill the `setup` section as developing a plugin.

4. Edit the `__init__.py` in the package to expose a "constructor" method for plugin initialization like below:

    ```python
    from typing import Dict

    from your.interactor.package import YourInteractor


    def constructor(config: Dict):
        return YourInteractor(config)


    __all__=[
        'constructor'# Please make sure the method name is exactly "constructor"
    ]
    ```

5. Modify the Copilot `config.yaml` with your own `Interactor` and run the Copilot to test

    ```yaml
    group_id: org.concopilot.basic.copilot
    artifact_id: basic-copilot
    version: <basic_copilot_version>

    type: copilot
    as_plugin: false

    # ...

    interactor:
      group_id: <your_interactor_group_id>
      artifact_id: <your_interactor_artifact_id>
      version: <your_interactor_version>
      config:
        # ...

    # ...
    ```

6. Deploy your python package.

7. Deploy your interactor into our Plugin Repository so that others can use it

    ```shell
    conpack deploy
            # --src-folder=<your_source_folder>
    ```
