from urllib.request import urlopen
from bs4 import BeautifulSoup

def fetch_webpage(url):
    try:
        page = urlopen(url)
        html = page.read().decode("utf-8")      
        start_index = html.find("<body")
        end_index = html.find("</body>")
        return html[start_index:end_index]

    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return None
    
def clean_html(html_content):
    """
    Uses BeautifulSoup to extract text from the HTML content's body.
    """
    soup = BeautifulSoup(html_content, 'lxml')
    text = soup.body.get_text(separator=' ', strip=True) if soup.body else ''
    return text