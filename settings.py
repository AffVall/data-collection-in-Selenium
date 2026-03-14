from time import strftime
from pathlib import Path
import re

FILE_NAME_LOG = f"log_{strftime('%d.%m.%y_%H.%M.%S')}.txt"
FILE_NAME_EXCEL = f"_{strftime('%d.%m.%y_%H.%M.%S')}.xlsx"
FILE_NAME_RESUME = f"resume_{strftime('%d.%m.%y_%H.%M.%S')}.txt"
LOG_DIR = "logs"
DATA_DIR = "data"
RESUME_DIR = "resume"

def ensure_dirs(*dirs):
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def log( message, level="INFO", txt = True):
    ensure_dirs(LOG_DIR)
    log_path = Path(LOG_DIR) / FILE_NAME_LOG
    with open(log_path, "a", encoding="utf-8") as log_file: 
        print(f"[{strftime('%H:%M:%S')}] {level.upper()}: {message}")
        if txt: log_file.write(f"[{strftime('%H:%M:%S')}] {level.upper()}: {message}\n")

def extract_value(marketplace, product, market_section, By):
    price_elements = product.find_elements(By.XPATH, market_section.get("card_value"))

    if marketplace == "Amazon":
        match = re.search(r'\$([\d\s,\.]+)', product.text)
        if match:
            price = "$" + match.group(1)
            return price
        return "Preço não encontrado"
    elif marketplace == "Mercado Livre":
        # attempt regex on product text first
        match_ml = re.search(r'R\$[\s]*([\d\.\,]+)', product.text)
        if match_ml:
            price_val = match_ml.group(1).replace('.', '').replace(',', '.')
            return price_val
    else:
        return price_elements

def exceptions_for_each_marketplace(marketplace, value):
    if isinstance(value, str):
        if marketplace == "Amazon" and value.startswith("$"):
            return value[1:].replace(' ', '.')
        return value
    elif isinstance(value, list):
        if not value:
            return "Preço não encontrado"
        price_text = value[2].text if len(value) > 2 else value[0].text
        price_text = price_text.replace("R$", "").replace(".", "").replace(",", ".").strip()
        return price_text
    else:
        return "Preço não encontrado"


