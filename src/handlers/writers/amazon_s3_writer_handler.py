import os
import time
from handlers.abstract_handler import AbstractHandler
from utils.aws_boto_client_manager import AWSBotoClientManager

class AmazonS3WriterHandler(AbstractHandler):
    
  def handle(self, request: dict) -> dict:
    
    # Accessing variables from .env file
    BUCKET_NAME = os.getenv('BUCKET_NAME')
    S3_FOLDER = os.getenv('S3_FOLDER')

    # Upload the file to S3
    file_path = request.get("path")

    print(f"Writing {file_path} to s3://{BUCKET_NAME}/{S3_FOLDER}")
    s3_file_path = self.upload_file_to_s3(file_path, BUCKET_NAME, S3_FOLDER)

    s3_path = f"s3://{BUCKET_NAME}/{s3_file_path}"
    request.update({"path": s3_path})

    return super().handle(request)
          
  def upload_file_to_s3(self, file_path, BUCKET_NAME, S3_FOLDER):
      """
      Uploads a file to an S3 bucket and returns the S3 path.
      """
      s3_client = AWSBotoClientManager.get_client('s3')
      file_name = file_path.split('/')[-1]
      s3_path = f"{S3_FOLDER}{file_name}"
      s3_client.upload_file(file_path, BUCKET_NAME, s3_path)
      
      # eventual consistency
      time.sleep(5)
      
      return s3_path