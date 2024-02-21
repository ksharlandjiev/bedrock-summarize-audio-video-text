# src/main.py
import sys
import pyperclip
import os
from dotenv import load_dotenv
from transcription import extract_transcript
from summarization import summarize_text_with_bedrock
from anonymization import anonymize_text
from file_helper import is_audio_video_file, is_text_file, load_prompt, read_text_content
from utils import print_ww


# Load environment variables from .env file
load_dotenv()

# Accessing variables from .env file
# Check if anonymization is enabled
anonymize = os.getenv('ANONYMIZE', 'false').lower() in ('true', '1', 't')
anonymize_replacement = os.getenv('ANONYMIZE_CUSTOMER_NAME_REPLACEMENT')
clipboard_copy = os.getenv('CLIPBOARD_COPY', 'false').lower() in ('true', '1', 't')

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_file> [prompt_file_name]")
        sys.exit(1)

    file_path = sys.argv[1]
    prompt_file_name = sys.argv[2] if len(sys.argv) > 2 else 'default_prompt'    
    if is_audio_video_file(file_path):
        print("Extracting text from file...\n")
        text_content = extract_transcript(file_path, prompt_file_name)
    elif is_text_file(file_path):
        # Read text content from the file
        print("Reading file...\n")
        text_content = read_text_content(file_path)        
    else:
        print("Unsupported file type.")
        exit()

    #Anonymize?
    if anonymize: 
        print("Anonymizing text...\n")
        text_content = anonymize_text(text_content, anonymize_replacement)
        

    # Load and format the prompt
    prompt = load_prompt(prompt_file_name, text_content)

    # Directly summarize the text content
    print("Summarizing...\n")
    summary = summarize_text_with_bedrock(prompt)
    print_ww(summary)

    # Copy the summary to the clipboard
    if clipboard_copy:
        pyperclip.copy(summary)
        print("\n\n  ================================================\n   The summary has been copied to your clipboard.\n  ================================================\n")

if __name__ == "__main__":
    main()

