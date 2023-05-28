import datetime as dt

import jwt
import requests

from api_gateway.infrastructure.auth0.auth0_token_payload import Auth0TokenPayload
from api_gateway.infrastructure.auth0.exceptions import TokenVerificationException
from api_gateway.infrastructure.auth0.auth0_user_info import Auth0UserInfo


class Auth0Client:
    def __init__(self, domain: str, api_audience: str, algorithms: str, issuer: str) -> None:
        self._domain = domain
        self._api_audience = api_audience
        self._algorithms = algorithms
        self._issuer = issuer

    def verify_token(self, token: str) -> Auth0TokenPayload:
        jwks_url = f"https://{self._domain}/.well-known/jwks.json"
        jwks_client = jwt.PyJWKClient(jwks_url)

        try:
            signing_key = jwks_client.get_signing_key_from_jwt(token).key
        except jwt.exceptions.DecodeError:
            raise TokenVerificationException("Invalid token structure")

        try:
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=self._algorithms,
                audience=self._api_audience,
                issuer=self._issuer,
            )
        except Exception:
            raise TokenVerificationException("Failed to decode token")

        return Auth0TokenPayload(**payload)

    def get_token_user_info(self, token: str) -> Auth0UserInfo:
        user_info_url = f"https://{self._domain}/userinfo"
        response = requests.get(user_info_url, headers={"Authorization": f"Bearer {token}"})
        user_info_json = response.json()

        return Auth0UserInfo(
            sub=user_info_json["sub"],
            nickname=user_info_json["nickname"],
            name=user_info_json["name"],
            picture=user_info_json["picture"],
            updated_at=dt.datetime.strptime(user_info_json["updated_at"], "%Y-%m-%dT%H:%M:%S.%fZ"),
            email=user_info_json["email"],
            email_verified=user_info_json["email_verified"],
        )
