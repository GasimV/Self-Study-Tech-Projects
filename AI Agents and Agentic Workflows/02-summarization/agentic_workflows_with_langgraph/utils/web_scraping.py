import requests
from bs4 import BeautifulSoup

def web_scrape(url: str) -> str:
    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = soup.get_text(separator=" ", strip=True)

            return page_text
        else:
            return f"Veb-səhifəni əldə etmək mümkün olmadı: Status kodu {response.status_code}"
    except Exception as e:
        print(e)
        return f"Veb-səhifəni əldə etmək mümkün olmadı: {e}"
