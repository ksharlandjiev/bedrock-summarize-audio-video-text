from typing import Any
from handlers.abstract_handler import AbstractHandler

class S3ReaderHandler(AbstractHandler):
    def handle(self, request: dict) -> dict:
        print("Downloading S3 object...")
        return super().handle(request)
            
