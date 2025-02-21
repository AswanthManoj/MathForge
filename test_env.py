# import os
# import json
# import random
# from openai import AsyncOpenAI  # Assuming this is the correct import for AsyncOpenAI

# from dotenv import load_dotenv
# load_dotenv() # Load environment variables from .env file

# current_provider = "groq"
# DEFAULT_GROQ_API_KEY = ""  # Define a default API key if none is found or parsing fails

# if current_provider == "groq":

#     groq_api_keys_str = os.environ.get("GROQ_API_KEYS")
#     api_keys = None  # Initialize to None, indicating default key usage

#     if groq_api_keys_str:
#         try:
#             api_keys = json.loads(groq_api_keys_str)
#             print(api_keys)
#             if isinstance(api_keys, list) and all(isinstance(key, str) for key in api_keys):
#                 # Successfully parsed and is a list of strings
#                 _api_key = random.choice(api_keys)
#             else:
#                 print("GROQ_API_KEYS environment variable is not a valid string array. Using default API key.")
#                 print("(Expected format: GROQ_API_KEYS='[\"key1\", \"key2\", ...\"]')")
#                 _api_key = DEFAULT_GROQ_API_KEY # Fallback to default if not a valid array
#         except json.JSONDecodeError:
#             print("GROQ_API_KEYS environment variable is not valid JSON. Using default API key.")
#             print("(Expected format: GROQ_API_KEYS='[\"key1\", \"key2\", ...\"]')")
#             _api_key = DEFAULT_GROQ_API_KEY # Fallback to default if JSON parsing fails
#     else:
#         print("GROQ_API_KEYS environment variable not found. Using default API key.")
#         _api_key = DEFAULT_GROQ_API_KEY # Fallback to default if GROQ_API_KEYS is not set

#     if not api_keys and _api_key == DEFAULT_GROQ_API_KEY: # Double check if we are using default key
#         print("(using default api key)") # Print message only when explicitly using default


#     groq = AsyncOpenAI(
#         api_key=_api_key,
#         base_url="fdsfdsf"
#     )