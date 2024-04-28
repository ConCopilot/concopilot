# -*- coding: utf-8 -*-

import queue
import threading


class InterruptableQueue(queue.Queue):
    def __init__(self, maxsize=0, interrupt_checking_timeout=None):
        super(InterruptableQueue, self).__init__(maxsize=maxsize)
        self._interrupt_checking_timeout=interrupt_checking_timeout if (interrupt_checking_timeout is not None and interrupt_checking_timeout>0) else 1
        self._interrupted: threading.Event = threading.Event()

    def put(self, item, block=True, timeout=None):
        if block==True and timeout is None:
            while not self.interrupted:
                try:
                    return super(InterruptableQueue, self).put(item, block=block, timeout=self._interrupt_checking_timeout)
                except queue.Full:
                    pass
            raise InterruptedError('InterruptableQueue.put has been interrupted.')
        elif not self.interrupted:
            return super(InterruptableQueue, self).put(item, block=block, timeout=self._interrupt_checking_timeout)
        else:
            raise InterruptedError('InterruptableQueue.put has been interrupted.')

    def get(self, block=True, timeout=None):
        if block==True and timeout is None:
            while not self.interrupted:
                try:
                    return super(InterruptableQueue, self).get(block=block, timeout=self._interrupt_checking_timeout)
                except queue.Empty:
                    pass
            raise InterruptedError('InterruptableQueue.get has been interrupted.')
        elif not self.interrupted:
            return super(InterruptableQueue, self).get(block=block, timeout=self._interrupt_checking_timeout)
        else:
            raise InterruptedError('InterruptableQueue.get has been interrupted.')

    def interrupt(self):
        self._interrupted.set()

    @property
    def interrupted(self) -> bool:
        return self._interrupted.is_set()
