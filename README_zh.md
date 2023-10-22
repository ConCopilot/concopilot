# ConCopilot

<span style="font-size: 24px">**_让所有人受益于人工智能（AI）和大语言模型（LLM）_**</span>

ConCopilot的设计理念为连接所有AI副官（**CON**nect all **COPILOT**s），将所有“_功能性部分_”变得**可复用**，**可替换**，**可移植**，**够灵活**，让所有潜在的任务都能受益于AI和LLM。

ConCopilot为有可能使组成AI副官的部件变得**可复用**，**可替换**，**可移植**，**够灵活**的部分定义了通用标准和接口。
我们同时也欢迎一切能提升这些特性的代码贡献。

除了这些理念以外，ConCopilot并不提供任何特定的实现范式或对开发者进行开发限制。
相反，ConCopilot将这些完全自由的暴露给开发者和用户。
在开发和使用过程中，任何组件和配置均可被修改，
并且我们非常欢迎开发者上传这些新功能到我们的组件仓库使得更多人能够收益。

## 为什么需要ConCopilot

**_以插件（Plugin）为基础，用消息（Message）来驱动_**

1. 一切皆**插件**，用**消息**将一切连接到AI和LLM。
2. **通用LLM接口**和LLM无缝替换。
3. **解耦业务，插件，和LLM。**
4. **解耦插件与AI副官，LLM，和资源（Resources）。**
5. 组件包管理工具。
6. 方便简单的社区贡献方式。
7. 自由灵活的应用开发。
8. 对其它开发工具友好。
9. 简单的末端应用方式。

**ConCopilot vs. LangChain vs. AutoGPT**

简单来说，LangChain是LLM应用的开发工具，
AutoGPT其中一种应用，
而ConCopilot为应用开发者和末端用户定义了能让其方便并便捷替换应用组件的通用标准和接口，
以及帮助其产品服务连接到LLM的通用范式。

因此，使用像LangChain这样的开发工具，遵循ConCopilot的接口，开发如同AutoGPT这样的应用，让全世界都能够受益。😆

## 资源

[官网](https://concopilot.org)
<br>
[GitHub](https://github.com/ConCopilot/concopilot)
<br>
[文档](https://concopilot.readthedocs.io)

请注意，ConCopilot**不**对任何恶意或滥用组件负责。

## 例子

在[这里](https://github.com/ConCopilot/concopilot/tree/main/concopilot_examples)查看范例代码和配置。

### 安装

```shell
pip install --upgrade concopilot
```

### 对末端用户

#### 运行开发好的AI副官

1. 从本站搜索对应AI副官信息（group_id，artifact_id，version）。
2. 运行AI副官：

    ```shell
    conpack run
            --group-id=<copilot_group_id>
            --artifact-id=<copilot_artifact_id>
            --version=<copilot_version>
            # --config-file=<your_downloaded_file_path>
            # --working-directory=<your_working_directory>
    ```

##### 快速范例

1. 下载这个简化版的类Auto-GPT[副官范例](https://github.com/ConCopilot/concopilot/blob/main/concopilot_examples/config.yaml)。
2. 执行以下命令运行:

    ```shell
    conpack run
            --config-file=<your_downloaded_file_path>
            # --working-directory=<your_working_directory>
    ```

### 对开发者

#### 开发一个插件（Plugin）

1. 目录结构

    ```
    root
    |-- .config
    |    |-- config.yaml
    |    |-- ... (其它配置文件)
    |
    |-- __init__.py (在此暴露一个构建你的插件的"constructor"方法)
    |-- ...
    ```

2. 使你的插件继承自`AbstractPlugin`类，并实现以下方法
    - `__init__`方法，仅接收一个包含其所有配置信息的`dict`参数。
    - `command`方法，接收一个`string`类型的命令名参数（`command_name`），一个`dict`类型的命令参数参数（`param`），并返回一个`dict`类型的命令执行结果。

    ```python
    from concopilot.framework.plugin import AbstractPlugin


    class YourPlugin(AbstractPlugin):
        def __init__(self, config: Dict):
            super(YourPlugin, self).__init__(config)
            # ...

        def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
            # ...
    ```

3. 编辑该插件的`.config`目录下的`config.yaml`文件。别忘了填写其`setup`部分：

    ```yaml
    # 在你的插件对应的config.yaml文件中

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

4. 编辑代码包下的`__init__.py`文件，暴露一个叫做"constructor"的方法用于构建该插件，如下所示：

    ```python
    from typing import Dict

    from your.plugin.package import YourPlugin


    def constructor(config: Dict):
        return YourPlugin(config)


    __all__=[
        'constructor'# 请确保该方法名为"constructor"
    ]
    ```

5. 发布你的python代码包。

6. 将你的插件部署到插件仓库以便他人使用：

    ```shell
    conpack deploy
            # --src-folder=<your_source_folder>
    ```

#### 开发一个AI副官（Copilot）

1. 开发目录结构与开发插件时一致。

2. 通常不需要继承`Copilot`接口，继承`Interactor`即可。

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

3. 编辑该interactor的`.config`目录下的`config.yaml`文件。其`setup`部分的填写方式和开发插件时相同。

4. 编辑代码包下的`__init__.py`文件，暴露一个叫做"constructor"的方法用于构建该插件，如下所示：

    ```python
    from typing import Dict

    from your.interactor.package import YourInteractor


    def constructor(config: Dict):
        return YourInteractor(config)


    __all__=[
        'constructor'# 请确保该方法名为"constructor"
    ]
    ```

5. 将默认AI副官（Copilot）框架下的`config.yaml`文件中的对应配置修改为你的`Interactor`，然后运行并测试

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

6. 发布你的python代码包。

7. 将你的interactor部署到插件仓库以便他人使用：

    ```shell
    conpack deploy
            # --src-folder=<your_source_folder>
    ```
