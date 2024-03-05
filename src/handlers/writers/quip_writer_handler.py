from dotenv import load_dotenv
import os
import urllib.request
import urllib.parse
import json
from urllib.error import HTTPError, URLError


from handlers.abstract_handler import AbstractHandler

# Load environment variables from .env file
load_dotenv()

class QuipWriterHandler(AbstractHandler):
    def handle(self, request: dict) -> dict:
        print(f"Writing  to Quip...")
        text = request.get("text", None)

        try:
          folder_id = os.getenv("QUIP_DEFAULT_FOLDER_ID",None)
          result = self.write_document(text, folder_id)
          request.update({"status": True, "text": result})
        except Exception as e: 
            request.update({"status": False, "error":str(e)})        

        return super().handle(request)

    def write_document2(self, content: str, folder_id: str = None, document_id: str = None) -> dict:
        """
        Writes content to a new or existing Quip document.
        If document_id is provided, updates the existing document; otherwise, creates a new document in the specified folder.
        """
        quip_token = os.getenv('QUIP_TOKEN')
        quip_endpoint = os.getenv('QUIP_ENDPOINT', 'https://platform.quip.com/')
        default_folder_id = os.getenv('QUIP_DEFAULT_FOLDER_ID')  # New env variable for default folder
        
        if not folder_id and not document_id:
            folder_id = default_folder_id  # Use default folder if none specified
        
        if not quip_token:
            raise ValueError("QUIP_TOKEN environment variable is not set.")

        headers = {'Authorization': f'Bearer {quip_token}'}

        
        data = {
            'format': 'html',
            'type': 'document',
            'title': 'test123',
            'content': "<h1>Hello World</h1><br/><b>This is test</b>",
            'member_ids': folder_id
        }

        if document_id:
            # Update existing document
            url = f"{quip_endpoint}/1/threads/{document_id}"
            request = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        else:
            # Create new document in specified folder
            url = f"{quip_endpoint}/1/threads/new-document"
            
            data['folder_id'] = folder_id
            request = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')        
        print(request)
        request.add_header("Content-Type","application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(request) as response:
                print(response)
                response_body = response.read()
                return json.loads(response_body)
        except HTTPError as e:
            raise Exception(f"HTTP Error encountered: {e.code} - {e.reason}")
        except URLError as e:
            raise Exception(f"URL Error encountered: {e.reason}")

    def write_document(self, content: str, folder_id=os.getenv('QUIP_DEFAULT_FOLDER_ID', None), document_id: str = None) -> dict:
        """
        Writes content to a new or existing Quip document.
        If document_id is provided, updates the existing document; otherwise, creates a new document in the specified folder.
        Includes additional fields as per cURL example.
        """
        quip_token = os.getenv('QUIP_TOKEN')
        quip_endpoint = os.getenv('QUIP_ENDPOINT', 'https://platform.quip.com/')
        
        if not quip_token:
            raise ValueError("QUIP_TOKEN environment variable is not set.")

        headers = {
            'Authorization': f'Bearer {quip_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'content': content,
            'format': 'html',
            'member_ids': folder_id,
            'type': 'document'
        }

        if document_id:
            # Intended for updates, but Quip may not support updating content via the same method.
            # This example assumes creation of new documents primarily.
            raise NotImplementedError("Document update functionality needs verification with the Quip API.")
        else:
            # Create new document
            url = f"{quip_endpoint}/1/threads/new-document"
            encoded_data = urllib.parse.urlencode(data).encode('utf-8')
            request = urllib.request.Request(url, data=encoded_data, headers=headers)

        try:
            with urllib.request.urlopen(request) as response:
                response_body = response.read()
                return json.loads(response_body)
        except HTTPError as e:
            raise Exception(f"HTTP Error encountered: {e.code} - {e.reason}")
        except URLError as e:
            raise Exception(f"URL Error encountered: {e.reason}")


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
