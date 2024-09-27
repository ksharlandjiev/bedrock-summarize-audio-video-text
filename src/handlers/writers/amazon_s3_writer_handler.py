import datetime
import os
import time
from typing import Dict
from handlers.abstract_handler import AbstractHandler
from utils.aws_boto_client_manager import AWSBotoClientManager
import tempfile


class AmazonS3WriterHandler(AbstractHandler):
    def handle(self, request: Dict) -> Dict:
        # Extracting data from request
        file_path = request.get("path")
        write_file_path = request.get("write_file_path")
        text = request.get("text")

        # Check for the scenario with write_file_path as an S3 URI
        if write_file_path and write_file_path.startswith("s3://"):
            # Get the S3 bucket and folder from the write_file_path
            bucket_name, folder_path, filename = self.parse_s3_path(write_file_path)
            
            if file_path:
                # Default behavior if `file_path` is provided
                print(f"Writing {file_path} to s3://{bucket_name}/{folder_path}")
                s3_file_path = self.upload_file_to_s3(file_path, bucket_name, folder_path, filename)
                s3_path = f"s3://{bucket_name}/{s3_file_path}"
                request.update({"path": s3_path})

            elif text:
                # Create a temporary file with text and upload to specified S3 location
                file_extension = self.get_file_extension(write_file_path)
                temp_file_path = self.create_temp_file_with_text(text, file_extension)
                print(f"Writing text to s3://{bucket_name}/{folder_path}/{filename}")
                s3_file_path = self.upload_file_to_s3(temp_file_path, bucket_name, folder_path, filename)
                s3_path = f"s3://{bucket_name}/{folder_path}/{filename}"
                request.update({"path": s3_path})

        elif file_path:
            # Default scenario where `file_path` is provided and `write_file_path` isn't S3
            bucket_name = os.getenv('BUCKET_NAME')
            s3_folder = os.getenv('S3_FOLDER')
            print(f"Writing {file_path} to s3://{bucket_name}/{s3_folder}")
            file_name = os.path.basename(file_path)
            s3_file_path = self.upload_file_to_s3(file_path, bucket_name, s3_folder, file_name)
            s3_path = f"s3://{bucket_name}/{s3_file_path}"
            request.update({"path": s3_path})

        else:
            raise ValueError("Either 'file_path' or 'text' with 'write_file_path' must be provided.")

        return super().handle(request)

    def upload_file_to_s3(self, file_path, bucket_name, s3_folder, file_name):
        """
        Uploads a file to an S3 bucket and returns the S3 path.
        """
        s3_client = AWSBotoClientManager.get_client("s3")        
        s3_path = f"{s3_folder}{file_name}"
        s3_client.upload_file(file_path, bucket_name, s3_path)

        # Eventual consistency delay
        time.sleep(5)

        return s3_path

    def create_temp_file_with_text(self, text, file_extension):
        """
        Creates a temporary file with the specified extension and writes the given text.
        """
# Prepare the output filename with the current date and time if not provided
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        local_dir = os.getenv('DIR_STORAGE', './downloads')
        if not os.path.exists(local_dir):
            os.makedirs(local_dir)  # Create the directory if it doesn't exist
        write_file_path = f"{local_dir}/{current_time}.{file_extension}"
        
        try:
            with open(write_file_path, "a") as f:
                f.write(text + "\n")  # Append a newline for separation between entries
                f.close()
        except Exception as e:
            print(f"Error writing to {write_file_path}: {e}")        
       
        return write_file_path

    def parse_s3_path(self, s3_path):
        """
        Parses an S3 path into bucket name, prefix, and filename.
        """
        if s3_path.startswith("s3://"):
            s3_path = s3_path[5:]

        parts = s3_path.split("/", 1)
        bucket_name = parts[0]

        if len(parts) > 1:
            prefix_and_filename = parts[1]
            if "/" in prefix_and_filename:
                last_slash_index = prefix_and_filename.rfind("/")
                prefix = prefix_and_filename[:last_slash_index + 1]
                filename = prefix_and_filename[last_slash_index + 1:]
            else:
                prefix = ''
                filename = prefix_and_filename
        else:
            prefix = ''
            filename = ''

        return bucket_name, prefix, filename

    def get_file_extension(self, s3_path):
        """
        Extracts the file extension from the S3 path.
        """
        if s3_path and '.' in s3_path:
            return s3_path.split('.')[-1]
        else:
            return ''
