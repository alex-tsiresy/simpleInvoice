from minio import Minio
from minio.error import S3Error
from io import BytesIO
import uuid
from app.config import get_settings
from typing import BinaryIO, Tuple

settings = get_settings()


class MinIOStorage:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure
        )
        self.bucket = settings.minio_bucket
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Ensure bucket exists"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            print(f"Error creating bucket: {e}")

    def upload_file(self, file: BinaryIO, filename: str, content_type: str) -> Tuple[str, int]:
        """
        Upload file to MinIO
        Returns: (object_key, file_size)
        """
        try:
            # Generate unique object key
            file_extension = filename.split('.')[-1] if '.' in filename else ''
            object_key = f"{uuid.uuid4()}.{file_extension}" if file_extension else str(uuid.uuid4())

            # Read file content
            file_content = file.read()
            file_size = len(file_content)
            file.seek(0)  # Reset file pointer

            # Upload to MinIO
            self.client.put_object(
                self.bucket,
                object_key,
                BytesIO(file_content),
                length=file_size,
                content_type=content_type
            )

            return object_key, file_size

        except S3Error as e:
            raise Exception(f"Failed to upload file to storage: {str(e)}")

    def download_file(self, object_key: str) -> bytes:
        """
        Download file from MinIO
        Returns: file content as bytes
        """
        try:
            response = self.client.get_object(self.bucket, object_key)
            return response.read()
        except S3Error as e:
            raise Exception(f"Failed to download file from storage: {str(e)}")
        finally:
            if response:
                response.close()
                response.release_conn()

    def delete_file(self, object_key: str) -> bool:
        """Delete file from MinIO"""
        try:
            self.client.remove_object(self.bucket, object_key)
            return True
        except S3Error:
            return False

    def get_file_url(self, object_key: str, expires: int = 3600) -> str:
        """
        Generate presigned URL for file access
        Args:
            object_key: Object key in bucket
            expires: URL expiration time in seconds (default 1 hour)
        """
        try:
            return self.client.presigned_get_object(
                self.bucket,
                object_key,
                expires=expires
            )
        except S3Error as e:
            raise Exception(f"Failed to generate file URL: {str(e)}")


# Singleton instance
storage = MinIOStorage()
