from handlers.abstract_handler import AbstractHandler
from utils.aws_boto_client_manager import AWSBotoClientManager

class AmazonComprehendInsightsHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        
        self.comprehend = AWSBotoClientManager.get_client('comprehend')
        self.max_bytes = 3000  # Amazon Comprehend's size limit of 5000kb for various operations
        
        print("Extracting insights from text...")
        text = request.get("text", None)    
        
        if text:
            text_chunks = self.chunk_text(text)
            sentiments = [self.detect_sentiment(chunk) for chunk in text_chunks]
            entities = []
            key_phrases = []
            for chunk in text_chunks:
                entities.extend(self.detect_entities(chunk))
                key_phrases.extend(self.detect_key_phrases(chunk))
            
            # Aggregate the insights and append to the request object
            aggregated_data = {
                "sentiment": max(set(sentiments), key=sentiments.count),  # Aggregation by most frequent sentiment
                "entities": entities,  # Entities from all chunks
                "key_phrases": key_phrases  # Key phrases from all chunks
            }

            # updating the request body and adding the aggregated data.
            request.update({"text": aggregated_data})
            
        else:
            print("No text provided for insights extraction.")

        return super().handle(request)

    def chunk_text(self, text):
        """
        Breaks the text into chunks, each within the Amazon Comprehend size limit.
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0

        for word in words:
            word_size = len(word.encode('utf-8'))
            if current_size + word_size <= self.max_bytes:
                current_chunk.append(word)
                current_size += word_size
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = word_size
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def detect_sentiment(self, text):
        """
        Detects the sentiment of the given text using Amazon Comprehend.
        """
        try:
            response = self.comprehend.detect_sentiment(Text=text, LanguageCode='en')
            return response.get("Sentiment")
        except Exception as e:
            print(f"Error detecting sentiment: {e}")
            return None

    def detect_entities(self, text):
        """
        Detects entities in the given text using Amazon Comprehend.
        """
        try:
            response = self.comprehend.detect_entities(Text=text, LanguageCode='en')
            entities = response.get("Entities")
            return [{"Text": entity["Text"], "Type": entity["Type"], "Score": entity["Score"]} for entity in entities]
        except Exception as e:
            print(f"Error detecting entities: {e}")
            return []

    def detect_key_phrases(self, text):
        """
        Detects key phrases in the given text using Amazon Comprehend.
        """
        try:
            response = self.comprehend.detect_key_phrases(Text=text, LanguageCode='en')
            key_phrases = response.get("KeyPhrases")
            return [{"Text": phrase["Text"], "Score": phrase["Score"]} for phrase in key_phrases]
        except Exception as e:
            print(f"Error detecting key phrases: {e}")
            return []

