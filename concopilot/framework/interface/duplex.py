# -*- coding: utf-8 -*-

import uuid
import queue
import threading

from typing import Dict, Optional

from .interface import UserInterface
from ..message import Message
from ...util.interruptable_queue import InterruptableQueue


class BasicDuplexUserInterface(UserInterface):
    def __init__(self, config: Dict):
        super(BasicDuplexUserInterface, self).__init__(config)
        self._user_msg_queue: InterruptableQueue = InterruptableQueue(interrupt_checking_timeout=self.config.config.interrupt_checking_timeout)
        self._agent_msg_queue: InterruptableQueue = InterruptableQueue(interrupt_checking_timeout=self.config.config.interrupt_checking_timeout)
        self._user_msg_cache=[]
        self._agent_msg_cache=[]
        self._user_msg_lock: threading.RLock = threading.RLock()
        self._agent_msg_lock: threading.RLock = threading.RLock()

    def send_msg_to_user(self, msg: Message):
        self._agent_msg_queue.put(msg)

    def on_msg_to_user(self, msg: Message) -> Optional[Message]:
        if not msg.thrd_id:
            msg=Message(**msg)
            msg.thrd_id=str(uuid.uuid4())
        thrd_id=msg.thrd_id
        self.send_msg_to_user(msg)
        cache=[]
        with self._user_msg_lock:
            while msg:=self.wait_user_msg():
                if msg.thrd_id==thrd_id:
                    self._user_msg_cache.extend(cache)
                    return msg
                else:
                    cache.append(msg)

    def has_user_msg(self) -> bool:
        with self._user_msg_lock:
            return len(self._user_msg_cache)>0 or self._user_msg_queue.qsize()>0

    def get_user_msg(self) -> Optional[Message]:
        with self._user_msg_lock:
            if len(self._user_msg_cache)>0:
                return self._user_msg_cache.pop(0)
            else:
                try:
                    return self._user_msg_queue.get_nowait()
                except queue.Empty:
                    return None

    def wait_user_msg(self) -> Optional[Message]:
        with self._user_msg_lock:
            if len(self._user_msg_cache)>0:
                return self._user_msg_cache.pop(0)
            else:
                return self._user_msg_queue.get()

    def send_msg_to_agent(self, msg: Message):
        self._user_msg_queue.put(msg)

    def on_msg_to_agent(self, msg: Message) -> Optional[Message]:
        if not msg.thrd_id:
            msg=Message(**msg)
            msg.thrd_id=str(uuid.uuid4())
        thrd_id=msg.thrd_id
        self.send_msg_to_agent(msg)
        cache=[]
        with self._agent_msg_lock:
            while msg:=self.wait_agent_msg():
                if msg.thrd_id==thrd_id:
                    self._agent_msg_cache.extend(cache)
                    return msg
                else:
                    cache.append(msg)

    def has_agent_msg(self) -> bool:
        with self._agent_msg_lock:
            return len(self._agent_msg_cache)>0 or self._agent_msg_queue.qsize()>0

    def get_agent_msg(self) -> Optional[Message]:
        with self._agent_msg_lock:
            if len(self._agent_msg_cache)>0:
                return self._agent_msg_cache.pop(0)
            else:
                try:
                    return self._agent_msg_queue.get_nowait()
                except queue.Empty:
                    return None

    def wait_agent_msg(self) -> Optional[Message]:
        with self._agent_msg_lock:
            if len(self._agent_msg_cache)>0:
                return self._agent_msg_cache.pop(0)
            else:
                return self._agent_msg_queue.get()

    def interrupt(self):
        self._user_msg_queue.interrupt()
        self._agent_msg_queue.interrupt()

    @property
    def interrupted(self) -> bool:
        return self._user_msg_queue.interrupted or self._agent_msg_queue.interrupted
