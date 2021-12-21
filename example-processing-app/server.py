#!/usr/bin/env python3
import logging
import sys
import json
import signal
from typing import KeysView, Optional, Tuple
from util.fakeprocess import fake_process

from util.log import setup_logging
from util.config import all_configs_exist
from util.agusavior import send_telegram_message

from messenger import connection_loop_with_reconnection, hbc_handler

# Return the response. If you don't want to respond anything, send None.

@hbc_handler
def process_a_message(data: dict) -> Optional[dict]:
    send_telegram_message(f'Processing a video...{data}')
    
    fake_process(8)

    send_telegram_message('Video processed.')
    
    return None

class Server:
    def __init__(self):
        self.log = setup_logging(self.__class__.__name__)
        if not all_configs_exist():
            self.log.critical("Please set up all credentials (var env/env.py)")
            sys.exit(1)

    def start(self):
        send_telegram_message('Starting a Server!')
        self.log.info("STARTING PROCESSING WORKER")
        try:
            self.log.info("Starting AMQP consume loop")
            connection_loop_with_reconnection(process_a_message)
        except Exception as e:
            self.log.exception(f'Server run exception: {e}')
        self.log.info("EXITING PROCESSING SERVER")
        send_telegram_message('Closing a Server.')


# Function that will be executed when AWS wants to kill the process.
def on_sigterm(_, __):
    # Let's notify
    send_telegram_message('AWS killing a process.')

    # Do the same as we press Ctrl+C
    raise KeyboardInterrupt

def main():
    # Register singal handler so we can caught the AWS intent for closing the app.
    # This intent will be produced if you are using an Spot instance.
    # The handler will be executed in the main thread.
    # Read more about it: https://aws.amazon.com/es/blogs/containers/graceful-shutdowns-with-ecs/
    signal.signal(signal.SIGTERM, on_sigterm)

    # Start the server.
    server = Server()
    server.start()
