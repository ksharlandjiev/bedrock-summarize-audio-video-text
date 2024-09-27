import os
import json
import urllib.request
from urllib.error import HTTPError, URLError
from handlers.abstract_handler import AbstractHandler
from utils.web_utils import clean_html

class QuipReaderHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        # Extract the document ID from the request path with the "quip://" prefix
        path = request.get("path")
        document_id = self.parse_quip_path(path)
        
        print(f"Reading content from Quip document: {document_id}")

        # Retrieve the document content
        document_content, document_link = self.get_document(document_id)
        # Determine the write file path and output folder
        write_file_path = request.get("write_file_path", None)
        if write_file_path:
            base_folder = os.path.dirname(write_file_path)
            file_id = os.path.basename(write_file_path).split('.')[0]
            output_folder = os.path.join(base_folder, file_id)
            media_folder = os.path.join(output_folder, "media")
            os.makedirs(media_folder, exist_ok=True)

        # Initialize the metadata dictionary
        if "metadata" not in request:
            request["metadata"] = {}

        # Initialize variables for media extraction
        media_files = []

        # Extract media if requested
        if request.get("extract_media", False):
            media_files.extend(self.extract_media(document_id, document_content, media_folder))

        # Clean the document content to extract text
        document_text = clean_html(document_content)

        # Save the cleaned text content to a file
        transcript_file_path = os.path.join(output_folder, 'transcript.txt')
        with open(transcript_file_path, 'w') as transcript_file:
            transcript_file.write(document_text)

        # Create metadata with traceability for graph database
        metadata = {
            "original_file": document_link,
            "transcript_file": transcript_file_path,
            "media_files": media_files
        }
        
        # Save metadata to a json file
        metadata_file_path = os.path.join(output_folder, 'metadata.json')
        with open(metadata_file_path, 'w') as metadata_file:
            json.dump(metadata, metadata_file, indent=4)

        # Update the request metadata with the new metadata
        request["metadata"][document_link] = metadata

        # Update the request with the extracted text
        request.update({"text": document_text})

        # Call the next handler in the chain
        return super().handle(request)

    def parse_quip_path(self, quip_path: str) -> str:
        """
        Parses the Quip document ID from the quip_path and returns it.
        Assumes quip_path format is "quip://<document_id>"
        """
        prefix = "quip://"
        if quip_path.startswith(prefix):
            return quip_path[len(prefix):]
        else:
            raise ValueError("Invalid Quip path format")

    def get_document(self, document_id):
        quip_token = os.getenv('QUIP_TOKEN')
        quip_endpoint = os.getenv('QUIP_ENDPOINT', 'https://platform.quip.com')
        if not quip_token:
            raise ValueError("QUIP_TOKEN environment variable is not set.")

        # Construct the URL for the document content endpoint
        url = f"{quip_endpoint}/1/threads/{document_id}"
        
        # Set up the headers with authorization
        headers = {
            'Authorization': f'Bearer {quip_token}'
        }
        
        # Create a request object with headers
        request = urllib.request.Request(url, headers=headers)

        try:
            # Make the GET request to the Quip API
            with urllib.request.urlopen(request) as response:
                # Assuming the content is JSON and the relevant part of the document is in the 'html' key
                # This might need adjustment based on the actual structure of the response
                response_body = response.read()
                document_data = json.loads(response_body)
                
                return document_data['html'], document_data['thread']['link']  # Adjust the key based on the actual response structure
        except HTTPError as e:
            # Handle HTTP errors
            raise Exception(f"HTTP Error encountered: {e.code} - {e.reason}")
        except URLError as e:
            # Handle URL errors (e.g., network issues)
            raise Exception(f"URL Error encountered: {e}")

    def extract_media(self, document_id: str, document_content: str, media_folder: str) -> list:
        """
        Extracts media files from the document content and saves them in the media folder.
        Returns a list of metadata about the extracted media files.
        """
        media_files = []
        import re

        quip_token = os.getenv('QUIP_TOKEN')
        quip_endpoint = os.getenv('QUIP_ENDPOINT', 'https://platform.quip.com')
        if not quip_token:
            raise ValueError("QUIP_TOKEN environment variable is not set.")

        img_tags = re.findall(r'<img[^>]+src=\'(/blob/[^\'"]+)\'', document_content)
        for idx, img_url in enumerate(img_tags):
            img_blob_url = f"{quip_endpoint}/1/blob/{img_url.split('/blob/')[1]}"
            img_file_name = f"image_{idx}.jpg"
            img_file_path = os.path.join(media_folder, img_file_name)
            try:
                headers = {
                    'Authorization': f'Bearer {quip_token}'
                }
                request = urllib.request.Request(img_blob_url, headers=headers)
                with urllib.request.urlopen(request) as response:
                    with open(img_file_path, "wb") as f:
                        f.write(response.read())
                media_files.append({"type": "image", "path": img_file_path, "source_url": img_blob_url})
            except Exception as e:
                print(f"Failed to download image from {img_blob_url}: {e}")

        # Similar extraction logic can be applied for videos and audios if their tags/URLs can be identified.
        # Example (pseudo-code):
        # video_tags = re.findall(r'<video[^>]+src=\'(/blob/[^\'"]+)\'', document_content)
        # audio_tags = re.findall(r'<audio[^>]+src=\'(/blob/[^\'"]+)\'', document_content)
        # Iterate over video_tags and audio_tags similar to img_tags above.

        return media_files
