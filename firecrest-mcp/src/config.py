# config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Injected by K8s External Secrets from Vault
    oauth_client_id: str
    oauth_client_secret: str
    oauth_token_url: str
    oauth_scopes: str
    backend_api_base_url: str
    # How many of the most recent requests to FirecREST are kept in the
    # history returned by get_request_stats; 0 keeps all of them
    request_stats_max_records: int = 1000

    class Config:
        env_file = ".env"


settings = Settings()
