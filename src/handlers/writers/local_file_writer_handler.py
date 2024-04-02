import datetime
import json
import os
from handlers.abstract_handler import AbstractHandler

class LocalFileWriterHandler(AbstractHandler):
    def handle(self, request: dict) -> dict:
        # Determine the file path for writing
        write_file_path = request.get("write_file_path", None)
        if not write_file_path:
            # Prepare the output filename with the current date and time if not provided
            current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            local_dir = os.getenv('DIR_STORAGE', './downloads')
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)  # Create the directory if it doesn't exist
            write_file_path = f"{local_dir}/output_{current_time}.txt"
        
        print(f"Writing data into: {write_file_path}")
        # Extract the text content from the request
        text = request.get("text", None)
        
        # Convert the content to a JSON string if it's a dictionary
        if isinstance(text, dict):
            text = json.dumps(text, indent=4)
        # Attempt to beautify if text is a JSON string (this will not change non-JSON strings)
        elif isinstance(text, str) and self.is_json(text):
            text = json.dumps(json.loads(text), indent=4)
        # Convert to string if it's neither dict nor already a string (for safety)
        else:
            text = str(text)

        # Attempt to write the content to the specified file
        try:
            with open(write_file_path, "a") as f:
                f.write(text + "\n")  # Append a newline for separation between entries
            request.update({"status": True})
        except Exception as e:
            request.update({"status": False, "error": str(e)})
            print(f"Error writing to {write_file_path}: {e}")

        return super().handle(request)
    
    def is_json(self, data):
        """Check if the data is a valid JSON string."""
        try:
            json_object = json.loads(data)
            return True
        except ValueError:
            return False
        except TypeError:  # In case the input isn't a string (e.g., bytes, file object)
            return False
