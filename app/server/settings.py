from typing import Set

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Parameters to be loaded from Environment Variables in .env file"""

    # API
    disable_openapi: bool = False
    root_path: str = None
    cors_allow_origins: Set[str] = None
    enable_racedisplay = True

    # Database
    database_url: str = "mongodb+srv://drift_0815:TDcMfjlbc0632h3FWbCT@cluster0.ua0cw.mongodb.net/?retryWrites=true&w=majority"
    database_name: str = "drift_0815"

    class Config:
        env_prefix = "DRIFTAPI_"
        env_file = ".env"
