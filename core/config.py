import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    # Providers
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3.5:397b-cloud"
    
    HF_API_TOKEN: Optional[str] = None
    HF_MODEL_ID: Optional[str] = "meta-llama/Llama-2-7b-chat-hf"
    
    NVIDIA_API_KEY: Optional[str] = None
    NVIDIA_MODEL_ID: Optional[str] = "nvidia/llama-3.1-405b-instruct"
    
    # Active Provider
    # Options: 'ollama', 'huggingface', 'nvidia'
    PROVIDER: str = "ollama"

    # Token limits
    MAX_CONTEXT_TOKENS: int = 4096
    TOKEN_ESTIMATE_PER_CHAR: int = 4
    SLIDING_WINDOW_SIZE: int = 50
    SUMMARY_TRIGGER_RATIO: float = 0.8
    
    # Execution
    MAX_STEPS: int = 100
    TIMEOUT: int = 300

settings = Settings()
