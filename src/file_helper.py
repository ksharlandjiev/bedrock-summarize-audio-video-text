# src/file_helper.py
import os

def is_audio_video_file(file_path):
    """
    Checks if the file is an audio or video file based on its extension.
    """
    audio_video_extensions = ['.mp3', '.mp4', '.m4a', '.wav', '.flac', '.mov', '.avi']
    extension = os.path.splitext(file_path)[1].lower()
    return extension in audio_video_extensions

def is_text_file(file_path):
    """
    Checks if the file is a text-based file based on its extension.
    """
    text_extensions = ['.txt', '.json', '.srt', '.sub']
    extension = os.path.splitext(file_path)[1].lower()
    return extension in text_extensions

def read_text_content(file_path):
    """
    Reads and returns the content of a text or JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def load_prompt(prompt_file_name, text):
    """
    Loads a prompt from a file in the 'prompts' directory and formats it with the provided text.
    """
    prompt_file_path = os.path.join('../prompts', f'{prompt_file_name}.txt')
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as file:
            prompt_template = file.read()
            formatted_prompt = prompt_template.format(input_text=text)
            return formatted_prompt
    except FileNotFoundError:
        print(f"Prompt file '{prompt_file_name}.txt' not found. Using default prompt.")
        default_prompt = "Please provide a summary of the following text: {input_text}"
        return default_prompt.format(input_text=text)
