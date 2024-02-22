from urllib.request import urlopen
from handlers.abstract_handler import AbstractHandler
from bs4 import BeautifulSoup

class HTTPHandler(AbstractHandler):
    def handle(self, request: dict) -> dict:
        url = request.get("path", None);
        print("Fetching data from web page: ",url)
        response = self.fetch_webpage(url)
        if response:
            # Clean HTML and extract text from the body
            cleaned_text = self.clean_html(response)
            request.update({"text": cleaned_text})
            print("Web page content fetched successfully.")
        else:
            print("Failed to fetch web page content.")
        
        return super().handle(request)
    
        
    def fetch_webpage(self, url):
        try:
            page = urlopen(url)
            html = page.read().decode("utf-8")      
            start_index = html.find("<body")
            end_index = html.find("</body>")
            return html[start_index:end_index]

        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return None
        
    def clean_html(self, html_content):
        """
        Uses BeautifulSoup to extract text from the HTML content's body.
        """
        soup = BeautifulSoup(html_content, 'lxml')
        text = soup.body.get_text(separator=' ', strip=True) if soup.body else ''
        return text        