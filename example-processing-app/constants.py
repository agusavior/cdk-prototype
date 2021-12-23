from util.constantbuilders import from_env, from_required_env, from_json_file, from_uuid

# Process unique number
PROCESS_UUID =  from_uuid()

# Amazon metadata information. Read more about it on https://docs.aws.amazon.com/AmazonECS/latest/developerguide/container-metadata.html
ECS_ENABLE_CONTAINER_METADATA = from_env('ECS_ENABLE_CONTAINER_METADATA')
ECS_CONTAINER_METADATA_FILE = from_env('ECS_CONTAINER_METADATA_FILE')
ECS_METADATA_DICT = from_json_file(ECS_CONTAINER_METADATA_FILE) if ECS_CONTAINER_METADATA_FILE else None

AMQP_URL =      from_required_env('AMQP_URL')
AMQP_RECV_Q =   from_required_env('AMQP_RECV_Q', default_value='processing.pending.1')
AMQP_SEND_Q =   from_required_env('AMQP_SEND_Q', default_value='processing.done.1')

AMQP_EXCHANGE =     'processing'
AMQP_ROUTING_KEY =  'processing.#'
