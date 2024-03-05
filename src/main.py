#!/opt/anaconda3/bin/python

from datetime import datetime
import os
import sys
from typing import Any
from dotenv import load_dotenv
from handlers.handler_factory import HandlerFactory
import argparse

# Load environment variables from .env file
load_dotenv()

def determine_input_type(file_path):
    if "youtube" in file_path or "youtu.be" in file_path:
        return "youtube_url"
    elif file_path.startswith(('http')):
        return "http"    
    elif file_path.startswith(('s3://')):
        return "s3"  
    elif file_path.startswith(('quip://')):
        return "quip"   
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

    # Use if-elif-else to construct the appropriate chain. In Python 3.10 we could use match statement.
    if input_type == "youtube_url":
        youtube_handler = HandlerFactory.get_handler("YouTubeReaderHandler")
        s3writer_handler = HandlerFactory.get_handler("AmazonS3WriterHandler")
        transcription_handler = HandlerFactory.get_handler("AmazonTranscriptionHandler")
        local_file_writer_handler = HandlerFactory.get_handler("LocalFileWriterHandler")
        
        chain = youtube_handler
        current_handler = youtube_handler.set_next(s3writer_handler).set_next(transcription_handler).set_next(local_file_writer_handler)
    elif input_type == "multimedia_file":
        s3writer_handler = HandlerFactory.get_handler("AmazonS3WriterHandler")
        transcription_handler = HandlerFactory.get_handler("AmazonTranscriptionHandler")
        local_file_writer_handler = HandlerFactory.get_handler("LocalFileWriterHandler")

        chain = s3writer_handler
        current_handler = s3writer_handler.set_next(transcription_handler).set_next(local_file_writer_handler)
    elif input_type == "image_file":
        local_file_reader_handler = HandlerFactory.get_handler("LocalFileReaderHandler")
        textract_handler = HandlerFactory.get_handler("AmazonTextractHandler")

        chain = local_file_reader_handler
        current_handler = local_file_reader_handler.set_next(textract_handler)        
    elif input_type == "pdf":
        pdf_handler = HandlerFactory.get_handler("PDFReaderHandler")

        chain = pdf_handler
        current_handler = pdf_handler 
    elif input_type == "http":
        http_handler = HandlerFactory.get_handler("HTTPHandler")
        http_clean_handler = HandlerFactory.get_handler("HTMLCleanerHandler")

        chain = http_handler
        current_handler = http_handler.set_next(http_clean_handler).set_next(local_file_writer_handler)
    elif input_type == "text_or_json":
        local_file_reader_handler = HandlerFactory.get_handler("LocalFileReaderHandler")

        chain = local_file_reader_handler
        current_handler = local_file_reader_handler
    elif input_type == "s3":
        s3reader_handler = HandlerFactory.get_handler("AmazonS3ReaderHandler")
        local_file_reader_handler = HandlerFactory.get_handler("LocalFileReaderHandler")

        chain = s3reader_handler
        current_handler = s3reader_handler.set_next(local_file_reader_handler)
    elif input_type == "quip":
        quip_reader_handler = HandlerFactory.get_handler("QuipReaderHandler")
        http_clean_handler = HandlerFactory.get_handler("HTMLCleanerHandler")

        chain = quip_reader_handler
        current_handler = quip_reader_handler.set_next(http_clean_handler)

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
        anonymize_handler = HandlerFactory.get_handler("AnonymizeHandler")
        current_handler = current_handler.set_next(anonymize_handler)

    # Add the prompt and bedrock handlers.
    prompt_handler = HandlerFactory.get_handler("PromptHandler")
    bedrock_handler = HandlerFactory.get_handler("AmazonBedrockHandler")    
    current_handler = current_handler.set_next(prompt_handler).set_next(bedrock_handler)

    # Copy to clipboard?
    clipboard = os.getenv('CLIPBOARD_COPY', 'false').lower() in ('true', '1', 't')
    if clipboard:         
        clipboard_handler = HandlerFactory.get_handler("ClipboardWriterHandler")
        current_handler = current_handler.set_next(clipboard_handler)
        print("\n\n  ================================================\n   The summary will be copied to your clipboard.\n  ================================================\n")    
        
    return chain

def construct_custom_chain():
    # Get creative...
    youtube_handler = HandlerFactory.get_handler("YouTubeReaderHandler")
    amazon_transcribe_handler = HandlerFactory.get_handler("AmazonTranscriptionHandler")
    prompt_handler = HandlerFactory.get_handler("PromptHandler")
    amazon_bedrock_handler = HandlerFactory.get_handler("AmazonBedrockHandler")
    amazon_s3_writer_handler = HandlerFactory.get_handler("AmazonS3WriterHandler")
    anonymize_handler = HandlerFactory.get_handler("AnonymizeHandler")

    
   
    # Read Youtube Video >> Save Audio in Amazon S3 >> Extract text from speach (Amazon Transcribe) >> Construct a prompt >> Summarize using Amazon Bedrock.
    chain = youtube_handler
    youtube_handler.set_next(amazon_s3_writer_handler).set_next(amazon_transcribe_handler).set_next(prompt_handler).set_next(anonymize_handler).set_next(amazon_bedrock_handler)

    return chain

def main():
 # Initialize the argument parser
    parser = argparse.ArgumentParser(description='Process input files or URLs. Optionally, specify a custom processing chain.')

    # Required positional argument for the file/URL to process
    parser.add_argument('file_path', type=str, help='The path to the file or URL to be processed.')

    # Optional positional argument for the prompt file name, with a default value
    parser.add_argument('prompt_file_name', nargs='?', default='default_prompt', help='The name of the prompt file. Defaults to "default_prompt" if not specified.')

    # Optional flag to specify the use of a custom chain
    parser.add_argument('--custom', action='store_true', help='Flag to use a custom processing chain instead of the default based on file type.')

    # Parse the command-line arguments
    args = parser.parse_args()

    # Handler discovery
    HandlerFactory.discover_handlers()

    # Determine the input type or use the custom chain based on the command-line argument
    if args.custom:
        input_type = "custom"
    else:
        input_type = determine_input_type(args.file_path)

    # Construct the appropriate processing chain
    handler_chain = construct_chain(input_type)

    # Prepare the output filename with the current date and time
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"./downloads/output_{current_time}.txt"
    
    # Package the request
    request = {
        "type": input_type,
        "path": args.file_path,
        "prompt_file_name": args.prompt_file_name,
        "text": "",
        "write_file_path": output_file
    }

    # Process the request through the chain
    result = handler_chain.handle(request)

    if result.get("text", None):
        print(result.get("text"))
    else:
        print(result)


if __name__ == "__main__":
    main()