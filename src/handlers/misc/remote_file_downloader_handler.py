import os
import urllib.request
import boto3
from handlers.abstract_handler import AbstractHandler

class RemoteFileDownloaderHandler(AbstractHandler):

    def handle(self, request: dict) -> dict:        
        file_path = request.get("path")
        print("Downloading file from: ", file_path)
        
        if file_path.startswith(('http', 'https')):
            local_path = self.download_from_http(file_path)
        elif file_path.startswith('s3://'):
            local_path = self.download_from_s3(file_path)
        
            
        # Update the request with the local path of the downloaded file
        request.update({"path": local_path})

        return super().handle(request)

        # Update the request with the path of the downloaded file
        request["path"] = local_path
        return super().handle(request)

    def download_from_http(self, url):
        local_filename = url.split('/')[-1]
        local_path = os.path.join(os.getenv('DIR_STORAGE', './downloads'), local_filename)
        urllib.request.urlretrieve(url, local_path)
        return local_path

    def download_from_s3(self, s3_url):
        # Extract bucket name and object key from the s3 URL
        path_parts = s3_url.replace("s3://", "").split('/')
        bucket_name = path_parts[0]
        object_key = '/'.join(path_parts[1:])
        local_filename = object_key.split('/')[-1]
        local_path = os.path.join(os.getenv('DIR_STORAGE', './downloads'), local_filename)

        s3_client = boto3.client('s3')
        s3_client.download_file(bucket_name, object_key, local_path)
        return local_path