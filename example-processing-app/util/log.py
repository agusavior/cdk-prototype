# ToDo: this module is copied from fanaty-iot, ideally DRY
import logging
from pathlib import Path

import os

OUTPUT_PATH = f"{os.getenv('HOME', '.')}/worker_media"
OUTPUT_TO_STDOUT = not os.getenv('SUPERVISOR_ENABLED')

def create_dirs(dirs):
    for d in dirs:
        Path(d).parent.mkdir(parents=True, exist_ok=True)

def setup_logging(module_name, filename=f'{OUTPUT_PATH}/worker.log'):
    create_dirs([filename])
    log = logging.getLogger(module_name)
    if not log.hasHandlers():
        log.setLevel(logging.DEBUG)
        fh = logging.FileHandler(filename)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        log.addHandler(fh)
        if OUTPUT_TO_STDOUT:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)  # ToDo: change to WARN?
            ch.setFormatter(formatter)
            log.addHandler(ch)
    return log
