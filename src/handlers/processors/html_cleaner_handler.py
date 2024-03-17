import os
from utils.web_utils import clean_html
from handlers.abstract_handler import AbstractHandler
class HTMLCleanerHandler(AbstractHandler):
        
    def handle(self, request: dict) -> dict:
        print("Cleaning HTML...")
        text = request.get("text")
        cleaned_tex = clean_html(text)
        request.update({"text": cleaned_tex})
        return super().handle(request)
