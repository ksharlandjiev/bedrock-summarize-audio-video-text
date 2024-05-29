from pptx import Presentation
from handlers.abstract_handler import AbstractHandler

class MicrosoftPowerPointReaderHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        print("Processing PPTX file...")

        # Initialize a variable to hold the extracted text
        text_content = ''

        # Load the presentation from the path specified in the request
        presentation = Presentation(request.get("path", None))

        # Iterate through each slide in the presentation
        for slide in presentation.slides:
            # Extract text from shapes
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text_content += shape.text + '\n'

            # Extract text from speaker notes
            if slide.has_notes_slide:
                notes_slide = slide.notes_slide
                text_content += notes_slide.notes_text_frame.text + '\n'

        # Update the request with the extracted text
        request.update({"text": text_content})

        # Call the next handler in the chain
        return super().handle(request)
