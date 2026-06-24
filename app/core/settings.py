from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    discord_token: str
    env: Literal["dev", "prod"]

    @property
    def is_dev(self) -> bool:
        return self.env == "dev"


load_dotenv()
SETTINGS = Settings()  # pyright: ignore[reportCallIssue]
