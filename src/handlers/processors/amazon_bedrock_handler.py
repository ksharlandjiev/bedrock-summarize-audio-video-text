from utils.bedrock import invoke_model
from handlers.abstract_handler import AbstractHandler
import botocore.exceptions

class AmazonBedrockHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        text = request.get("text", None)
        print("Summarizing text with Bedrock. Text Len:", len(text))
        
        summary = self.summarize_with_retry(text)
        
        request.update({"text": summary})
        return super().handle(request)

    def summarize_with_retry(self, text: str) -> str:
        try:
            return invoke_model(text)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ValidationException':
                return self.chunk_and_summarize(text)
            else:
                raise e

    def chunk_and_summarize(self, text: str) -> str:
        max_attempts = 10
        num_chunks = 2
        attempt = 0
        print("Retrying summarization of text with Bedrock with chunking")

        while attempt < max_attempts:
            chunks = self.split_text(text, num_chunks)
            try:
                summaries = [invoke_model(chunk) for chunk in chunks]
                return "\n".join(summaries)
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'ValidationException':
                    num_chunks *= 2  # Increase the number of chunks
                    attempt += 1
                    print(f"Attempt {attempt}: Splitting text into {num_chunks} chunks")
                else:
                    raise e
        
        raise RuntimeError("Failed to summarize text due to input length constraints after multiple attempts.")

    def split_text(self, text: str, num_chunks: int) -> list:
        """
        Splits the text into the specified number of chunks, respecting word boundaries.
        """
        avg_chunk_length = len(text) // num_chunks
        chunks = []
        start = 0
        
        for _ in range(num_chunks - 1):
            end = start + avg_chunk_length
            while end < len(text) and text[end] != ' ':
                end += 1
            chunks.append(text[start:end].strip())
            start = end
        
        chunks.append(text[start:].strip())
        return chunks
