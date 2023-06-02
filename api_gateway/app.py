import io
import json
import uuid

from fastapi import FastAPI, UploadFile, Depends, Form, Body, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pika import BasicProperties

from starlette import status
from starlette.middleware.cors import CORSMiddleware

from api_gateway.infrastructure.auth0.exceptions import TokenVerificationException
from api_gateway.infrastructure.rabbit_mq.rabbit_mq_publisher import RabbitMqPublisher
from api_gateway.setup_utils.origins import get_allowed_origins
from api_gateway.utility.file_to_dataframe import file_to_dataframe
from api_gateway.infrastructure.auth0.auth0_client import Auth0Client
from api_gateway.setup_utils.rabbit_mq import get_rabbit_publisher
from api_gateway.setup_utils.s3 import get_s3_uploader
from api_gateway.infrastructure.s3.s3_uploader import S3Uploader
from api_gateway.utility.file_type.determine_file_type import determine_file_type
from api_gateway.setup_utils.auth0 import get_auth0_client
from api_gateway.infrastructure.auth0.auth0_user_info import Auth0UserInfo
from api_gateway.utility.file_type.exceptions import UnsupportedFileTypeException

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

token_auth_scheme = HTTPBearer()


def get_user_info(
    auth_credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme),
    auth0_client: Auth0Client = Depends(get_auth0_client),
) -> Auth0UserInfo:
    token = auth_credentials.credentials

    try:
        auth0_client.verify_token(token)
    except TokenVerificationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return auth0_client.get_token_user_info(token)


@app.post("/table-datasets", status_code=status.HTTP_200_OK)
async def create_table_dataset_view(
    file: UploadFile,
    label_column: str = Form(),
    user_info: Auth0UserInfo = Depends(get_user_info),
    s3_uploader: S3Uploader = Depends(get_s3_uploader),
    publisher: RabbitMqPublisher = Depends(get_rabbit_publisher),
) -> None:
    file_content = await file.read()
    file_type = determine_file_type(file_content)

    try:
        dataframe = file_to_dataframe(file_content, file_type)
    except UnsupportedFileTypeException as e:
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=str(e))

    if label_column not in dataframe.columns:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"'{label_column}' is not present in table")

    with io.BytesIO() as bytes_io:
        dataframe.to_feather(bytes_io)
        file_content = bytes_io.getvalue()

    file_key = "table-datasets/" + uuid.uuid4().hex
    s3_uploader.upload_file(file_key, file_content)

    body = json.dumps({"table_dataset": {"file_key": file_key, "label_column": label_column}}).encode()
    publisher.basic_publish(
        exchange="",
        routing_key="create_table_dataset",
        body=body,
        properties=BasicProperties(headers={"username": user_info.name}),
    )


@app.post("/feed-forward-networks", status_code=status.HTTP_200_OK)
async def create_feed_forward_network_view(
    feed_forward_network_json: dict = Body(),
    user_info: Auth0UserInfo = Depends(get_user_info),
    publisher: RabbitMqPublisher = Depends(get_rabbit_publisher),
) -> None:
    body = json.dumps({"feed_forward_network": feed_forward_network_json}).encode()
    publisher.basic_publish(
        exchange="",
        routing_key="create_feed_forward_network",
        body=body,
        properties=BasicProperties(headers={"username": user_info.name}),
    )


@app.post("/training-sessions", status_code=status.HTTP_200_OK)
async def create_training_session_view(
    training_session_json: dict = Body(),
    user_info: Auth0UserInfo = Depends(get_user_info),
    publisher: RabbitMqPublisher = Depends(get_rabbit_publisher),
) -> None:
    body = json.dumps({"training_session": training_session_json}).encode()
    publisher.basic_publish(
        exchange="",
        routing_key="create_training_session",
        body=body,
        properties=BasicProperties(headers={"username": user_info.name}),
    )


@app.post("/start-ffn-training", status_code=status.HTTP_200_OK)
async def start_ffn_training_view(
    start_ffn_training_json: dict = Body(),
    user_info: Auth0UserInfo = Depends(get_user_info),
    publisher: RabbitMqPublisher = Depends(get_rabbit_publisher),
) -> None:
    body = json.dumps(start_ffn_training_json).encode()
    publisher.basic_publish(
        exchange="",
        routing_key="start_ffn_training",
        body=body,
        properties=BasicProperties(headers={"username": user_info.name}),
    )
