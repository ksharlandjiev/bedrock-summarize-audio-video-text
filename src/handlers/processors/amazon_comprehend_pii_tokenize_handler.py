import os
import json
from handlers.abstract_handler import AbstractHandler
from utils.aws_boto_client_manager import AWSBotoClientManager

class AmazonComprehendPIITokenizeHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        self.comprehend = AWSBotoClientManager.get_client('comprehend')
        self.storage_dir = os.getenv('DIR_STORAGE', './')  # Defaulting to current directory if not specified
        self.token_prefix = "T"  # Prefix for tokens
        self.token_counter = 1  # Starting point for token counter
        
        print("Starting PII Tokenization for specific types with shorter tokens...")
        text = request.get("text", None)
        
        pii_tokens, token_map = self.tokenize_pii(text)
        
        # Update the request with the tokenized text
        tokenized_text = self.replace_pii_with_tokens(text, pii_tokens)
        request.update({"text": tokenized_text})

        token_map_file = self.store_token_map(token_map)
        request.update({"token_map": token_map_file})        
        
        return super().handle(request)

    def generate_token(self):
        """
        Generates a new, shorter token.
        """
        token = f"{self.token_prefix}{self.token_counter}"
        self.token_counter += 1
        return token

    def tokenize_pii(self, text):
        """
        Detects and tokenizes specific PII data types in the given text using Amazon Comprehend.
        Filters for name, company name, phone, email, and address.
        """
        pii_entities = self.comprehend.detect_pii_entities(Text=text, LanguageCode='en')
        pii_tokens = []
        token_map = {}
        allowed_types = ['NAME', 'DATE', 'ADDRESS', 'PHONE', 'EMAIL']
        for entity in pii_entities['Entities']:
            if entity['Type'] in allowed_types:
                start = entity['BeginOffset']
                end = entity['EndOffset']
                pii_text = text[start:end]

                # Check if the PII text already has a token
                token = next((t for t, v in token_map.items() if v == pii_text), None)
                if not token:  # If not, generate a new token
                    token = self.generate_token()
                    token_map[token] = pii_text
                
                pii_tokens.append((start, end, token))
        return pii_tokens, token_map

    def replace_pii_with_tokens(self, text, pii_tokens):
        """
        Replaces PII in text with tokens.
        """
        tokenized_text = text
        offset = 0
        for start, end, token in pii_tokens:
            tokenized_text = tokenized_text[:start + offset] + token + tokenized_text[end + offset:]
            offset += len(token) - (end - start)
        return tokenized_text

    def store_token_map(self, token_map):
        """
        Stores the token map in a JSON file and returns the file path.
        """
        file_path = os.path.join(self.storage_dir, f"token_map_{self.generate_token()}.json")
        with open(file_path, 'w') as file:
            json.dump(token_map, file)
        return file_path
