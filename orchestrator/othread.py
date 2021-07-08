import logging
import threading
import traceback
import grpc
import time

from queue import Queue, Full, Empty
from typing import Dict, Any
from pydantic import BaseModel
from abc import ABC, abstractmethod


def resolve_protobuf_message(message_name: str):
    # TODO generalize this
    import orchestrator_pb2
    return getattr(orchestrator_pb2, message_name)


def resolve_service_stub(service_name: str):
    import orchestrator_pb2_grpc
    return getattr(orchestrator_pb2_grpc, service_name + 'Stub')


class Event(BaseModel):
    name: str
    detail: Dict[str, Any]


class OrchestrationObserver(ABC):
    @abstractmethod
    def event(self, evt: Event):
        pass


class LoggingOrchestrationObserver(OrchestrationObserver):
    def event(self, evt: Event):
        shortdetail = {
            k: v
            for k, v in evt.detail.items()
            if k not in 'message'}
        messagedetail = ''
        if 'message' in evt.detail:
            messagedetail = ' (message length %d)' % len(str(evt.detail['message']))
        logging.info("Orchestration Event: %s %s%s", evt.name, shortdetail, messagedetail)


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
        super().__init__(name, Queue(maxsize=0), observer)


class LatestMessageOrchestrationQueue(OrchestrationQueue):
    def __init__(self, name: str, observer: OrchestrationObserver):
        super().__init__(name, Queue(maxsize=1), observer)


class OrchestrationThreadBase(threading.Thread):
    def __init__(
        self,
        host: str, port: int,
        servicename: str, rpcname: str,
        observer: OrchestrationObserver,
        empty_in: bool = False, empty_out: bool = False
    ):
        super().__init__(daemon=True)

        self.host = host
        self.port = port
        self.servicename = servicename
        self.rpcname = rpcname
        self.observer = observer
        self.empty_in = empty_in
        self.empty_out = empty_out

        self.input_queue = None
        self.output_queue = None

    def _event(self, name: str, detail: dict):
        extended_detail = detail | {
            'source': str(self)
        }
        self.observer.event(Event(
            name=name,
            detail=extended_detail))

    def attach_input_queue(self, q: OrchestrationQueue):
        '''
        connect input queue
        '''
        if self.input_queue is not None:
            raise RuntimeError("cannot attach two input queues to thread " + str(self))
        self.input_queue = q

    def attach_output_queue(self, q: OrchestrationQueue):
        '''
        connect output queue
        '''
        if self.output_queue is not None:
            raise RuntimeError("cannot attach two output queues to thread " + str(self))
        self.output_queue = q

    def _wait_for_or_create_input(self):
        if not self.empty_in:
            in_message = self.input_queue.consume()
        else:
            # TODO generalize: message type as constructor parameters
            in_message = resolve_protobuf_message('Empty')()
        return in_message

    def _distribute_or_ignore_output(self, out_message):
        if not self.empty_out:
            self.output_queue.add(out_message)

    def __str__(self):
        return f'OrchestrationThreadBase[svc={self.servicename},rpc={self.rpcname}]'


class StreamOutOrchestrationThread(OrchestrationThreadBase):
    def run(self):
        self._event('thread started', {})
        channel = grpc.insecure_channel(f'{self.host}:{self.port}')
        stub = resolve_service_stub(self.servicename)(channel)
        try:
            while True:
                in_message = self._wait_for_or_create_input()
                self._event('calling RPC', {'rpc': self.rpcname, 'message': in_message})
                rpcresult = getattr(stub, self.rpcname)(in_message)
                for out_message in rpcresult:
                    self._event('distributing streaming output', {'rpc': self.rpcname, 'message': out_message})
                    self._distribute_or_ignore_output(out_message)
        except Exception:
            logging.error(traceback.format_exc())
        self._event('thread terminated', {})


class NonstreamOrchestrationThread(OrchestrationThreadBase):
    def run(self):
        self._event('thread started', {})
        channel = grpc.insecure_channel(f'{self.host}:{self.port}')
        stub = resolve_service_stub(self.servicename)(channel)
        try:
            while True:
                in_message = self._wait_for_or_create_input()
                self._event('calling RPC', {'rpc': self.rpcname, 'message': in_message})
                out_message = getattr(stub, self.rpcname)(in_message)
                self._event('distributing output message', {'rpc': self.rpcname, 'message': out_message})
                self._distribute_or_ignore_output(out_message)
        except Exception:
            logging.error(traceback.format_exc())
        self._event('thread terminated', {})


class InputIteratorFromOrchestrationQueue:
    def __init__(self, q: OrchestrationQueue):
        self.q = q

    def __iter__(self):
        while True:
            e = self.q.consume()
            # TODO remember "unconsumed" if exception during yield and usefor next rpc call
            yield e


class StreamInOrchestrationThread(OrchestrationThreadBase):
    def run(self):
        self._event('thread started', {})
        channel = grpc.insecure_channel(f'{self.host}:{self.port}')
        stub = resolve_service_stub(self.servicename)(channel)
        assert(self.empty_in is False)
        try:
            while True:
                while self.input_queue.qsize() == 0:
                    time.sleep(0.1)
                in_message_iterator = InputIteratorFromOrchestrationQueue(self.input_queue)
                self._event('calling RPC', {'rpc': self.rpcname})
                out_message = getattr(stub, self.rpcname)(in_message_iterator.__iter__())
                self._event('distributing output message', {'rpc': self.rpcname, 'message': out_message})
                self._distribute_or_ignore_output(out_message)
        except Exception:
            logging.error(traceback.format_exc())
        self._event('thread terminated', {})


class StreamInOutOrchestrationThread(OrchestrationThreadBase):
    def run(self):
        self._event('thread started', {})
        channel = grpc.insecure_channel(f'{self.host}:{self.port}')
        stub = resolve_service_stub(self.servicename)(channel)
        assert(self.empty_in is False)
        try:
            while True:
                while self.input_queue.qsize() == 0:
                    time.sleep(0.1)
                in_message_iterator = InputIteratorFromOrchestrationQueue(self.input_queue)
                self._event('calling RPC', {'rpc': self.rpcname})
                rpcresult = getattr(stub, self.rpcname)(in_message_iterator.__iter__())
                for out_message in rpcresult:
                    self._event('distributing streaming output', {'rpc': self.rpcname, 'message': out_message})
                    self._distribute_or_ignore_output(out_message)
        except Exception:
            logging.error(traceback.format_exc())
        self._event('thread terminated', {})


class OrchestrationManager:
    threads: Dict[str, OrchestrationThreadBase]
    queues: Dict[str, OrchestrationQueue]
    observer: OrchestrationObserver

    def __init__(self):
        self.threads = {}
        self.queues = {}
        self.observer = LoggingOrchestrationObserver()

        # key = (stream_in, stream_out)
        self.THREAD_TYPES = {
            (False, False): NonstreamOrchestrationThread,
            (False, True): StreamOutOrchestrationThread,
            (True, False): StreamInOrchestrationThread,
            (True, True): StreamInOutOrchestrationThread,
        }

    def create_thread(
        self,
        stream_in: bool, stream_out: bool,
        host: str, port: int,
        service: str, rpc: str,
        empty_in: bool = False, empty_out: bool = False,
    ) -> OrchestrationThreadBase:

        name = f'{service}.{rpc}'
        assert(name not in self.threads)

        Thread_type = self.THREAD_TYPES[(stream_in, stream_out)]
        t = Thread_type(host, port, service, rpc, self.observer, empty_in, empty_out)
        self.threads[name] = t

        return t

    def create_queue(
        self,
        name: str, message: str
    ) -> OrchestrationQueue:

        assert(name not in self.queues)

        Queue_type = LimitlessOrchestrationQueue
        q = Queue_type(name, self.observer)
        self.queues[name] = q

        return q

    def orchestrate_forever(self):
        # event
        for t in self.threads.values():
            t.start()

        # event
        for t in self.threads.values():
            t.join()
