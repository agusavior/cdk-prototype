# Add the testing or production url in the following format

# 'amqp://user_name:password@host:port/virtual_host_name'

amqp_url = ''

# Production values
s3_access_key = ''
s3_secret_key = ''
s3_bucket_name = 'fanaty-production'
s3_default_region = 'us-east-1'

# Rabbit MQ queue names

#mq_recv_q = 'processing.pending.1'
amqp_exchange = 'processing_pending.gpu'
mq_recv_q = 'processing.gpu.pending.1'
mq_send_q = 'processing.done.1'

# File path to the executable produced by the () code
stitch_bin = 'STITCH_BIN'

# File path to the executable produced by the video-processing code
serhii_stitch_bin = '/home/agusavior/build/football_stitcher'

reverse_stitch = True

crop_x = 1934
crop_y = 896
crop_offset_x = 1081
crop_offset_y = 576
