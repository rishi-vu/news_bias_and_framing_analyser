import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Explainable Multi-Source News Bias and Framing Analyzer"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    CLUSTERING_SIMILARITY_THRESHOLD: float = 0.65
    CLAIM_SIMILARITY_THRESHOLD: float = 0.70
    OMISSION_SIMILARITY_THRESHOLD: float = 0.60
    DEVICE: str = "cpu"  # will automatically detect cuda if available

    class Config:
        env_file = ".env"

settings = Settings()
