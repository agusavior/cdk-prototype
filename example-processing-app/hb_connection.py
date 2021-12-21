from typing import Any, Callable
import pika
import logging
import threading
import time
from util.log import setup_logging

# Type alias
OnMessageCallback = Callable[['HBCChannel', Any, Any, bytes], Any]

'''
We've had this problem:
https://stackoverflow.com/questions/14572020/handling-long-running-tasks-in-pika-rabbitmq
There were many proposal solutions.
One of them is turning off heartbeating. But, for some reason, this is not advisable.
Another solution is using this code:
https://github.com/pika/pika/blob/0.12.0/examples/basic_consumer_threaded.py
But, this code allows to consume messages in parallel, and this is a problem. We want to
consume and process one message at once (per program).
So, this class allows you to:
1. Keeping the hartbeating.
2. Process one message at once.
Every time that the amqp consumer loop, receive a message, it will create a thread
to process that message, UNLESS there is already a thread processing a message.

Thanks to this feature, we can do stuff with threading: https://github.com/pika/pika/pull/956
'''
class HeartbeatingBlockingConnection(pika.BlockingConnection):
    def __init__(self, parameters=None, _impl_class=None):
        super().__init__(parameters=parameters, _impl_class=_impl_class)
        self.lock = threading.Lock()
    
    def create_hbc_channel(self, queue_name: str, on_message_callback: OnMessageCallback):
        return HBCChannel(self.lock, queue_name, self, on_message_callback)

    
# HBCChannel means HeartbeatingBlockingConnection channel
class HBCChannel:
    def __init__(self,
        lock: threading.Lock,
        queue_name: str,
        connection: HeartbeatingBlockingConnection,
        on_message_callback: OnMessageCallback,
        ) -> None:
        # Attributes
        self._connection = connection
        self._channel = connection.channel()
        self.log = setup_logging(HBCChannel.__name__)
        self.lock = lock
        self.last_process_message_thread = None

        # Create remote queue (if not exists)
        self._channel.queue_declare(queue_name)
    
        # Set up consume
        self._channel.basic_consume(
            queue=queue_name,
            on_message_callback=lambda ch, method_frame, header_frame, body:
                self._on_message(ch, method_frame, header_frame, body, on_message_callback),
            auto_ack=False
        )
    
    def _on_message(self, _channel, method_frame, _header_frame, body, on_message_callback: OnMessageCallback):
        delivery_tag = method_frame.delivery_tag
        
        has_been_locked = self.lock.acquire(blocking=False)

        if has_been_locked:
            # When this thread finish, it will release the lock.
            def function_that_will_be_running_in_other_thread():
                try:
                    on_message_callback(self, method_frame, _header_frame, body)
                finally:
                    self.lock.release()
                
            # Launch a thread to process it.
            process_message_thread = threading.Thread(
                target=function_that_will_be_running_in_other_thread,
            )
            process_message_thread.start()

            # Save it.
            self.last_process_message_thread = process_message_thread
        else:
            # Reject the message so another consumer can consume it.
            self._channel.basic_reject(delivery_tag)

            # Wait a few seconds to prevent consuming the same (or other) message right now.
            # Probably this code is unnecessary.
            time.sleep(2)

    def basic_publish(self, *args, **kwargs):
        self._connection.add_callback_threadsafe(
            lambda: self._channel.basic_publish(*args, **kwargs)
        )

    def basic_ack(self, *args, **kwargs):
        self._connection.add_callback_threadsafe(
            lambda: self._channel.basic_ack(*args, **kwargs)
        )

    def start_consuming(self):
        try:
            self._channel.start_consuming()
        finally:
            if self.last_process_message_thread and self.last_process_message_thread.is_alive:
                self.log.info('Waiting until "process_message_thread" finishes.')
                self.last_process_message_thread.join()

    def stop_consuming(self):
        self._channel.stop_consuming()
    