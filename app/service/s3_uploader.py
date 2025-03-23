import boto3
import uuid
from botocore.exceptions import NoCredentialsError
from app.config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, S3_BUCKET_NAME, S3_BUCKET_DIRECTORY

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def upload_to_s3(local_path):
    # 확장자 추출 및 고유 파일명 생성
    file_ext = local_path.split('.')[-1]
    file_id = f"{uuid.uuid4()}.{file_ext}"

    # 지정된 버킷 디렉토리에 업로드할 S3 key 생성
    s3_key = f"{S3_BUCKET_DIRECTORY}/{file_id}"

    try:
        s3.upload_file(local_path, S3_BUCKET_NAME, s3_key)
        url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        return url
    except NoCredentialsError:
        raise Exception("AWS 인증 정보가 올바르지 않습니다.")
