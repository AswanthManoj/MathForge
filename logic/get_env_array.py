import os
import json
import random
from openai import AsyncOpenAI  # Assuming this is the correct import for AsyncOpenAI

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

def get_env_array(env_var_name):
    """
    Retrieves an environment variable and parses it as a string array.

    Args:
        env_var_name (str): The name of the environment variable.

    Returns:
        list[str] or None: A list of strings if the environment variable
                           is found, is valid JSON, and represents a string array.
                           Returns None otherwise.
    """
    env_var_str = os.environ.get(env_var_name)
    if env_var_str:
        try:
            array_candidate = json.loads(env_var_str)
            if isinstance(array_candidate, list) and all(isinstance(item, str) for item in array_candidate):
                return array_candidate
            else:
                return None # Not a string array
        except json.JSONDecodeError:
            return None # Not valid JSON
    else:
        return None # Environment variable not found



