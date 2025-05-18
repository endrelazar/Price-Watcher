import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        print(f"DEBUG: selector={selector}, found={el}")  # Debug
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return None

def get_html_selenium(url):
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')  # GPU gyorsítás kikapcsolása
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--blink-settings=imagesEnabled=false')  # Képek letiltása
    options.add_argument('--disable-extensions')  # Bővítmények letiltása
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    options.add_argument(f"user-agent={user_agent}")
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(10)  # Maximum 10 másodperc várakozás
        driver.get(url)
        
        # Csak a szükséges elemekre várunk
        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 
            ','.join(config['price_selectors']))))
            
        html = driver.page_source
        return html
    except Exception as e:
        logging.error(f"Hiba a weboldal betöltésekor: {e}, URL: {url}")
        return None
    finally:
        driver.quit()
   

def scrape_price(url):
    html = get_html_selenium(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')
    price_text = find_first_text(soup, config['price_selectors'])
    if price_text:
        import re
        # Pénznem és szóköz eltávolítása
        price_text = price_text.replace('Ft', '').replace('HUF', '').replace(' ', '').strip()
        # Ha van vessző, csak a vessző előtti rész kell (tizedes elhagyása)
        if ',' in price_text:
            price_text = price_text.split(',')[0]
        # Minden nem számjegy eltávolítása
        digits = re.findall(r'\d+', price_text)
        if digits:
            price = int(''.join(digits))
            return price
        else:
            logging.error(f"Nem található szám az árban: {price_text}, URL: {url}")
            return None
    return None

def scrape_name(url):
    html = get_html_selenium(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')
    name = find_first_text(soup, config['name_selectors'])
    return name

if __name__ == "__main__":
    url = "https://www.temu.com/hu/-tit%C3%A1n-ez%C3%BCstsz%C3%ADn%C5%B1-aut%C3%B3-napellenz%C5%91-els%C5%91-sz%C3%A9lv%C3%A9d%C5%91-h%C5%91szigetel%C3%A9s-%C3%A9s-uv-v%C3%A9delem-feltekerhet%C5%91-kialak%C3%ADt%C3%A1s-egyszer%C5%B1-t%C3%A1rol%C3%A1shoz-minden-aut%C3%B3modellhez-alkalmas-ny%C3%A1ri-%C3%A9s-meleg-id%C5%91j%C3%A1r%C3%A1sra-megfelel%C5%91-aj%C3%A1nd%C3%A9k-aut%C3%B3tulajdonosoknak-g-601100198508322.html?_oak_name_id=1309028899676052377&_oak_mp_inf=EKLuud6o1ogBGiBiNWE0MzNiOWFkNmI0NjJhYTZiOWQ3MDc1ZTZjMjRiNCDzgbfV7DI%3D&top_gallery_url=https%3A%2F%2Fimg.kwcdn.com%2Fproduct%2Ffancy%2F57683e4e-fb07-4605-93a0-a3d0a9928a52.jpg&spec_gallery_id=6918011355&refer_page_sn=10005&refer_source=0&freesia_scene=1&_oak_freesia_scene=1&_oak_rec_ext_1=MzE1MDAw&_oak_gallery_order=1118611968%2C1352904820%2C1183780199%2C1847118361%2C659376439&refer_page_el_sn=200024&_x_sessn_id=ffyryqeu8g&refer_page_name=home&refer_page_id=10005_1747157105989_hgbzg5yjw7"
    price = scrape_price(url)
    name = scrape_name(url)
    print(f"Termék neve: {name}")
    print(f"Termék ára: {price}")