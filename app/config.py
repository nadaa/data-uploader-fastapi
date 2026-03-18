from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path


# Base class for defining and managing environment-based settings
class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    database_test_name:str

    upload_root:Path = Path.home()
    upload_dir:str
    default_store_type:str
  

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"  
    )


settings = Settings()