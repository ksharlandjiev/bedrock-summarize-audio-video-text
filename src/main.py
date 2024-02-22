import os
import sys
from typing import Any
from dotenv import load_dotenv
from handlers.abstract_handler import AbstractHandler
from handlers.handler import Handler
from handlers.youtube_handler import YouTubeHandler
from handlers.transcription_handler import TranscriptionHandler
from handlers.pdf_handler import PDFHandler
from handlers.local_file_handler import LocalFileHandler
from handlers.prompt_handler import PromptHandler
from handlers.bedrock_handler import BedrockHandler
from handlers.s3reader_handler import S3ReaderHandler
from handlers.s3writer_handler import S3WriterHandler
from handlers.anonymize_handler import AnonymizeHandler
from handlers.clipboard_handler import ClipboardHandler
from handlers.http_handler import HTTPHandler
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
    elif file_path.endswith(('.txt', '.json')):
        return "text_or_json"
    else:
        return "unsupported"

def construct_chain(input_type):
    # Initialize handlers
    youtube_handler = YouTubeHandler()
    transcription_handler = TranscriptionHandler()
    pdf_handler = PDFHandler()
    local_file_handler = LocalFileHandler()
    prompt_handler = PromptHandler()
    bedrock_handler = BedrockHandler()
    s3reader_handler = S3ReaderHandler()
    s3writer_handler = S3WriterHandler()
    http_handler = HTTPHandler()
    

    # Use if-elif-else to construct the appropriate chain. In Python 3.10 we could use match statement.
    if input_type == "youtube_url":
        chain = youtube_handler
        current_handler = youtube_handler.set_next(s3writer_handler).set_next(transcription_handler)
    elif input_type == "multimedia_file":
        chain = s3writer_handler
        current_handler = s3writer_handler.set_next(transcription_handler)
    elif input_type == "pdf":
        chain = pdf_handler
        current_handler = pdf_handler 
    elif input_type == "http":
        chain = http_handler
        current_handler = http_handler        
    elif input_type == "text_or_json":
        chain = local_file_handler
        current_handler = local_file_handler
    elif input_type == "s3":
        chain = s3reader_handler
        current_handler = s3reader_handler.set_next(local_file_handler)
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
        clipboard_handler = ClipboardHandler()
        current_handler = current_handler.set_next(clipboard_handler)
        print("\n\n  ================================================\n   The summary will be copied to your clipboard.\n  ================================================\n")  

    return chain

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_file_or_youtube_url> [prompt_file_name]") 
        sys.exit(1)

    file_path = sys.argv[1]
    prompt_file_name = sys.argv[2] if len(sys.argv) > 2 else 'default_prompt'

    input_type = determine_input_type(file_path)
    handler_chain = construct_chain(input_type)

    # Process the input
    request = {"type": input_type, "path": file_path, "prompt_file_name": prompt_file_name, "text":""}
    
    result = handler_chain.handle(request)
    if (result.get("text", None)):
        print(result.get("text"))
    else:
        print(result)

if __name__ == "__main__":
    main()