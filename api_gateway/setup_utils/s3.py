from typing import Final

from pydantic import BaseSettings

from api_gateway.infrastructure.s3.s3_uploader import S3Uploader


class S3Settings(BaseSettings):
    bucket_name: str

    class Config:
        env_prefix = "s3_"


def _create_s3_uploader() -> S3Uploader:
    settings = S3Settings()
    return S3Uploader(settings.bucket_name)


_S3_UPLOADER: Final[S3Uploader] = _create_s3_uploader()


def get_s3_uploader() -> S3Uploader:
    return _S3_UPLOADER
