import attrs


@attrs.define
class Auth0TokenPayload:
    iss: str
    sub: str
    aud: list[str]
    iat: int
    exp: int
    azp: str
    scope: str
