import spacy
import os
from handlers.abstract_handler import AbstractHandler

class AnonymizeHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
      print("Starting Anonymization...")
      replacement = os.environ.get("ANONYMIZE_CUSTOMER_NAME_REPLACEMENT", '[Customer]')
      text = request.get("text", None)
      anonymized_text = self.anonymize_text(text, replacement)
      # updating the request body and adding the anonymized text.
      request.update({"text": anonymized_text})
      
      return super().handle(request)
    
    def anonymize_text(self, text, replacement="[Customer]"):
        """
        Anonymizes entities in the given text by replacing them with a specified replacement.
        """

        # Load the spaCy model
        nlp = spacy.load("en_core_web_sm")

        doc = nlp(text)
        anonymized_text = text
        for ent in doc.ents:
            if ent.label_ == "ORG":
                anonymized_text = anonymized_text.replace(ent.text, replacement)
        return anonymized_text    