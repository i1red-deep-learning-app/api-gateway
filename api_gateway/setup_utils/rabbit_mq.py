from typing import Final

from pydantic import BaseSettings
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel

from api_gateway.infrastructure.rabbit_mq.rabbit_mq_publisher import RabbitMqPublisher


class RabbitMqSettings(BaseSettings):
    host: str
    port: int
    username: str
    password: str

    class Config:
        env_prefix = "rabbit_"


def _get_connection_parameters() -> ConnectionParameters:
    settings = RabbitMqSettings()
    return ConnectionParameters(
        host=settings.host,
        port=settings.port,
        credentials=PlainCredentials(username=settings.username, password=settings.password),
    )


def _setup_channel(channel: BlockingChannel) -> None:
    channel.queue_declare("create_table_dataset")
    channel.queue_declare("create_feed_forward_network")
    channel.queue_declare("create_training_session")
    channel.queue_declare("start_ffn_training")


_PUBLISHER: Final[RabbitMqPublisher] = RabbitMqPublisher(_get_connection_parameters(), _setup_channel)


def get_rabbit_publisher() -> RabbitMqPublisher:
    return _PUBLISHER

