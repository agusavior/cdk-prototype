from util.constantbuilders import from_env, from_json_file, from_uuid

# Amazon metadata information. Read more about it on https://docs.aws.amazon.com/AmazonECS/latest/developerguide/container-metadata.html
ECS_ENABLE_CONTAINER_METADATA = from_env('ECS_ENABLE_CONTAINER_METADATA')
ECS_CONTAINER_METADATA_FILE = from_env('ECS_CONTAINER_METADATA_FILE')
ECS_METADATA_DICT = from_json_file(ECS_CONTAINER_METADATA_FILE) if ECS_CONTAINER_METADATA_FILE else None

PROCESS_UUID = from_uuid()

AMQP_URL = 'AMQP_URL'
AMQP_EXCHANGE = 'AMQP_EXCHANGE'
RECV_Q = 'RECV_Q'
SEND_Q = 'SEND_Q'

EXCHANGE = 'processing_responses'
ROUTING_KEY = 'processing.#'
