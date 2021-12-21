import os
from typing import Optional
import env

import json

# If the variable `enviroment_variable_name` is defined as an enviroment variable or if it is defined
# in your env.py file, return it. Else, return None.
def from_env(enviroment_variable_name, required = False, default_value = None) -> Optional[str]:
    value = os.getenv(enviroment_variable_name) or getattr(env, enviroment_variable_name, None) or default_value
    if required and value is None: raise NotImplementedError(f'Please define your {enviroment_variable_name} variable.')
    else: return value

# From a file path, open that file, reads the JSON and convert it to a python dict.
# This assume that the JSON has an object as root (neither a number nor a string).
def from_json_file(file_path: str) -> dict:
    f = open(file_path)
    data: dict = json.load(f)
    f.close()
    return data
