# handlers/processors/textract_handler.py

import sys
import time
from handlers.abstract_handler import AbstractHandler
from utils.aws_boto_client_manager import AWSBotoClientManager

class AmazonTextractHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        self.textract_client = AWSBotoClientManager.get_client('textract')
        self.s3_client = AWSBotoClientManager.get_client('s3')

        path = request.get('path')
        bucket, key = self._parse_s3_path(path)

        if path:
            print(f"Processing document with Amazon Textract: {path}")
            if path.startswith('s3://'):
                
                if key.endswith('.pdf'):
                    text =  self._process_pdf(bucket, key)
                else:
                    text =  self._process_image(bucket, key)                
            else:
                text =  self._extract_text_local(path)
            
            # updating the request body and adding the transcribed text.
            request.update({"text": text})
        
        return super().handle(request)

    def _parse_s3_path(self, s3_path):
        _, _, bucket, *key = s3_path.split('/', 3)
        return bucket, '/'.join(key)

    def _is_pdf_file(self, key):
        return key.lower().endswith('.pdf')

    def _process_image(self, bucket, key):
        # Original synchronous image processing logic remains unchanged
        response = self.textract_client.detect_document_text(
            Document={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        return self.parse_detect_document_text_response(response)

    def _process_pdf(self, bucket, key):
        # Start an asynchronous job for a PDF document
        response = self.textract_client.start_document_text_detection(
            DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': key}}
        )
        job_id = response['JobId']
        print(f"Started job with id: {job_id}")

        # Polling the job status
        while True:
            status_response = self.textract_client.get_document_text_detection(JobId=job_id)
            status = status_response['JobStatus']
            if status in ['SUCCEEDED', 'FAILED']:
                break
            time.sleep(5)  # Sleep between polls

        if status == 'SUCCEEDED':
            return self._parse_async_response(status_response, job_id)
        else:
            return {'Error': 'Document text detection failed'}

    def parse_detect_document_text_response(self, response):
        """
        Parses the response from Textract to reconstruct and concatenate text from lines and words.
        """
        # Initialize a dictionary to hold lines and words
        lines = {}
        words = {}

        # First pass: collect words and lines
        for block in response.get('Blocks', []):
            block_id = block.get('Id')
            block_type = block.get('BlockType')
            
            if block_type == 'WORD':
                words[block_id] = block.get('Text', '')
            elif block_type == 'LINE':
                # Lines will hold word IDs to reconstruct the text
                lines[block_id] = [relationship.get('Ids', []) for relationship in block.get('Relationships', []) if relationship['Type'] == 'CHILD']

        # Second pass: reconstruct lines from words
        reconstructed_lines = []
        for line_id, word_ids_list in lines.items():
            for word_ids in word_ids_list:
                line_text = ' '.join([words[word_id] for word_id in word_ids])
                reconstructed_lines.append(line_text)

        # Join all lines into a single text
        full_text = '\n'.join(reconstructed_lines)
        return full_text
    
    def _extract_text_local(self, path): 
        with open(path, 'rb') as document:
            try:
                response = self.textract_client.detect_document_text(
                    Document={'Bytes': document.read()}
                )
            except Exception as e:     
                print(e)
                print("Currently Amazon Textract does not support processing local pdf files. Consider uploading this in S3 first.")
                sys.exit()
            
        return self.parse_detect_document_text_response(response)

    def _parse_async_response(self, initial_response, job_id):
        # Initialize result pages list
        pages = []

        # Fetching all pages of results
        next_token = None
        while True:
            response_options = {
                'JobId': job_id
            }
            if next_token:
                response_options['NextToken'] = next_token

            response = self.textract_client.get_document_text_detection(**response_options)

            pages.extend(response.get('Blocks', []))

            next_token = response.get('NextToken', None)
            if not next_token:
                break

        # Extract text from blocks
        text = ''
        for block in pages:
            if block['BlockType'] == 'LINE':
                text += block['Text'] + '\n'

        return text