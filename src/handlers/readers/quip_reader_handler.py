import os
from handlers.abstract_handler import AbstractHandler

import urllib.request
import json
from urllib.error import HTTPError, URLError
from utils.web_utils import clean_html



class QuipReaderHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        # Extract the document ID from the request path with the "quip://" prefix
        path = request.get("path")
        document_id = self.parse_quip_path(path)
        
        print(f"Reading content from Quip document: {document_id}")

        # Retrieve the document content
        document_content = self.get_document(document_id)
        document_text = clean_html(document_content)
        # Update request with the document content
        request.update({"text": document_text})
        
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
                return document_data['html']  # Adjust the key based on the actual response structure
        except HTTPError as e:
            # Handle HTTP errors
            raise Exception(f"HTTP Error encountered: {e.code} - {e.reason}")
        except URLError as e:
            # Handle URL errors (e.g., network issues)
            raise Exception(f"URL Error encountered: {e}")