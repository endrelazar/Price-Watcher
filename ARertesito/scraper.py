import json
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "elmfind.json")

with open(json_path, 'r', encoding='utf-8') as f:
    
#with open('h:\\IT\\my-app\\tanulas1\\ARertesito\\elmfind.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

def find_first_text(soup, selectors):
    for selector in selectors:
        el = soup.select_one(selector)
        logging.debug(f"DEBUG: selector={selector}, found={el}")  # Debug
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return None

def get_html_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        page = context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(5000)  
        html = page.content()
        browser.close()
        return html

def scrape_price(url):
    try:
        html = get_html_playwright(url)
        soup = BeautifulSoup(html, 'html.parser')
        price_text = find_first_text(soup, config['price_selectors'])
        if price_text:
            import re
            price_text = price_text.replace('Ft', '').replace('HUF', '').replace(' ', '').strip()
            if ',' in price_text:
                price_text = price_text.split(',')[0]
            digits = re.findall(r'\d+', price_text)
            if digits:
                price = int(''.join(digits))
                return price
            else:
                logging.error(f"Nem található szám az árban: {price_text}, URL: {url}")
        return None
    except Exception as e:
        logging.exception(f"Hiba az ár lekérésekor URL: {url} - {e}")
        return None

def scrape_name(url):
    try:
        html = get_html_playwright(url)
        soup = BeautifulSoup(html, 'html.parser')
        name = find_first_text(soup, config['name_selectors'])
        return name
    except Exception as e:
        logging.exception(f"Hiba a név lekérésekor URL: {url} - {e}")
        return None

if __name__ == "__main__":


    url = "https://lol.hu"
    price = scrape_price(url)
    name = scrape_name(url)
    print(f"Termék neve: {name}")
    print(f"Termék ára: {price}")