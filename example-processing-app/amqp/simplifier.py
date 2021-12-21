
from typing import Callable, Optional

import amqp.hb_connection as hb_connection

from util.log import setup_logging
from util.config import get_config
import constants as c
import json

# Decorator
def callback_simplifier(function: Callable[[dict], Optional[dict]]):
    def on_message_callback(channel: hb_connection.HBCChannel, method_frame, _headers, body):
        log = setup_logging(on_message_callback.__name__)

        delivery_tag = method_frame.delivery_tag

        if not body:
            log.warn(f'Received empty message body. (delivery_tag={delivery_tag})')
            return
        
        try:
            body_str: str = body.strip().decode()   # From bytes to str
            body_dict: dict = json.loads(body_str)  # From JSON (str) to dict
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
                c.EXCHANGE, 
                c.ROUTING_KEY,
                json_response
            )
        
        # Acknowledge
        channel.basic_ack(delivery_tag)
    return on_message_callback