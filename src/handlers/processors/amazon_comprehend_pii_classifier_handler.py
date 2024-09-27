from handlers.abstract_handler import AbstractHandler
from utils.aws_boto_client_manager import AWSBotoClientManager

class AmazonComprehendPIIClassifierHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        self.comprehend = AWSBotoClientManager.get_client('comprehend')
        
        print("Starting PII Classification...")
        text = request.get("text", None)
        
        # Process the text to check for PII
        is_pii, pii_types = self.classify_pii(text)
                # Update the request with PII detection results
        request.update({
            "is_pii": is_pii,
            "detected_pii": pii_types
        })
        
        return super().handle(request)

    def classify_pii(self, text):
        """
        Classifies text to detect PII and identify the types of PII found.
        """
        max_length = 5000  # character length, adjust based on the encoding
        chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
        detected_pii_types = set()

        for chunk in chunks:
            pii_entities = self.detect_pii(chunk)
            for entity in pii_entities['Entities']:
                detected_pii_types.add(entity['Type'])

        is_pii_detected = len(detected_pii_types) > 0
        return is_pii_detected, list(detected_pii_types)

    def detect_pii(self, text):
        """
        Detects PII data in the given text using Amazon Comprehend.
        """
        return self.comprehend.detect_pii_entities(Text=text, LanguageCode='en')
