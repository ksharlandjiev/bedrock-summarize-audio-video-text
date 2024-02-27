import os
import sys
from typing import Any
from dotenv import load_dotenv
from handlers.abstract_handler import AbstractHandler
from handlers.handler import Handler
from handlers.readers.youtube_reader_handler import YouTubeReaderHandler
from handlers.processors.amazon_transcribe_handler import AmazonTranscriptionHandler
from handlers.readers.pdf_reader_handler import PDFReaderHandler
from handlers.readers.local_file_reader_handler import LocalFileReaderHandler
from handlers.writers.local_file_writer_handler import LocalFileWriterHandler
from handlers.processors.prompt_handler import PromptHandler
from handlers.processors.amazon_bedrock_handler import AmazonBedrockHandler
from handlers.readers.amazon_s3_reader_handler import AmazonS3ReaderHandler
from handlers.writers.amazon_s3_writer_handler import AmazonS3WriterHandler
from handlers.processors.anonymize_handler import AnonymizeHandler
from handlers.processors.amazon_textract_handler import AmazonTextractHandler
from handlers.writers.clipboard_writer_handler import ClipboardWriterHandler
from handlers.readers.http_handler import HTTPHandler
import utils


# Load environment variables from .env file
load_dotenv()

def determine_input_type(file_path):
    if "youtube" in file_path or "youtu.be" in file_path:
        return "youtube_url"
    elif file_path.startswith(('http')):
        return "http"    
    elif file_path.startswith(('s3://')):
        return "s3"    
    elif file_path.endswith(('.mp3', '.mp4', '.m4a', '.wav', '.flac', '.mov', '.avi')):
        return "multimedia_file"
    elif file_path.endswith('.pdf'):
        return "pdf"
    elif file_path.endswith(('.jpg', '.jpeg', '.png', '.tiff')):
        return "image_file"    
    elif file_path.endswith(('.txt', '.json')):
        return "text_or_json"
    else:
        return "unsupported"

def construct_chain(input_type):
    # Initialize handlers
    youtube_handler = YouTubeReaderHandler()
    transcription_handler = AmazonTranscriptionHandler()
    pdf_handler = PDFReaderHandler()
    local_file_reader_handler = LocalFileReaderHandler()
    local_file_writer_handler = LocalFileWriterHandler()
    prompt_handler = PromptHandler()
    bedrock_handler = AmazonBedrockHandler()
    s3reader_handler = AmazonS3ReaderHandler()
    s3writer_handler = AmazonS3WriterHandler()
    http_handler = HTTPHandler()
    textract_handler = AmazonTextractHandler()

    # Use if-elif-else to construct the appropriate chain. In Python 3.10 we could use match statement.
    if input_type == "youtube_url":
        chain = youtube_handler
        current_handler = youtube_handler.set_next(s3writer_handler).set_next(transcription_handler)
    elif input_type == "multimedia_file":
        chain = s3writer_handler
        current_handler = s3writer_handler.set_next(transcription_handler)
    elif input_type == "image_file":
        chain = local_file_reader_handler
        current_handler = local_file_reader_handler.set_next(textract_handler)        
    elif input_type == "pdf":
        chain = pdf_handler
        current_handler = pdf_handler 
    elif input_type == "http":
        chain = http_handler
        current_handler = http_handler        
    elif input_type == "text_or_json":
        chain = local_file_reader_handler
        current_handler = local_file_reader_handler
    elif input_type == "s3":
        chain = s3reader_handler
        current_handler = s3reader_handler.set_next(local_file_reader_handler)
    elif input_type == "custom":
        return construct_custom_chain() # for testing only
            # construct and return a custom chain.    
    else:
        # For unsupported types, default to just summarization_handler
        print("Unsupported file type.", input_type)
        sys.exit(1)
    
    # Anonymize data?
    anonymize = os.getenv('ANONYMIZE', 'false').lower() in ('true', '1', 't')
    if anonymize: 
        anonymize_handler = AnonymizeHandler()
        current_handler = current_handler.set_next(anonymize_handler)

    # Add the prompt and bedrock handlers.
    current_handler = current_handler.set_next(prompt_handler).set_next(bedrock_handler)

    # Copy to clipboard?
    clipboard = os.getenv('CLIPBOARD_COPY', 'false').lower() in ('true', '1', 't')
    if clipboard:         
        clipboard_handler = ClipboardWriterHandler()
        current_handler = current_handler.set_next(clipboard_handler)
        print("\n\n  ================================================\n   The summary will be copied to your clipboard.\n  ================================================\n")  

    
        
    return chain

def construct_custom_chain():
    # Get creative...
    youtube_handler = YouTubeReaderHandler()
    amazon_transcribe_handler = AmazonTranscriptionHandler()
    pdf_handler = PDFReaderHandler()
    local_file_reader_handler = LocalFileReaderHandler()
    local_file_writer_handler = LocalFileWriterHandler()
    prompt_handler = PromptHandler()
    amazon_bedrock_handler = AmazonBedrockHandler()
    amazon_s3_writer_handler = AmazonS3WriterHandler()
    amazon_s3_reader_handler = AmazonS3ReaderHandler()
    
    http_handler = HTTPHandler()
    textract_handler = AmazonTextractHandler()
    anonymize_handler = AnonymizeHandler()

    chain = amazon_s3_writer_handler

    amazon_s3_writer_handler.set_next(textract_handler).set_next(prompt_handler).set_next(amazon_bedrock_handler)
    # Read Youtube Video >> Save Audio in Amazon S3 >> Extract text from speach (Amazon Transcribe) >> Construct a prompt >> Summarize using Amazon Bedrock.
    # youtube_handler.set_next(amazon_s3_writer_handler).set_next(amazon_transcribe_handler).set_next(prompt_handler).set_next(anonymize_handler).set_next(amazon_bedrock_handler)
    # s3reader_handler.set_next(local_file_writer_handler)

    return chain

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_file_or_youtube_url> [prompt_file_name]") 
        sys.exit(1)

    file_path = sys.argv[1]
    prompt_file_name = sys.argv[2] if len(sys.argv) > 2 else 'default_prompt'

    
    input_type = determine_input_type(file_path)

    # for testing only
    # input_type = "custom"

    handler_chain = construct_chain(input_type)

    # Process the input
    request = {"type": input_type, "path": file_path, "prompt_file_name": prompt_file_name, "text":"", "write_file_path":"output.txt"}

    result = handler_chain.handle(request)
    if (result.get("text", None)):
        print(result.get("text"))
    else:
        print(result)

if __name__ == "__main__":
    main()