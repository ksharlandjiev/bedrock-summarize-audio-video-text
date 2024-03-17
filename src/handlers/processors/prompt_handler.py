import os
from handlers.abstract_handler import AbstractHandler

class PromptHandler(AbstractHandler):
        
    def handle(self, request: dict) -> dict:
        print("Constructing prompt...")
        prompt = self.load_prompt(request.get("prompt_file_name", "default_prompt"), request.get("text", None))

        request.update({"text": prompt})
        return super().handle(request)


    def load_prompt(self, prompt_file_name, text):
        """
        Loads a prompt from a file in the 'prompts' directory and formats it with the provided text.
        """
        prompt_file_path = os.path.join('./prompts', f'{prompt_file_name}.txt')
        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as file:
                prompt_template = file.read()
                formatted_prompt = prompt_template.format(input_text=text)
                return formatted_prompt
        except FileNotFoundError:
            print(f"Prompt file '{prompt_file_name}.txt' not found. Using default prompt.")
            default_prompt = "Please provide a summary of the following text: {input_text}"
            return default_prompt.format(input_text=text)