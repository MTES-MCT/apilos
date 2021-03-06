from django.conf import settings
import boto3


class StorageClient:
    # pylint: disable=R0903
    client = None
    is_s3 = False

    def __init__(self):
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            self.is_s3 = True
            self.client = boto3.client(
                "s3",
                region_name=settings.AWS_S3_REGION_NAME,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

    def put_object(self, my_file, target):
        if self.is_s3:
            self.client.put_object(
                Body=my_file,
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=target,
                ACL="private",
                CacheControl="max-age=31556926",  # 1 year
            )


client = StorageClient()
