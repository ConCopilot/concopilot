# -*- coding: utf-8 -*-

import abc

from typing import Dict

from ..plugin.plugin import Plugin, AbstractPlugin


class PluginPromptGenerator(AbstractPlugin):
    """
    Called by a Plugin Manager to generate prompts for plugins that the copilot may use.

    This is necessary because in many cases prompts varying with LLMs, but working flow remains unchanged.
    """

    def __init__(self, config: Dict):
        """
        Configure the PluginPromptGenerator without initialization.

        Make sure the `type` in the config file is set to "plugin_prompt_generator".

        :param config: configures read from its config file (default to "config.yaml")
        """
        super(PluginPromptGenerator, self).__init__(config)
        assert self.type=='plugin_prompt_generator'

    @abc.abstractmethod
    def generate_prompt(self, plugin: Plugin) -> str:
        """
        Generate a prompt for the passed plugin.

        :param plugin: the plugin that to be generated a prompt for
        :return: the generated prompt
        """
        pass

    def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
        return {}
