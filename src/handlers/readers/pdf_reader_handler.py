import os
import json
import shutil
import fitz  # PyMuPDF
from pdfminer.high_level import extract_text
from handlers.abstract_handler import AbstractHandler

class PDFReaderHandler(AbstractHandler):

    def handle(self, request: dict) -> dict:
        print("Processing PDF file...")

        # Initialize variables
        text_content = ''
        media_files = []

        # Load the PDF from the path specified in the request
        pdf_path = request.get("path", None)
        
        # Determine the write file path and output folder
        write_file_path = request.get("write_file_path", None)
        if write_file_path:
            base_folder = os.path.dirname(write_file_path)
            file_id = os.path.basename(write_file_path).split('.')[0]
            output_folder = os.path.join(base_folder, file_id)
            media_folder = os.path.join(output_folder, "media")
            os.makedirs(media_folder, exist_ok=True)
        
        # Initialize the metadata dictionary
        if "metadata" not in request:
            request["metadata"] = {}

        # Copy the original PDF file to the output folder
        original_file_path = os.path.join(output_folder, 'original.pdf')
        shutil.copy(pdf_path, original_file_path)

        # Extract text from PDF
        text_content = extract_text(pdf_path)
        
        # Save the transcript to a text file
        transcript_file_path = os.path.join(output_folder, 'transcript.txt')
        with open(transcript_file_path, 'w') as transcript_file:
            transcript_file.write(text_content)

        # Extract images if requested
        if request.get("extract_media", False):
            pdf_document = fitz.open(pdf_path)
            for page_number in range(len(pdf_document)):
                page = pdf_document.load_page(page_number)
                image_list = page.get_images(full=True)
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_file_name = f"page_{page_number + 1}_image_{img_index + 1}.{image_ext}"
                    image_file_path = os.path.join(media_folder, image_file_name)
                    with open(image_file_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    media_files.append({"type": "image", "path": image_file_path, "page_number": page_number + 1, "xref": xref})

        # Create metadata with traceability for graph database
        metadata = {
            "original_file": original_file_path,
            "transcript_file": transcript_file_path,
            "media_files": media_files
        }
        
        # Save metadata to a json file
        metadata_file_path = os.path.join(output_folder, 'metadata.json')
        with open(metadata_file_path, 'w') as metadata_file:
            json.dump(metadata, metadata_file, indent=4)

        # Update the request metadata with the new metadata
        request["metadata"][pdf_path] = metadata

        # Update the request with the extracted text
        request.update({"text": text_content})

        # Call the next handler in the chain
        return super().handle(request)
