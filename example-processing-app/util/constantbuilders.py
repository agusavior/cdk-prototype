import os
from typing import Optional
import env
import uuid
import json

# If the variable `enviroment_variable_name` is defined as an enviroment variable or if it is defined
# in your env.py file, return it. Else, return None.
def from_env(enviroment_variable_name, default_value = None) -> Optional[str]:
    return os.getenv(enviroment_variable_name) or getattr(env, enviroment_variable_name, None) or default_value
    if required and value is None: raise NotImplementedError(f'Please define your {enviroment_variable_name} variable.')
    else: return value

def from_required_env(enviroment_variable_name, default_value = str) -> str:
    value = from_env(enviroment_variable_name, default_value=default_value)
    if value is None: raise NotImplementedError(f'Please define your {enviroment_variable_name} variable.')
    return value

# From a file path, open that file, reads the JSON and convert it to a python dict.
# This assume that the JSON has an object as root (neither a number nor a string).
def from_json_file(file_path: str) -> dict:
    f = open(file_path)
    data: dict = json.load(f)
    f.close()
    return data

# Generate a random string
def from_uuid():
    return uuid.uuid4().hex[:6].upper()
