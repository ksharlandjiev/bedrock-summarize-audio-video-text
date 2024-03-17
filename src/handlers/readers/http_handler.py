from handlers.abstract_handler import AbstractHandler
from utils.web_utils import fetch_webpage
class HTTPHandler(AbstractHandler):

    def handle(self, request: dict) -> dict:
        url = request.get("path", None);
        print("Fetching data from web page: ",url)
        response = fetch_webpage(url)
        if response:
            
            request.update({"text": response})
            
            print("Web page content fetched successfully.")
        else:
            print("Failed to fetch web page content.")
        
        return super().handle(request)    