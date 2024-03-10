from utils.bedrock import invoke_model

from handlers.abstract_handler import AbstractHandler
class AmazonBedrockHandler(AbstractHandler):
    def handle(self, request: dict) -> dict:
        print("Summarizing text with Bedrock...")
        
        summary = invoke_model(request.get("text", None))
        
        request.update({"text":summary})
        return super().handle(request)

