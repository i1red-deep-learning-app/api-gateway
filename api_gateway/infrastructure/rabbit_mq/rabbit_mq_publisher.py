import logging
from collections.abc import Callable

from pika import BasicProperties, BlockingConnection, ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel
from pika.exceptions import StreamLostError


logger = logging.getLogger(__name__)


class RabbitMqPublisher:
    def __init__(
        self, connection_parameters: ConnectionParameters, setup_channel: Callable[[BlockingChannel], None]
    ) -> None:
        self._connection_parameters = connection_parameters
        self._setup_channel = setup_channel

        self._channel = self._create_channel()

    def _create_channel(self) -> BlockingChannel:
        connection = BlockingConnection(self._connection_parameters)
        channel = connection.channel()
        self._setup_channel(channel)
        return channel

    def basic_publish(
        self, exchange: str, routing_key: str, body: bytes, properties: BasicProperties = None, mandatory: bool = False
    ) -> None:
        try:
            self._channel.basic_publish(exchange, routing_key, body, properties, mandatory)
        except StreamLostError:
            logger.info("Handle pika's StreamLostError")
            self._channel = self._create_channel()
            self._channel.basic_publish(exchange, routing_key, body, properties, mandatory)
