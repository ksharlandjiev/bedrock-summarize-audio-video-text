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