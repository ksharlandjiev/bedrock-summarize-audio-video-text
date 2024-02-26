import pyperclip
from handlers.abstract_handler import AbstractHandler

class ClipboardWriterHandler(AbstractHandler):
    def handle(self, request: dict):      
        print("\n\n  ================================================\n   The summary has been copied to your clipboard.\n  ================================================\n")  
        pyperclip.copy(request.get("text", None))        
        return super().handle(request)
