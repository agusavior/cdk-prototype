import logging
from time import sleep
from typing import Callable, Optional, Tuple
import urllib.parse

import pika
import pika.exceptions

import hb_connection

from util.log import setup_logging
from util.config import get_config
from util import constants as c
import threading
import json

from util.agusavior import send_telegram_message
from util.fakeprocess import fake_process

QUEUE_NAME = get_config(c.RECV_Q)
EXCHANGE = 'processing_responses'
ROUTING_KEY = c.SEND_Q.rsplit('.', 1)[0] + '.#'

if not QUEUE_NAME:
    raise Exception('You must define a queue for amqp')

def new_pika_heartbeating_blocking_connection() -> hb_connection.HeartbeatingBlockingConnection:
    url_str = get_config(c.AMQP_URL)
    url = urllib.parse.urlparse(url_str)
    params = pika.ConnectionParameters(
        host=url.hostname,
        virtual_host=url.path[1:],
        heartbeat=300,
        credentials=pika.PlainCredentials(url.username, url.password)
    )
    return hb_connection.HeartbeatingBlockingConnection(params)

# Decorator
def hbc_handler(function: Callable[[dict], Optional[dict]]):
    def on_message_callback(channel: hb_connection.HBCChannel, method_frame, _headers, body):
        log = setup_logging(on_message_callback.__name__)

        delivery_tag = method_frame.delivery_tag

        if not body:
            log.warn(f'Received empty message body. (delivery_tag={delivery_tag})')
            return
        
        try:
            body_str: str = body.strip().decode()
            body_dict = json.loads(body_str) # From JSON to dict
        except json.decoder.JSONDecodeError as e:
            log.error(f'Invalid JSON format. Please send a message in JSON format. Reason: {e}')
            return
        
        # Log info
        log.info(f'Message received (delivery_tag={delivery_tag}):\n{body_dict}')

        # Process
        response = function(body_dict)

        # Response
        if response is not None:
            json_response = json.dumps(response)
            channel.basic_publish(
                EXCHANGE, 
                ROUTING_KEY,
                json_response
            )
        
        # Acknowledge
        channel.basic_ack(delivery_tag)
    return on_message_callback

# This function is similar to this one:
# https://pika.readthedocs.io/en/stable/examples/blocking_consume_recover_multiple_hosts.html
def connection_loop_with_reconnection(on_message_callback):
    log = setup_logging(connection_loop_with_reconnection.__name__)

    while True:
        try:
            # Create and set up connection
            log.info('Setting up new AMQP connection.')
            connection = new_pika_heartbeating_blocking_connection()

            # Create channel and queue
            hbc_channel = connection.create_hbc_channel(QUEUE_NAME, on_message_callback)

            # Consuming loop
            log.info('Consuming loop. Press Ctrl+C to stop it.')
            try:
                hbc_channel.start_consuming()
            except KeyboardInterrupt:
                log.info('KeyboardInterrupt detected.')
            finally:
                log.info('Stopping AMQP connection...')
                hbc_channel.stop_consuming()
                connection.close()
            
            log.info('Consuming loop is over and connection closed.')
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
