import sys
from handlers.abstract_handler import AbstractHandler
from utils.bedrock import invoke_model
import json

class AmazonBedrockChatHandler(AbstractHandler):
    
    def handle(self, request: dict) -> dict:
        
        print(f"Hello, I'm the Amazon Bedrock chat hanlder buddy.\n")
        
        print(request.get("text"))      
        print(f"\n\n------\nYou can ask any questions on the text above. To terminate the chat session, use Ctrl+C")
        
        chat_history = []
        chat_history.append({"role": "user", "content": request['text']})
        try: 
          while True:
              user_input = input("> ")              
              chat_history.append({"role": "user", "content": user_input})
              messages = json.dumps({"messages": chat_history})
              # Assume summarize_text_with_bedrock is adapted to handle chat
              response = invoke_model(messages)
              
              print(f"Model: {response}")
              chat_history.append({"role": "assistant", "content": response})
        except KeyboardInterrupt:      
          exit_choice = input("\n ---------------- Terminating Chat Session ---------------- \n Type 'yes' to include the chat history for your next handler? ")
          if exit_choice == "yes":
              request['text'] = json.dumps({"messages": chat_history})
        
        return super().handle(request)
