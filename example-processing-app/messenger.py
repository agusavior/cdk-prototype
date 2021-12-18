from time import sleep
import urllib.parse

import pika
import pika.exceptions

from util.log import setup_logging
from util.config import get_config
from util import constants as c
import threading
import json

def new_pika_blocking_connection():
    url_str = get_config(c.AMQP_URL)
    url = urllib.parse.urlparse(url_str)
    params = pika.ConnectionParameters(
        host=url.hostname,
        virtual_host=url.path[1:],
        heartbeat=300,
        credentials=pika.PlainCredentials(url.username, url.password)
    )
    return pika.BlockingConnection(params)

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
'''
class LongTasksNotParallelAMQPConnection:
    QUEUE = get_config(c.RECV_Q)

    def __init__(self, process_function):
        # Logger.
        self.log = setup_logging(LongTasksNotParallelAMQPConnection.__name__)
        self.process_function = process_function
        self.lock = threading.Lock()
        self.last_process_message_thread = None
        self.connection = new_pika_blocking_connection()
        self.channel = self.connection.channel()

        # Create queue (if not exists)
        self.channel.queue_declare(self.QUEUE)

        # Set up consume
        self.channel.basic_consume(
            queue=self.QUEUE,
            on_message_callback=lambda ch, mf, hf, b: self._on_message(ch, mf, hf, b),
            auto_ack=False
        )

    def _on_message(self, _channel, method_frame, _header_frame, body):
        delivery_tag = method_frame.delivery_tag

        self.log.debug(f'AMQP message received. Delivery tag: {delivery_tag}')

        has_been_locked = self.lock.acquire(blocking=False)

        if has_been_locked:
            message_body = body.strip().decode()

            # Launch a thread to process it.
            # When this thread finish, it will release the lock.
            process_message_thread = ProcessMessageThread(
                self.channel,
                self.process_function,
                message_body,
                delivery_tag,
                self.lock,
            )
            process_message_thread.start()

            # Save it.
            self.last_process_message_thread = process_message_thread
        else:
            # Reject the message so another consumer can consume it.
            self.channel.basic_reject(delivery_tag)

            self.log.debug('An AMQP message has been rejected.')

            # Wait a few seconds to prevent consuming the same (or other) message right now.
            # Probably this code is unnecessary.
            sleep(2)
    
    def consuming_loop(self):
        self.log.info('Consuming loop. Press Ctrl+C to stop it.')
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.log.info('KeyboardInterrupt detected. Exiting...')
        
        if self.last_process_message_thread:
            self.log.info('Wait until "process_message_thread" finish.')
            self.last_process_message_thread.join()

        self.log.info('Stopping AMQP connection...')
        self.channel.stop_consuming()
        self.connection.close()


class ProcessMessageThread(threading.Thread):
    EXCHANGE = 'processing_responses'
    ROUTING_KEY = c.SEND_Q.rsplit('.', 1)[0] + '.#'

    def __init__(self, channel, process_function, message_body, message_delivery_tag, lock_to_release):
        super().__init__()
        self.channel = channel
        self.lock_to_release = lock_to_release
        self.message_body = message_body
        self.message_delivery_tag = message_delivery_tag
        self.process_function = process_function

    def run(self):
        # Process
        should_respond, response = self.process_function(self.message_body)

        # Response
        if should_respond:
            json_response = json.dumps(response)
            self.channel.basic_publish(
                self.EXCHANGE, 
                self.ROUTING_KEY,
                json_response
            )

        # Acknowledge
        self.channel.basic_ack(self.message_delivery_tag)

        # Release lock
        self.lock_to_release.release()

# This function is similar to this one:
# https://pika.readthedocs.io/en/stable/examples/blocking_consume_recover_multiple_hosts.html
def connection_loop_with_reconnection(process_function):
    log = setup_logging(connection_loop_with_reconnection.__name__)

    while True:
        try:
            log.info('Setting up new AMQP connection.')

            # Create and set up connection
            connection = LongTasksNotParallelAMQPConnection(process_function)

            # Consuming loop
            connection.consuming_loop()

            log.info('Consuming loop is over. Stopping...')
            break
        except pika.exceptions.ConnectionClosedByBroker:
            # Uncomment this to make the example not attempt recovery
            # from server-initiated connection closure, including
            # when the node is stopped cleanly
            #
            # break
            log.debug('Connection closed by broker. Retrying...')
            continue
        except pika.exceptions.AMQPChannelError as err:
            # Do not recover on channel errors
            log.error(f'Caught a channel error: {err}, stopping...')
            break
        except pika.exceptions.AMQPConnectionError as err:
            # Recover on all other connection errors
            log.error(f'Connection was closed. Reason: {err}.\nRetrying...')
            continue
