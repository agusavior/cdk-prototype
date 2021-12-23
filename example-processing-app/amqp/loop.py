import urllib.parse

import pika
import pika.exceptions

import amqp.hb_connection as hb_connection

from util.log import setup_logging
import constants as c

from util.agusavior import send_telegram_message
from util.fakeprocess import fake_process

# Creates a HeartbeatingBlockingConnection based on constants and configuration
def new_pika_heartbeating_blocking_connection() -> hb_connection.HeartbeatingBlockingConnection:
    url_str = c.AMQP_URL
    url = urllib.parse.urlparse(url_str)
    params = pika.ConnectionParameters(
        host=url.hostname,
        virtual_host=url.path[1:],
        heartbeat=300,
        credentials=pika.PlainCredentials(url.username, url.password)
    )
    return hb_connection.HeartbeatingBlockingConnection(params)

# This function is similar to this one:
# https://pika.readthedocs.io/en/stable/examples/blocking_consume_recover_multiple_hosts.html
# But it uses a custom connection instance and a custom channel instance
def connection_loop_with_reconnection(on_message_callback):
    log = setup_logging(connection_loop_with_reconnection.__name__)

    while True:
        try:
            # Create and set up connection
            log.info('Setting up new AMQP connection.')
            connection = new_pika_heartbeating_blocking_connection()

            # Create channel and queue
            hbc_channel = connection.create_hbc_channel(c.AMQP_RECV_Q, on_message_callback)

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
