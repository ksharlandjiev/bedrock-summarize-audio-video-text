from utils.bedrock import invoke_model

from handlers.abstract_handler import AbstractHandler
class AmazonBedrockHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        print("Summarizing text with Bedrock...")
        
        text = request.get("text", None)
        
        summary = invoke_model(text)
        
        request.update({"text":summary})
        return super().handle(request)

