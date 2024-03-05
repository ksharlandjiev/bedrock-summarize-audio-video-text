from typing import Any

from handlers.abstract_handler import AbstractHandler

class LocalFileWriterHandler(AbstractHandler):
    def handle(self, request: dict) -> dict:
        
        file_path = request.get("write_file_path")

        print(f"Writing  to {file_path}")
        write_file_path = request.get("write_file_path", None)
        text = request.get("text", None)

        try:
          f = open(write_file_path, "a")
          f.write(text)
          f.close()
          request.update({"status": True})
        except Exception as e: 
            request.update({"status": False, "error": str(e)})        

        return super().handle(request)
    
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