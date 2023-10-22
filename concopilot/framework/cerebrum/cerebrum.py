# -*- coding: utf-8 -*-

import abc

from typing import Dict, List

from ..plugin import AbstractPlugin, PluginManager
from ..resource.category import LLM
from ..message import Message
from ...util.context import Asset
from ...util import ClassDict


class InteractParameter(ClassDict):
    def __init__(self, instructions: List[str] = None, command: str = None, message_history: List[Message] = None, assets: List[Asset] = None, content: str = None, require_token_len: bool = None, require_cost: bool = None, **kwargs):
        super(InteractParameter, self).__init__(**kwargs)
        self.instructions: List[str] = instructions
        self.command: str = command
        self.message_history: List[Message] = message_history
        self.assets: List[Asset] = assets
        self.content: str = content

        self.require_token_len: bool = require_token_len
        self.require_cost: bool = require_cost


class InteractResponse(ClassDict):
    class PluginCall(ClassDict):
        def __init__(self, plugin_name: str, command: str, param: Dict, **kwargs):
            super(InteractResponse.PluginCall, self).__init__(**kwargs)
            self.plugin_name: str = plugin_name
            self.command: str = command
            self.param: ClassDict = ClassDict.convert(param)

    def __init__(self, content: str = None, plugin_call: PluginCall = None, input_token_len: int = None, output_token_len: int = None, cost: float = None, **kwargs):
        super(InteractResponse, self).__init__(**kwargs)
        self.content: str = content
        self.plugin_call: InteractResponse.PluginCall = plugin_call

        self.input_token_len: int = input_token_len
        self.output_token_len: int = output_token_len
        self.cost: float = cost


class Cerebrum(AbstractPlugin):
    """
    A Cerebrum act like a human brain and interact user requirements and plugins with an LLM.

    It translates the incoming common copilot data, the `InteractParameter`, into what a specific LLM can understand,
    and translates the LLM response to the common `InteractResponse`.
    """

    def __init__(self, config: Dict):
        """
        Configure the Cerebrum without initialization.

        Make sure the `type` in the config file is set to "cerebrum".

        :param config: configures read from its config file (default to "config.yaml")
        """
        super(Cerebrum, self).__init__(config)
        assert self.type=='cerebrum'

    @property
    @abc.abstractmethod
    def role(self) -> str:
        pass

    @role.setter
    @abc.abstractmethod
    def role(self, value: str):
        pass

    @abc.abstractmethod
    def setup_plugins(self, plugin_manager: PluginManager):
        """
        This method will be called by the Interactor to expose the plugin_manager (and all plugins in it) to the cerebrum.

        Special work can be done here with the plugins, such as config OpenAI function call from plugins, if necessary.

        :param plugin_manager: the plugin manager
        """
        pass

    @property
    @abc.abstractmethod
    def model(self) -> LLM:
        """
        Return the backed LLM.

        Retrieve the LLM from the plugin's resource list for convenient use.

        :return: the backed LLM
        """
        pass

    @abc.abstractmethod
    def interact(self, param: InteractParameter, **kwargs) -> InteractResponse:
        """
        This method will be called by the Interactor to interact copilot materials (`InteractParameter`) with the backed LLM.

        A standard `InteractResponse` object will be constructed and returned to the Interactor by reading the LLM response,
        so that the Interactor and other parts of the copilot need not know any detail of the LLM.

        :param param: the InteractParameter object contains the interacting information from the copilot working flow
        :param kwargs: reserved, not recommend to use
        :return: the InteractResponse contains the LLM response
        """
        pass

    def command(self, command_name: str, param: Dict, **kwargs) -> Dict:
        return {}


class AbstractCerebrum(Cerebrum, metaclass=abc.ABCMeta):
    def __init__(self, config: Dict):
        super(AbstractCerebrum, self).__init__(config)
        self._role=self.config.config.role

    @property
    def role(self) -> str:
        return self._role

    @role.setter
    def role(self, value: str):
        self._role=value
