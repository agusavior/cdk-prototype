import os
import sys

import constants as c
import env

OUTPUT_PATH = f"{os.getenv('HOME', '.')}/worker_media"
OUTPUT_TO_STDOUT = not os.getenv('SUPERVISOR_ENABLED')


_configs = {
    c.AMQP_URL: env.amqp_url,

    c.S3_ACCESS_KEY: env.s3_access_key,
    c.S3_SECRET_KEY: env.s3_secret_key,
    c.S3_BUCKET_NAME: env.s3_bucket_name,
    c.S3_DEFAULT_REGION: env.s3_default_region,

    c.RECV_Q: env.mq_recv_q,
    c.SEND_Q: env.mq_send_q,

    c.STITCH_BIN: env.stitch_bin,
    c.SERHII_STITCH_BIN: env.serhii_stitch_bin,
    c.REVERSE_STITCH: env.reverse_stitch,

    c.CROP_X: env.crop_x,
    c.CROP_Y: env.crop_y,
    c.CROP_OFFSET_X: env.crop_offset_x,
    c.CROP_OFFSET_Y: env.crop_offset_y
}


def all_configs_exist():
    """Checks each key resolves to some non-empty value."""
    for key in _configs.keys():
        if not _config_getter(key):
            return False
    return True

def assert_all_config():
    """Checks if some key has some non-empty value. If it has, raise an Exception."""
    for key in _configs.keys():
        if not _config_getter(key):
            raise AssertionError(f'Key "{key}" has empty value in configuration.')

def get_config(var):
    """Returns env var, defaults to env.py configuration."""
    if var not in _configs.keys():
        from .log import setup_logging
        log = setup_logging('get_config')
        log.critical('Inexistent config variable. Will exit!')
        sys.exit(1)
    try:
        return _config_getter(var)
    except AttributeError:
        return None

def _config_getter(var):
    return os.getenv(var, _configs[var])


# Asserting configuration!
assert_all_config()
