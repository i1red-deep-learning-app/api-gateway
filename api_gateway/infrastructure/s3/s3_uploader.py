import boto3


class S3Uploader:
    def __init__(self, bucket_name: str) -> None:
        self.s3_client = boto3.client("s3")
        self.bucket_name = bucket_name

    def upload_file(self, file_key: str, file_content: bytes) -> None:
        self.s3_client.put_object(Bucket=self.bucket_name, Key=file_key, Body=file_content)
