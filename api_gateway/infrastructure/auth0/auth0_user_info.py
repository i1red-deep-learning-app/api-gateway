import datetime as dt

import attrs


@attrs.define
class Auth0UserInfo:
    sub: str
    nickname: str
    name: str
    picture: str
    updated_at: dt.datetime
    email: str
    email_verified: bool
