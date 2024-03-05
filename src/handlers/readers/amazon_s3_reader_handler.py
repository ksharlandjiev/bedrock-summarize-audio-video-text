import os
import boto3
from io import BytesIO
from typing import Any
from handlers.abstract_handler import AbstractHandler
from dotenv import load_dotenv
class AmazonS3ReaderHandler(AbstractHandler):
    def handle(self, request: dict) -> dict:
        # Extract the S3 object path from the request
        s3_object_path = request.get("path")
        
        s3_bucket, s3_object = self.parse_s3_path(s3_object_path)


        print(f"Reading content from s3://{s3_bucket}/{s3_object}")

        file_content = self.read_file_content_from_s3(s3_object, s3_bucket)
        
        # Update request with the file content
        request.update({"text": file_content})
        
        return super().handle(request)

    def read_file_content_from_s3(self, s3_object, bucket_name):
        """
        Reads file content from an S3 bucket and returns it as a string.
        """
        s3_client = boto3.client('s3')
        s3_object = s3_client.get_object(Bucket=bucket_name, Key=s3_object)
        file_content = s3_object['Body'].read().decode('utf-8')
        
        return file_content

    def parse_s3_path(self, s3_path):
        # Assumes s3_path format is "s3://bucket-name/path/to/object"
        _, _, bucket_name, object_key = s3_path.split('/', 3)
        return bucket_name, object_key