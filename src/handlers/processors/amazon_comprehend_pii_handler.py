from handlers.abstract_handler import AbstractHandler
from utils.aws_boto_client_manager import AWSBotoClientManager

class AmazonComprehendPIIHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        
        self.comprehend = AWSBotoClientManager.get_client('comprehend')

        print("Starting PII Detection...")
        text = request.get("text", None)
        pii_tokens = self.detect_and_tokenize_pii(text)
        # Update the request with the PII tokens
        request.update({"pii_tokens": pii_tokens})

        return super().handle(request)

    def detect_and_tokenize_pii(self, text):
        """
        Detects and tokenizes PII data in the given text using Amazon Comprehend.
        """
        pii_entities = self.comprehend.detect_pii_entities(Text=text, LanguageCode='en')
        pii_tokens = []
        for entity in pii_entities['Entities']:
            start = entity['BeginOffset']
            end = entity['EndOffset']
            pii_tokens.append({
                "text": text[start:end],
                "type": entity['Type']
            })
        return pii_tokens