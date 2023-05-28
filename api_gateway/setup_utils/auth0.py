from typing import Final

from pydantic import BaseSettings

from api_gateway.infrastructure.auth0.auth0_client import Auth0Client


class Auth0Settings(BaseSettings):
    domain: str
    api_audience: str
    algorithms: str
    issuer: str

    class Config:
        env_prefix = "auth0_"


def _create_auth0_client() -> Auth0Client:
    settings = Auth0Settings()
    return Auth0Client(
        domain=settings.domain,
        api_audience=settings.api_audience,
        algorithms=settings.algorithms,
        issuer=settings.issuer,
    )


_AUTH0_CLIENT: Final[Auth0Client] = _create_auth0_client()


def get_auth0_client() -> Auth0Client:
    return _AUTH0_CLIENT
