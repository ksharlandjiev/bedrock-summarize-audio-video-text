from pdfminer.high_level import extract_text
from handlers.abstract_handler import AbstractHandler

class PDFReaderHandler(AbstractHandler):
    def handle(self, request: dict) -> dict:
        print("Processing PDF file...")

        text_content = extract_text(request.get("path", None))

        request.update({"text":text_content})

        return super().handle(request)
