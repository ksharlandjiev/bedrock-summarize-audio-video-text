import os
import json
from handlers.abstract_handler import AbstractHandler

class AmazonComprehendPIIUntokenizeHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        self.storage_dir = os.getenv('DIR_STORAGE', './')

        print("Starting PII Untokenization...")
        try:
            token_map_file = request.get("token_map", None)
            if token_map_file is None:
                raise ValueError("Token map is missing, have you forgotten to tokenize first?")

            text = request.get("text", None)
            token_map = self.load_token_map(token_map_file)
            untokenized_text = self.replace_tokens_with_pii(text, token_map)

            # Update the request with the untokenized text
            request.update({"text": untokenized_text})
                        
        except Exception as e:
            print(f"Error during untokenization: {e}")
            raise

        return super().handle(request)

    def load_token_map(self, file_path):
        """
        Loads the token map from a file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Token map file {file_path} not found.")
        with open(file_path, 'r') as file:
            token_map = json.load(file)
        return token_map

    def replace_tokens_with_pii(self, text, token_map):
        """
        Replaces tokens in text with original PII values.
        """
        
        for token, pii_value in token_map.items():
            text = text.replace(token, pii_value)
        return text
