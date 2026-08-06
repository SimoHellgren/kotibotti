from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    bot_token: str
    db_path: Path = Path("/var/lib/kotibotti/db.sqlite")


config = Config()
