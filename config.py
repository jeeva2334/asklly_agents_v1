import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> str:
    """
    Get environment variable with proper error handling.
    
    Args:
        key: Environment variable name
        default: Default value if not found
        required: If True, raises error when variable is missing
        
    Returns:
        Environment variable value
        
    Raises:
        ValueError: If required variable is missing
    """
    value = os.getenv(key, default)
    
    if required and value is None:
        raise ValueError(f"Required environment variable '{key}' is not set")
    
    if value is None:
        raise ValueError(f"Environment variable '{key}' is not set and no default provided")
    
    return value

# Database Configuration
MONGO_URI = get_env_var('MONGO_URI', required=True)
MONGO_DB_NAME = get_env_var('MONGO_DB_NAME', required=True)
MONGO_COLLECTION_USERS = get_env_var('MONGO_COLLECTION_USERS', required=True)
MONGO_COLLECTION_CHATS = get_env_var('MONGO_COLLECTION_CHATS', required=True)

# AstraDB Configuration
ASTRA_CLIENT_ID = get_env_var('ASTRA_CLIENT_ID', required=True)
ASTRA_SECRET = get_env_var('ASTRA_SECRET', required=True)
ASTRA_TOKEN = get_env_var('ASTRA_TOKEN', required=True)
ASTRA_DB_ID = get_env_var('ASTRA_DB_ID', required=True)
ASTRA_ENDPOINT = get_env_var('ASTRA_ENDPOINT', required=True)

# AI Model Configuration
MISTRAL_MODEL_ID = get_env_var('MISTRAL_MODEL_ID', required=True)
MISTRAL_API_ENDPOINT = get_env_var('MISTRAL_API_ENDPOINT', required=True)
DEEPSEEK_MODEL_NAME = get_env_var('DEEPSEEK_MODEL_NAME', required=True)
LLAMA3_MODEL_NAME = get_env_var('LLAMA3_MODEL_NAME', required=True)

# DeepInfra Configuration
DEEPINFRA_API_BASE = get_env_var('DEEPINFRA_API_BASE', required=True)
DEEPINFRA_API_TOKEN = get_env_var('DEEPINFRA_API_TOKEN', required=True)
BAAI_MODEL_ID = get_env_var('BAAI_MODEL_ID', required=True)
VISION_MODEL_ID = get_env_var('VISION_MODEL_ID', required=True)

# Digital Ocean Spaces Configuration
DO_SPACES_BUCKET_NAME = get_env_var('DO_SPACES_BUCKET_NAME', required=True)
DO_SPACES_ENDPOINT_URL = get_env_var('DO_SPACES_ENDPOINT_URL', required=True)
AWS_ACCESS_KEY_ID = get_env_var('AWS_ACCESS_KEY_ID', required=True)
AWS_SECRET_ACCESS_KEY = get_env_var('AWS_SECRET_ACCESS_KEY', required=True)

# Brave Search API
BRAVE_API_KEY = get_env_var('BRAVE_API_KEY', required=True)
POSTGRES_URL = get_env_var('POSTGRES_URL', required=True)

# Legacy token mappings for backward compatibility
TOKENS = {
    "clientId": ASTRA_CLIENT_ID,
    "secret": ASTRA_SECRET,
    "token": ASTRA_TOKEN
}

DB_TOKENS = {
    "dbID": ASTRA_DB_ID,
    "token": ASTRA_TOKEN
}

TOKEN = ASTRA_TOKEN
ASTRADB_ENDPOINT = ASTRA_ENDPOINT
DB_ID = ASTRA_DB_ID