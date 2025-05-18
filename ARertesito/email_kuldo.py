import smtplib
from email.message import EmailMessage
from datetime import datetime
import json
import logging
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "config.json")



with open(json_path, 'r', encoding='utf-8') as f:
# Konfiguráció beolvasása
#with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

felado = config['email_felado']
jelszo = config['email_jelszo']

def kuld_email(new_price,product_name,product_url,useremail):  
    msg = EmailMessage()
    today = datetime.now().strftime("%Y-%m-%d")
    msg['Subject'] = f'Árfigyelő - {today}'
    msg['From'] = felado
    msg['To'] = useremail
    msg.set_content(f'A {product_url} web-en található {product_name} ára lecsökkent {new_price} Ft -ra')

    try:
        with smtplib.SMTP('smtp.freemail.hu', 587) as smtp:
            smtp.ehlo()                # Üdvözlés a szerver felé
            smtp.starttls()            # TLS titkosítás elindítása
            smtp.ehlo()                # Ismét üdvözlés a titkosított csatornán
            smtp.login(felado, jelszo)
            smtp.send_message(msg)

        logging.info("Email sikeresen elküldve.")
    except Exception as e:
        logging.error(f"Hiba az email küldésnél: {str(e)}")
