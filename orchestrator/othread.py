import logging
import threading

from queue import Queue, Full, Empty
from typing import Dict, Any
from pydantic import BaseModel
from abc import ABC, abstractmethod


class Event(BaseModel):
    name: str
    detail: Dict[str, Any]


class OrchestrationObserver(ABC):
    @abstractmethod
    def event(self, evt: Event):
        pass


class OrchestrationQueue(ABC):
    queue: Queue

    @abstractmethod
    def __init__(self, name: str, internal_queue: Queue, observer: OrchestrationObserver):
        self.name = name
        self.observer = observer
        self.queue = internal_queue

    def add(self, message: Any):
        try:
            self.queue.put_nowait(message)
            self.observer.event(Event(name='queue.added', detail={'queue': self.name, 'message': message}))
        except Full:
            self.observer.event(Event(name='queue.discarded', detail={'queue': self.name, 'message': message}))

    def poll(self) -> Any or None:
        '''
        return consume() if there is a message in the queue, None otherwise
        '''
        try:
            return self._consume(block=False)
        except Empty:
            self.observer.event(Event(name='queue.polled_empty', detail={'queue': self.name}))
            return None

    def consume(self) -> Any:
        '''
        wait for queue to contain element, remove and return
        notify on consumption
        '''
        return self._consume(block=True)

    def qsize(self) -> int:
        return self.queue.qsize()

    def _consume(self, block: bool) -> Any:
        message = self.queue.get(block=block)
        self.observer.event(Event(name='queue.consumed', detail={'queue': self.name, 'message': message}))
        return message


class LimitlessOrchestrationQueue(OrchestrationQueue):
    def __init__(self, name: str, observer: OrchestrationObserver):
        super().__init__(self, name, Queue(maxsize=0), observer)


class LatestMessageOrchestrationQueue(OrchestrationQueue):
    def __init__(self, name: str, observer: OrchestrationObserver):
        super().__init__(self, name, Queue(maxsize=1), observer)


class OrchestrationThreadBase(threading.Thread):
    def __init__(self, host: str, port: int, servicename: str, rpcname: str):
        pass

    def attach_input_queue(self, q: OrchestrationQueue):
        '''
        connect input queue
        '''
        pass

    def attach_output_queue(self, q: OrchestrationQueue):
        '''
        connect output queue
        '''
        pass
