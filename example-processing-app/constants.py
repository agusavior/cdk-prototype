from util.constantbuilders import from_env, from_json_file

# Amazon metadata information. Read more about it on https://docs.aws.amazon.com/AmazonECS/latest/developerguide/container-metadata.html
ECS_ENABLE_CONTAINER_METADATA = from_env('ECS_ENABLE_CONTAINER_METADATA')
ECS_CONTAINER_METADATA_FILE = from_env('ECS_CONTAINER_METADATA_FILE')
ECS_METADATA_DICT = from_json_file(ECS_CONTAINER_METADATA_FILE) if ECS_CONTAINER_METADATA_FILE else None

AMQP_URL = 'AMQP_URL'
AMQP_EXCHANGE = 'AMQP_EXCHANGE'
RECV_Q = 'RECV_Q'
SEND_Q = 'SEND_Q'

# Amazon S3 constants.
S3_ACCESS_KEY = 'FANATY_S3_ACCESS_KEY'
S3_SECRET_KEY = 'FANATY_S3_SECRET_KEY'
S3_BUCKET_NAME = 'FANATY_S3_BUCKET_NAME'
S3_DEFAULT_REGION = 'FANATY_S3_DEFAULT_REGION'

STITCH_BIN = 'STITCH_BIN'
SERHII_STITCH_BIN = 'SERHII_STITCH_BIN'
REVERSE_STITCH = 'REVERSE_STITCH'

CROP_X = 'CROP_X'
CROP_Y = 'CROP_Y'
CROP_OFFSET_X = 'CROP_OFFSET_X'
CROP_OFFSET_Y = 'CROP_OFFSET_Y'

# Actions
STITCH_ACTION = 'stitch'
SERHII_STITCH_ACTION = 'serhii_stitch'
CUSTOM_FOLLOW_ACTION = 'custom_follow'
SLEEP_ACTION = 'test_sleep'
TRACK_ACTION = 'track'
HIGHLIGHT_CUT = 'highlight'
CONCATENATE = 'concatenate'
LONG_CONCAT = 'concat_long'
CROP_ACTION = 'crop'

EXCHANGE = 'processing_responses'
ROUTING_KEY = 'processing.#'