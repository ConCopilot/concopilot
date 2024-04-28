# -*- coding: utf-8 -*-

import json
import re
import regex
import uuid
import logging

from typing import List, Dict, Tuple, Any, Union, Optional

from .....framework.message import Message
from .....framework.message.manager import MessageManager
from .....framework.cerebrum import InteractResponse
from .....framework.identity import Identity
from .....package.config import Settings


settings=Settings()
logger=logging.getLogger(__file__)


class BasicJsonMessageManager(MessageManager):
    def __init__(self, config: Dict):
        super(BasicJsonMessageManager, self).__init__(config)

    def parse(self, response: InteractResponse, thrd_id: Union[uuid.UUID, str, int] = None) -> List[Message]:
        msg_list=[]
        if response.content:
            try:
                reply=fix_json_using_multiple_techniques(response.content)
                if isinstance(reply, List):
                    for item in reply:
                        msg_list.append(BasicJsonMessageManager.parse_as_msg(item, thrd_id=thrd_id))
                else:
                    msg_list.append(BasicJsonMessageManager.parse_as_msg(reply, thrd_id=thrd_id))
            except Exception as e:
                logger.warning('response.content parse failed!', exc_info=e)
                msg_list.append(Message(content=response.content, thrd_id=thrd_id))
        if response.plugin_calls:
            for plugin_call in response.plugin_calls:
                content=Message.Command(**plugin_call)
                msg_list.append(Message(
                    receiver=Identity(
                        role='plugin',
                        name=content.pop('plugin_name', None)
                    ),
                    content_type='command',
                    content=content,
                    time=settings.current_time(),
                    thrd_id=thrd_id
                ))
        return msg_list

    @staticmethod
    def parse_as_msg(item: Any, thrd_id: Union[uuid.UUID, str, int] = None):
        sender=None
        receiver=None
        content_type=None
        time=None
        if isinstance(item, Dict):
            sender=item.pop('sender', None)
            receiver=item.pop('receiver', None)
            content_type=item.pop('content_type', None)
            content=item.pop('content', None)
            time=item.pop('time', None)
        else:
            content=item
            item={}
        msg=Message(
            sender=sender,
            receiver=receiver,
            content_type=content_type,
            content=content,
            time=time if time else settings.current_time(),
            thrd_id=thrd_id,
            **item
        )
        if msg.content_type is None and msg.content.command:
            msg.content_type='command'
        return msg

    def command(self, command_name: str, param: Any, **kwargs) -> Any:
        return {}


def get_md_json_string(json_string: str) -> str:
    json_string.strip()
    if json_string.startswith('```json'):
        json_string=json_string[7:].strip()
    if json_string.endswith('```'):
        json_string=json_string[:-3].strip()
    return json_string


def get_json_prefix_json_string(json_string: str) -> str:
    json_string.strip()
    if json_string.startswith('json '):
        json_string=json_string[5:].strip()
    return json_string


def get_outermost_balanced_braces_json_string(json_string: str) -> str:
    match=regex.compile(r'\{(?:[^{}]|(?R))*\}').search(json_string)
    if match:
        return match.group(0)


def invalid_escape_json_parser(json_string: str, error: Exception = None) -> Tuple[Any, str, Optional[Exception]]:
    if error is None:
        try:
            return json.loads(json_string), json_string, None
        except json.JSONDecodeError as e:
            error=e
    error_message=str(error)
    while error_message.startswith('Invalid \\escape'):
        match=re.compile(r'\(char (\d+)\)').search(error_message)
        bad_escape_location=int(match[1])
        json_string=json_string[:bad_escape_location]+json_string[bad_escape_location+1:]
        try:
            return json.loads(json_string), json_string, None
        except json.JSONDecodeError as e:
            error=e
            error_message=str(error)
    return None, json_string, error


def missing_quotes_json_parser(json_string: str, error: Exception = None) -> Tuple[Any, str, Optional[Exception]]:
    if error is None:
        try:
            return json.loads(json_string), json_string, None
        except json.JSONDecodeError as e:
            error=e
    if str(error).startswith('Expecting property name enclosed in double quotes'):
        json_string=re.compile(r'([,{\[]+\s*|^)"?(\w+)"?:').sub(lambda m : f'{m[1]}"{m[2]}":', json_string)

        try:
            return json.loads(json_string), json_string, None
        except json.JSONDecodeError as e:
            error=e
    return None, json_string, error


def imbalance_braces_json_parser(json_string: str, error: Exception = None) -> Tuple[Any, str, Optional[Exception]]:
    open_braces_count=json_string.count('{')
    close_braces_count=json_string.count('}')

    if open_braces_count!=close_braces_count:
        while open_braces_count>close_braces_count:
            json_string+='}'
            close_braces_count+=1

        while close_braces_count>open_braces_count:
            json_string='{'+json_string
            open_braces_count+=1

        try:
            return json.loads(json_string), json_string, None
        except json.JSONDecodeError as e:
            error=e
    elif error is None:
        try:
            return json.loads(json_string), json_string, None
        except json.JSONDecodeError as e:
            error=e
    return None, json_string, error


def brace_finder_json_parser(json_string: str, error: Exception = None) -> Tuple[Any, str, Optional[Exception]]:
    try:
        brace_index=json_string.index('{')
        json_string=json_string[brace_index:]
        last_brace_index=json_string.rindex('}')
        json_string=json_string[:last_brace_index+1]
        return json.loads(json_string), json_string, None
    except (json.JSONDecodeError, ValueError) as e:
        return None, json_string, e


def fix_and_parse_json(json_string) -> Tuple[Any, str, Optional[Exception]]:
    json_parser=[
        invalid_escape_json_parser,
        missing_quotes_json_parser,
        imbalance_braces_json_parser,
        brace_finder_json_parser
    ]
    json_obj=None
    error=None
    for parser in json_parser:
        json_obj, json_string, error=parser(json_string, error)
        if json_obj is not None:
            break
    return json_obj, json_string, error


def fix_json_using_multiple_techniques(json_string: str) -> Any:
    json_string_parser=[
        lambda json_string : get_json_prefix_json_string(get_md_json_string(json_string)),
        get_outermost_balanced_braces_json_string
    ]
    error=None
    for parser in json_string_parser:
        json_obj, json_string, error=fix_and_parse_json(parser(json_string))
        if json_obj is not None:
            return json_obj
    raise error
