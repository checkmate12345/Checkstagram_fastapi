# test_upload.py
import uuid
from io import BytesIO
from app.config import Config
import boto3
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

s3_client = boto3.client(
    "s3",
    region_name=Config.AWS_REGION,
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
)

def test_put_object():
    unique_filename = f"{Config.S3_BUCKET_DIRECTORY}/{uuid.uuid4().hex}_test.jpg"
    logging.debug(f"Uploading test file with key: {unique_filename}")
    try:
        # 간단한 BytesIO 객체 생성
        file_obj = BytesIO(b"Test data")
        response = s3_client.put_object(
            Bucket=Config.S3_BUCKET_NAME,
            Key=unique_filename,
            Body=file_obj,
            ContentType="image/jpeg"
        )
        logging.debug(f"Put object response: {response}")
        file_url = f"https://{Config.S3_BUCKET_NAME}.s3.{Config.AWS_REGION}.amazonaws.com/{unique_filename}"
        logging.debug(f"Test file URL: {file_url}")
    except Exception as e:
        logging.error("Test upload failed", exc_info=True)

if __name__ == "__main__":
    test_put_object()
