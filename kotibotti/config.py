from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="KOTIBOTTI_")

    bot_token: str
    db_path: Path = Path.home() / ".local/state/kotibotti/db.sqlite"


config = Config()
