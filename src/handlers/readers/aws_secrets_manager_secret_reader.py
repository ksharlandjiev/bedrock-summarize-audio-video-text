from handlers.abstract_handler import AbstractHandler
import boto3
from botocore.exceptions import ClientError

from utils.aws_boto_client_manager import AWSBotoClientManager

class AWSSecretsManagerSecretReader(AbstractHandler):
    def handle(self, request: dict) -> dict:
        secret_name = request.get("aws_secret_name")

        if not secret_name :
            print("AWS secret name not provided in the request.")
            return request

        print(f"Retrieving secret '{secret_name}' from AWS Secrets Manager")
        
        # Retrieve secret from AWS Secrets Manager
        secret_values = self.get_secret(secret_name)

        if secret_values:
            # Merge the secret values into the request object
            request.update(secret_values)
            print("Secret values merged into the request.")

        return super().handle(request)

    def get_secret(self, secret_name):
        """
        Retrieve the secret from AWS Secrets Manager.
        """
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = AWSBotoClientManager.get_client('secretsmanager')
        
        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            print(f"Unable to retrieve secret: {e}")
            return None
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return eval(secret)  # Safely convert string to dictionary
        else:
            print("Secret is binary, which is not handled in this example.")
            return None

