from handlers.abstract_handler import AbstractHandler
from utils.aws_boto_client_manager import AWSBotoClientManager

class AmazonComprehendPIIHandler(AbstractHandler):

    def handle(self, request: dict) -> dict:
        self.comprehend = AWSBotoClientManager.get_client('comprehend')

        print("Starting PII Detection...")
        text = request.get("text", None)

        # Handle large text by splitting it into chunks
        pii_tokens = self.process_text_in_chunks(text)

        # Update the request with the PII tokens
        request.update({"pii_tokens": pii_tokens})

        return super().handle(request)

    def process_text_in_chunks(self, text):
        """
        Process text in chunks to avoid hitting the size limit of Comprehend API.
        """
        max_length = 5000  # character length, adjust based on average byte size of your text encoding
        chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
        all_pii_tokens = []

        for chunk in chunks:
            pii_tokens = self.detect_and_tokenize_pii(chunk)
            all_pii_tokens.extend(pii_tokens)

        return all_pii_tokens

    def detect_and_tokenize_pii(self, text):
        """
        Detects and tokenizes PII data in the given text using Amazon Comprehend.
        """
        pii_entities = self.comprehend.detect_pii_entities(Text=text, LanguageCode='en')
        print(pii_entities)
        pii_tokens = []
        for entity in pii_entities['Entities']:
            start = entity['BeginOffset']
            end = entity['EndOffset']
            pii_tokens.append({
                "text": text[start:end],
                "type": entity['Type']
            })
        return pii_tokens
