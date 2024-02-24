# -*- coding: utf-8 -*-

import abc
import uuid
import os

from typing import Dict, List, Union, Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from ..resource import Resource, ResourceManager
    from ...util.context import Context
from ..message import Message
from ...util.identity import Identity
from ...util import ClassDict
from ...package.config import Settings


settings=Settings()


class Plugin(metaclass=abc.ABCMeta):
    """
    The ConCopilot Plugin interface.

    Do not do any resource initialization/finalization here,
    do those in Resources and register the resource configs here.
    """

    @abc.abstractmethod
    def __init__(self, config: Dict):
        """
        Configure the Plugin without initialization.

        All necessary framework references are configure here,
        but the resources are not initialized.

        :param config: configures read from its config file (default to "config.yaml")
        """
        pass

    @abc.abstractmethod
    def config_resources(self, resource_manager: 'ResourceManager'):
        """
        Configure the plugin resources from the `resource_manager`.

        Only the resources that are configured in both the plugin and the `resource_manager`'s "config.yaml" are valid.

        :param resource_manager: the resource manager that manages the resource.
        """
        pass

    @abc.abstractmethod
    def config_context(self, context: 'Context'):
        """
        Configure the context for this plugin, and for all components under this plugin if necessary.

        :param context: the input context.
        """
        pass

    @abc.abstractmethod
    def config_file_path(self, file_name: str = None) -> str:
        """
        Return the config file path with the given `file_name` of this plugin.

        The config file here is a general concept that indicates any file that is related to this plugin and has been pushed into the component repo.

        This method does not check the file existence.

        :param file_name: the file name of the config file. `None` for the default "config.yaml".
        :return: the file path of the specific file.
        """
        pass

    @property
    @abc.abstractmethod
    def config(self) -> ClassDict:
        """
        Get the configures of this plugin.

        The returned config has the same structure of the plugin's "config.yaml".

        :return: the plugin `config` attribute.
        """
        pass

    @property
    @abc.abstractmethod
    def group_id(self) -> str:
        """
        :return: the plugin group id
        """
        pass

    @property
    @abc.abstractmethod
    def artifact_id(self) -> str:
        """
        :return: the plugin artifact id
        """
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        """
        :return: the plugin version
        """
        pass

    @property
    @abc.abstractmethod
    def id(self) -> Union[uuid.UUID, str, int]:
        """
        :return: the plugin id
        """
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        :return: the plugin name
        """
        pass

    @property
    @abc.abstractmethod
    def type(self) -> str:
        """
        :return: the plugin type (the "type" field in the "config.yaml")
        """
        pass

    @property
    @abc.abstractmethod
    def as_plugin(self) -> bool:
        """
        :return: the plugin's "as_plugin" attribute (the "as_plugin" field in the "config.yaml")
        """
        pass

    @property
    @abc.abstractmethod
    def resources(self) -> List['Resource']:
        """
        :return: the plugin resource list
        """
        pass

    @property
    @abc.abstractmethod
    def resource_id_map(self) -> Dict[Union[uuid.UUID, str, int], 'Resource']:
        """
        :return: the plugin resource map arranged by the resource id
        """
        pass

    @property
    @abc.abstractmethod
    def resource_name_map(self) -> Dict[str, 'Resource']:
        """
        :return: the plugin resource map arranged by the resource name
        """
        pass

    @property
    @abc.abstractmethod
    def resource_type_map(self) -> Dict[str, List['Resource']]:
        """
        :return: the plugin resource map arranged by the resource type
        """
        pass

    @abc.abstractmethod
    def get_resource(self, *, resource_id: str = None, resource_name: str = None, resource_type: str = None) -> Optional['Resource']:
        """
        Retrieve a resource with its resource id, resource name, and resource_type.

        if the `resource_id` is "default", it will be ignored.

        If the `resource_type` is provided alone, the first resource with the given resource type will be returned.

        :param resource_id: the resource id
        :param resource_name: the resource name
        :param resource_type: the resource type
        :return: the resource found or None
        """
        pass

    @property
    @abc.abstractmethod
    def context(self) -> 'Context':
        """
        :return: the plugin context
        """
        pass

    @abc.abstractmethod
    def command(self, command_name: str, param: Any, **kwargs) -> Any:
        """
        The raw (without message encapsulation) plugin command execution interface.

        Implement this method if the component is supposed to be a real full functional plugin.

        :param command_name: the command name to call
        :param param: the command parameter
        :param kwargs: reserved, not recommend to use
        :return: the command response
        """
        pass

    @abc.abstractmethod
    def send_msg(self, msg: Message):
        """
        Send a message to this plugin.

        The `command` method will be called to run the command in the `msg` content.

        :param msg: the message to be sent
        """
        pass

    @abc.abstractmethod
    def on_msg(self, msg: Message) -> Message:
        """
        Send a message to this plugin and waiting for a response.

        The `command` method will be called to run the command in the `msg` content.

        :param msg: the message to be sent
        :return: the response message
        """
        pass

    @abc.abstractmethod
    def has_msg(self) -> bool:
        """
        Check if the plugin has a message to be sent out.
        Call the `get_msg` method to retrieve the message if this method returns `True`.

        :return: True if it has, False if it hasn't
        """
        pass

    @abc.abstractmethod
    def get_msg(self) -> Optional[Message]:
        """
        :return: the first message this plugin is about to send or None
        """
        pass

    @property
    @abc.abstractmethod
    def prompt(self) -> str:
        """
        The plugin prompt provided to the Cerebrum to interact with LLM.

        :return: the plugin prompt string if any or None
        """
        pass

    @prompt.setter
    @abc.abstractmethod
    def prompt(self, value: str):
        """
        The setter of the plugin prompt.

        :param value: the value of the plugin prompt
        """
        pass


class AbstractPlugin(Plugin, metaclass=abc.ABCMeta):
    def __init__(self, config: Dict):
        super(AbstractPlugin, self).__init__(config)
        self._config=ClassDict.convert(config)
        self._group_id=str(self.config.group_id).lower()
        self._artifact_id=str(self.config.artifact_id).lower()
        self._version=str(self.config.version).lower()

        if self.config.config.id and self.config.config.id!='default':
            self._id=self.config.config.id
        else:
            self._id=uuid.uuid4()
        if self.config.config.name:
            self._name=self.config.config.name
        elif self.config.name:
            self._name=self.config.name
        elif self.config.info is not None and self.config.info.title:
            self._name=self.config.info.title
        else:
            self._name=None
        self._type=str(self.config.type).lower()
        if not isinstance(self.config.as_plugin, bool):
            if isinstance(self.config.as_plugin, int):
                self.config.as_plugin=self.config.as_plugin!=0
            else:
                self.config.as_plugin=str(self.config.as_plugin).lower()=='true'
        self._as_plugin=self.config.as_plugin

        self._resources: List[Resource] = []
        self._resource_id_map: Dict[Union[uuid.UUID, str, int], Resource] = {}
        self._resource_name_map: Dict[str, Resource] = {}
        self._resource_type_map: Dict[str, List[Resource]] = {}

        self._context: Context = None

        self._prompt: str = ''
        if self.config.as_plugin:
            assert self.name is not None and len(self.name)>0
            if self.config.info.prompt is not None and isinstance(self.config.info.prompt, str):
                self.prompt=self.config.info.prompt
            elif self.config.info.prompt_file_name is not None and isinstance(self.config.info.prompt_file_name, str):
                with open(self.config_file_path(self.config.info.prompt_file_name), encoding='utf8') as file:
                    self.prompt=file.read()
            elif self.config.info.prompt_file_path is not None and isinstance(self.config.info.prompt_file_path, str):
                with open(self.config.info.prompt_file_path, encoding='utf8') as file:
                    self.prompt=file.read()

    def config_resources(self, resource_manager: 'ResourceManager'):
        self._resources=[]
        if resource_manager is None:
            raise ValueError('No resource_manager passed.')
        if self.config.resources is not None:
            for resource_config in self.config.resources:
                self._config_one_resource(resource_config, resource_manager)
        if self.config.config.resources is not None:
            for resource_config in self.config.config.resources:
                self._config_one_resource(resource_config, resource_manager)

    def _config_one_resource(self, resource_config, resource_manager: 'ResourceManager'):
        resource=resource_manager.get_resource(resource_id=resource_config.id, resource_name=resource_config.name, resource_type=resource_config.type)
        if resource is None:
            raise ValueError(f'No such resource found. resource_id={resource_config.id}, resource_type={resource_config.type}')
        if resource.id in self.resource_id_map:
            existed=self.resource_id_map[resource.id]
            raise ValueError(f'\
                Resource with id={resource.id} already existed.\
                \n    Existed: ({existed.group_id}, {existed.artifact_id}, {existed.version})\
                \n    Current: ({resource.group_id}, {resource.artifact_id}, {resource.version})\
            ')
        if resource.name in self.resource_name_map:
            existed=self.resource_name_map[resource.name]
            raise ValueError(f'\
                Resource with name={resource.name} already existed.\
                \n    Existed: ({existed.group_id}, {existed.artifact_id}, {existed.version})\
                \n    Current: ({resource.group_id}, {resource.artifact_id}, {resource.version})\
            ')
        self.resources.append(resource)
        self.resource_id_map[resource.id]=resource
        if resource.name is not None and len(resource.name)>0:
            self.resource_name_map[resource.name]=resource
        if resource.resource_type not in self.resource_type_map:
            self.resource_type_map[resource.resource_type]=[]
        self.resource_type_map[resource.resource_type].append(resource)

    def config_context(self, context: 'Context'):
        self._context=context

    def config_file_path(self, file_name: str = None) -> str:
        return os.path.join(self.config._config_info.config_folder, file_name if file_name else self.config._config_info.config_file)

    @property
    def config(self) -> ClassDict:
        return self._config

    @property
    def group_id(self) -> str:
        return self._group_id

    @property
    def artifact_id(self) -> str:
        return self._artifact_id

    @property
    def version(self) -> str:
        return self._version

    @property
    def id(self) -> Union[uuid.UUID, str, int]:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> str:
        return self._type

    @property
    def as_plugin(self) -> bool:
        return self._as_plugin

    @property
    def resources(self) -> List['Resource']:
        return self._resources

    @property
    def resource_id_map(self) -> Dict[Union[uuid.UUID, str, int], 'Resource']:
        return self._resource_id_map

    @property
    def resource_name_map(self) -> Dict[str, 'Resource']:
        return self._resource_name_map

    @property
    def resource_type_map(self) -> Dict[str, List['Resource']]:
        return self._resource_type_map

    def get_resource(self, *, resource_id: Union[uuid.UUID, str, int] = None, resource_name: str = None, resource_type: str = None) -> Optional['Resource']:
        if resource_id and str(resource_id).lower()!='default':
            resource=self.resource_id_map.get(resource_id)
            if resource:
                if resource_name and resource.name!=resource_name:
                    return None
                if resource_type and resource.resource_type!=resource_type:
                    return None
            return resource
        elif resource_name:
            resource=self.resource_name_map.get(resource_name)
            if resource and resource_type and resource.resource_type!=resource_type:
                return None
            return resource
        elif resource_type and resource_type in self.resource_type_map:
            return self.resource_type_map.get(resource_type)[0]
        else:
            return None

    @property
    def context(self) -> 'Context':
        return self._context

    def send_msg(self, msg: Message):
        self.on_msg(msg)

    def on_msg(self, msg: Message) -> Message:
        if not msg.receiver:
            raise ValueError('No message receiver!')
        if msg.receiver.role!='plugin' and msg.receiver.role!=self.type:
            if self.type=='plugin':
                raise ValueError(f'Not a message to plugin! msg.receiver.role is `{msg.receiver.role}`, must be "plugin".')
            else:
                raise ValueError(f'Not a message to plugin or plugin type! The `msg.receiver.role` is "{msg.receiver.role}", must be "plugin" or "{self.type}".')
        if self.id!=msg.receiver.id and self.name!=msg.receiver.name:
            raise ValueError(f'Incorrect message receiver! Message expect (id="{msg.receiver.id}" name="{msg.receiver.name}"), plugin is (id="{self.id}" name="{self.name}").')
        if msg.content_type!='command':
            raise ValueError('Not a command message! The `msg.content_type` must be "command".')
        if not msg.content:
            raise ValueError('No message content!')
        if not msg.content.command:
            raise ValueError('Message content contains NO plugin command! `msg.content.command` must be set.')

        msg=Message(
            sender=Identity(role=msg.receiver.role, id=self.id, name=self.name),
            receiver=msg.sender,
            content_type='command',
            content=Message.Command(
                command=msg.content.command,
                response=self.command(msg.content.command, msg.content.param if msg.content.param else ClassDict())
            ),
            time=settings.current_time()
        )
        return msg

    def has_msg(self) -> bool:
        return False

    def get_msg(self) -> Optional[Message]:
        return None

    @property
    def prompt(self) -> str:
        return self._prompt

    @prompt.setter
    def prompt(self, value: str):
        self._prompt=value
