import os
import json
from PIL import Image
from io import BytesIO
from handlers.abstract_handler import AbstractHandler
from utils.aws_boto_client_manager import AWSBotoClientManager

class AmazonRekognitionHandler(AbstractHandler):

    def handle(self, request: dict) -> dict:
        # Ensure metadata exists in the request
        if "metadata" not in request:
            return super().handle(request)

        # Initialize Amazon Rekognition client using the provided AWSBotoClientManager
        rekognition_client = AWSBotoClientManager.get_client('rekognition')

        # Iterate through all files in the metadata
        for original_path, metadata in request["metadata"].items():
            # Process each media file in the metadata
            for media_file in metadata.get("media_files", []):
                print(f"Processing {media_file['path']}")
                if media_file["type"] == "image":
                    self.process_image(media_file, rekognition_client)
        
        # Call the next handler in the chain
        return super().handle(request)

    def process_image(self, media_file: dict, rekognition_client):
        # Read the image content
        image_path = media_file["path"]
        with open(image_path, 'rb') as image_file:
            image_bytes = image_file.read()

        # Ensure the image is in a supported format
        image_bytes = self.ensure_supported_format(image_bytes)

        # Call Amazon Rekognition to detect labels
        response = rekognition_client.detect_labels(Image={'Bytes': image_bytes})

        # Extract relevant data
        labels_info = []
        for label in response['Labels']:
            label_info = {
                "Name": label["Name"],
                "Aliases": label.get("Aliases", []),
                "Categories": label.get("Categories", [])
            }
            labels_info.append(label_info)
        
        # Enrich the media file metadata
        media_file["labels"] = labels_info

    def ensure_supported_format(self, image_bytes: bytes) -> bytes:
        try:
            image = Image.open(BytesIO(image_bytes))
            if image.format not in ['JPEG', 'PNG']:
                # Convert image to JPEG
                buffer = BytesIO()
                image = image.convert('RGB')  # Ensure image is in RGB mode
                image.save(buffer, format='JPEG')
                return buffer.getvalue()
            else:
                return image_bytes
        except Exception as e:
            raise ValueError(f"Error processing image: {e}")
