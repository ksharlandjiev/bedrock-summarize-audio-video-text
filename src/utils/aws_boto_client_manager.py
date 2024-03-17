import os
import boto3
from botocore.config import Config

class AWSBotoClientManager:
    _clients = {}

    @classmethod
    def get_client(cls, service_name):
     
        AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        my_config = Config(region_name=AWS_DEFAULT_REGION)
                
        if service_name not in cls._clients:
            cls._clients[service_name] = boto3.client(service_name, config=my_config)
        return cls._clients[service_name]
