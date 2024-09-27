import json
import uuid
from handlers.abstract_handler import AbstractHandler
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import os

from utils.aws_boto_client_manager import AWSBotoClientManager

class AmazonDataZoneAssetWriterHandler(AbstractHandler):

    def handle(self, request: dict) -> dict:
        domain_id = os.getenv("DATAZONE_DOMAIN_ID")
        project_id = os.getenv("DATAZONE_PROJECT_ID")
        revision = os.getenv("DATAZONE_METADATA_REVISION")
        asset_revision = os.getenv("DATAZONE_ASSET_TYPE_REVISION")
        metadata = request


        # Validate necessary information is available
        if not domain_id or not project_id or not metadata:
            raise ValueError("Missing domainId, projectId, or metadata in the request.")

        # Generate unique client token
        client_token = str(uuid.uuid4())

        # Construct the content for the asset creation request
        content = {
            "file_type": metadata.get("file_type"),
            "original_file": metadata.get("original_file"),
            "is_pii": metadata.get("is_pii"),
            "summary": metadata.get("summary"),
            "category": metadata.get("category"),
            "detected_pii": ', '.join(metadata.get("detected_pii", [])),
            "transcript_file": metadata.get("transcript_file"),
            "tags": ', '.join(metadata.get("tags", [])),
            "entities": ', '.join(metadata.get("entities", [])),
            "key_phrases": ', '.join(metadata.get("key_phrases", []))
        }

        # Construct the asset creation request
        asset_request = {
            "clientToken": client_token,
            "domainIdentifier":domain_id,
            "description": metadata.get("title", "N/A"),
            "formsInput": [
                {
                    "formName": "unstructured_data",
                    "typeIdentifier": "unstructured_data",
                    "content": json.dumps(content)
                    
                }, 
                {
                    "content": json.dumps({"readMe": metadata.get("summary")}),
                    "formName": "AssetCommonDetailsForm"
                }
            ],
            "name": metadata.get("original_file").split('/')[-1],  # Extract the file name
            "owningProjectIdentifier": project_id,
            "typeIdentifier": "unstructured",
        }
        # print("Request: ", json.dumps(asset_request, indent=2))
        # Send the request to the DataZone API
        try:
            datazone_client = AWSBotoClientManager.get_client("datazone")
            response = datazone_client.create_asset(**asset_request)
            print("Asset created successfully:", response)
            try: 
                publish_request = {
                    "action": "PUBLISH",
                    "domainIdentifier": domain_id,
                    "entityIdentifier": response.get("id"),
                    "entityRevision": response.get("revision"),
                    "entityType": "ASSET"
                }
                # print("Publishing listing change set:", publish_request)
                
                datazone_client.create_listing_change_set(**publish_request)

            except (BotoCoreError, ClientError) as error:
                print("Error publishing listing change set:", error)
        except (BotoCoreError, ClientError) as error:
            print("Error creating asset:", error, asset_request)
            raise error

        return super().handle(request)

