#!/usr/bin/env python3
import logging
import sys
import signal
import constants
from typing import Optional
from util.fakeprocess import fake_process

from util.log import setup_logging
from util.config import all_configs_exist
from util.agusavior import send_telegram_message

from amqp.loop import connection_loop_with_reconnection
from amqp.simplifier import callback_simplifier

# Return the response. If you don't want to respond anything, send None.
@callback_simplifier
def on_message(data: dict) -> Optional[dict]:
    send_telegram_message(f'Processing a video...{data}')
    
    fake_process(8 * 60)

    send_telegram_message('Video processed.')
    return None

# Function that will be executed when AWS wants to kill the process.
def on_sigterm(_, __):
    # Let's notify
    send_telegram_message('AWS killing a process.')

    # Do the same as we press Ctrl+C
    raise KeyboardInterrupt()

def main():
    log = setup_logging(main.__name__)

    # Assert that every necessary config is setted up
    if not all_configs_exist():
        log.critical("Please set up all credentials (var env/env.py)")
        sys.exit(1)

    # Register singal handler so we can caught the AWS intent for closing the app.
    # This intent will be produced if AWS wants to terminate your instance.
    # I think that this signal doesn't work if AWS terminates your instance for an Auto Scaling down.
    # The handler will be executed in the main thread.
    # Read more about it: https://aws.amazon.com/es/blogs/containers/graceful-shutdowns-with-ecs/
    signal.signal(signal.SIGTERM, on_sigterm)

    # AWS Task detection
    if constants.ECS_METADATA_DICT:
        send_telegram_message(f'AWS Metadata: {constants.ECS_METADATA_DICT}')

    # Start the server
    send_telegram_message(f'Starting a Server! {constants.ECS_ENABLE_CONTAINER_METADATA} {constants.ECS_CONTAINER_METADATA_FILE}')
    log.info("STARTING PROCESSING WORKER")
    try:
        log.info("Starting AMQP consume loop")
        connection_loop_with_reconnection(on_message)
    except Exception as e:
        log.exception(f'Server run exception: {e}')
    log.info("EXITING PROCESSING SERVER")
    send_telegram_message('Closing a Server.')
