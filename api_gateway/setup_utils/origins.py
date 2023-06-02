from pydantic import BaseSettings


class AllowedOriginsSettings(BaseSettings):
    allowed_origins: str


def get_allowed_origins() -> list[str]:
    settings = AllowedOriginsSettings()
    return settings.allowed_origins.split(",")
