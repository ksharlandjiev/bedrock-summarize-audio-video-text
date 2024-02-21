# src/anonymization.py
import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def anonymize_text(text, replacement="[Customer]"):
    """
    Anonymizes entities in the given text by replacing them with a specified replacement.
    """
    doc = nlp(text)
    anonymized_text = text
    for ent in doc.ents:
        if ent.label_ == "ORG":
            anonymized_text = anonymized_text.replace(ent.text, replacement)
    return anonymized_text
