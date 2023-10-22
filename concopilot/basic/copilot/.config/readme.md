# basic-copilot

This is a general purposed Copilot framework design to adapt multiple tasks.

It is generally not necessary to change the framework or code of a Copilot,
just change its "config.yaml" by adding more necessary component or replacing existed components for specific tasks.

See the "config.yaml" for details.

## Framework

When an instance of this Copilot is created and run, it executes below tasks step by step:

1. `__init__`

   1. `resource_manager`:
      1. construct a Resource Manager according to the `resource_manager` section in the "config.yaml" file.
      2. construct all resources under the `resource_manager` section (**currently the resources are not initialized**)

   2. `storage`: construct the Storage for the Copilot memery according to the `storage` section in the "config.yaml" file.

   3. `user_interface`: construct the User Interface according to the `user_interface` section in the "config.yaml" file.

   4. `cerebrum`: construct the Cerebrum instance to take advantages from some LLM according to the `cerebrum` section in the "config.yaml" file.

   5. `plugin_manager`:
      1. construct a Plugin Manager according to the `plugin_manager` section in the "config.yaml" file.
      2. construct a Plugin Prompt Generator according to the `plugin_prompt_generator` section under the `plugin_manager` section in the "config.yaml" file.
      3. construct all plugins under the `plugin_manager` section (**currently the plugins are not initialized**)

   6. `message_manager`: construct a Message Manager according to the `message_manager` section in the "config.yaml" file.

   7. `interactor`: construct an Interactor according to the `interactor` section in the "config.yaml" file.
      the resource_manager, cerebrum, plugin_manager, and message_manager will be pass to the interactor since it is the central coordinator.

2. initialize

   1. initialize the `resource_manager`, and all resources under it.
      **The resources can only be used after this step.**

   2. config resources for all components.
      **A component can only access its necessary resources after this step.**

   3. config a context for the Copilot so that every component can access below resources by using its `self.context` field:
      1. `storage`
      2. `assets` (additional materials apart from chat histories to be passed to Cerebrum LLM to analysis if necessary)
      3. `user_interface`

   4. initialize interactor
      1. config general prompts by calling the `interactor.setup_prompts` method.
         This step is to config the general prompts for the interactor. Details will vary for different kinds of interactor.
      2. calling the `interactor.setup_plugins` method.
         This step is for configuring plugins after the prompts generation as well as pass all plugins to the cerebrum object for potential necessary initialization (such as the OpenAI function call).

3. **run interaction**: run the main task loop defined by the Interactor.

4. finalize: release/close all resources if necessary and exit the program.

## Config

1. `resource_manager`: Specify a Resource Manager to manager resources.
   Add all necessary resources under the resource manager config also.

2. `cerebrum`: Add a cerebrum component for task analysis.
   A cerebrum usually backed on a LLM to analyse user requirements and plugin information.

3. `interactor`: **This is the central part of a Copilot.**
   It controls the information dispatching, task coordinating, and function calls in a Copilot.
   Different task may need different "Interaction Framework".
   **Replace this component rather than the Copilot itself for specific tasks.**

4. `plugin_manager`: Specify a Plugin Manager to manager plugins.
   Add all necessary plugins under the plugin manager config also.

5. `message_manager`: Specify a Message Manager to deal with Cerebrum response.

6. `storage`: Specify this for the Copilot memory.

7. `user_interface`: Specify this to interact with users.

## Usage

Choose suitable component from our [website](https://concopilot.org) for your specific tasks,
and use them to modify the Copilot "config.yaml",
then use our `conpack` tool to run the Copilot.

Contribution to the Plugin Repository is highly welcome and encouraged.
Your contributions will benefit the world and make everyone be benefited by the development of ML and AI.
