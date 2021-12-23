from util.constantbuilders import from_env, from_json_file, from_uuid

# Amazon metadata information. Read more about it on https://docs.aws.amazon.com/AmazonECS/latest/developerguide/container-metadata.html
ECS_ENABLE_CONTAINER_METADATA = from_env('ECS_ENABLE_CONTAINER_METADATA')
ECS_CONTAINER_METADATA_FILE = from_env('ECS_CONTAINER_METADATA_FILE')
ECS_METADATA_DICT = from_json_file(ECS_CONTAINER_METADATA_FILE) if ECS_CONTAINER_METADATA_FILE else None

PROCESS_UUID = from_uuid()

AMQP_URL = from_env('AMQP_URL', required=True)
AMQP_RECV_Q = 'processing.pending.1'
AMQP_SEND_Q = 'processing.done.1'

AMQP_EXCHANGE = 'processing'
AMQP_ROUTING_KEY = 'processing.#'
