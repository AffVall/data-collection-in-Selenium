
import pandas
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from configparser import ConfigParser
config_p = ConfigParser()

import settings

#opening browser and searching for product
def start_driver(driver_name, url):
    try:
        settings.log(f"Iniciando Driver: {driver_name} in {url}.")
        driver = webdriver.Edge()
        driver.implicitly_wait(1)
        driver.get(url)
        #driver.minimize_window()
        settings.log("Driver iniciado com sucesso.")
        return driver
    except Exception as e:
        settings.log(f"Erro ao iniciar driver: {str(e)}", "ERROR")
        raise

def page_process(driver, market_section, product_search, name_in_product, marketplace, products):
    #paging and loading all products
    error_count = 0
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)
    try:
        products_cards = driver.find_elements(By.XPATH, market_section.get("products_cards"))
    except Exception as e:
        settings.log(f"Erro ao encontrar produtos na página: {str(e)}", "ERROR")
        error_count += 1

    #processing each product card
    for product in products_cards:
        if error_count >= 3: 
            settings.log(f"Múltiplos erros consecutivos ao processar produtos. Pulando página.", "ERROR", False)
            return True
        name = None
        value = None
        url = None
        try:
            if name_in_product == "s":
                if product_search.lower() not in product.text.lower(): continue

            #setting variables
            try:
                #name
                name_element = product.find_element(By.XPATH, market_section.get("card_name"))
                name = name_element.text
            except Exception as e: 
                settings.log(f"Erro ao pegar nome no {marketplace}: {str(e)}", "ERROR")
                error_count += 1
                continue
            try:
                #price
                value_element = settings.extract_value(marketplace, product, market_section, By)
                value = settings.exceptions_for_each_marketplace(marketplace, value_element)
            except Exception as e: 
                settings.log(f"Erro ao pegar valor no {marketplace}: {str(e)}", "ERROR")
                error_count += 1
                continue
            try:
                #link
                link_element = product.find_element(By.XPATH, market_section.get("card_link"))
                url = link_element.get_attribute("href")
            except Exception as e: 
                settings.log(f"Erro ao pegar link no {marketplace}: {str(e)}", "ERROR")
                error_count += 1

            #saving data in excel only if all elements found
            products.append({
                "Nome": name,
                "Preço": f"{value}",
                "Link": url
            })
            error_count = 0
            settings.log(f"Produto adicionado à lista [{marketplace}]: {name, value}. Total de produtos: {len(products)}.", "PRODUCT", False)
        
        except Exception as e:
            error_count += 1
            settings.log(f"Erro geral ao processar produto no {marketplace}: {type(e).__name__}\n{str(e)}", "ERROR")
            continue

    settings.log(f"Página processada. produtos na pagina [{marketplace}]: {len(products_cards)}, Total de produtos: {len(products)}.", "PAGE")
    try:
        #clicking on next page
        WebDriverWait(driver, 0.5).until(
            EC.element_to_be_clickable((By.XPATH, market_section.get("next_page")))
        ).click()
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, market_section.get("products_cards")))
        )
        return True
    except Exception as e:
        settings.log(f"Erro ao clicar na próxima página: {str(e)}. Finalizando coleta.", "ERROR", False)
        return False

def main_process_marketplace(driver, product_search, name_in_product, marketplace):
    products = []
    try:
        # read the INI and grab only the requested section
        config_p.read("elements.ini")
        market_section = config_p[marketplace]
        settings.log(f"Arquivo elements.ini: \n{dict(market_section)}\n lido com sucesso.", "VARIABLE")
    except Exception as e:
        settings.log(f"Erro ao ler elements.ini: {str(e)}", "ERROR")
        raise

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        driver.find_element(By.XPATH, market_section.get("search")).send_keys(product_search)
        driver.find_element(By.XPATH, market_section.get("search")).submit()
        settings.log(f'Busca realizada para "{product_search}" no {marketplace}.')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, market_section.get("products_cards")))
        ) 
    except Exception as e:
        settings.log(f"Erro na busca: {str(e)}", "ERROR")
        return products
    while page_process(driver, market_section, product_search, name_in_product, marketplace, products):
        pass
    return products

def products_to_excel(results_map):
    df = pandas.DataFrame()
    df.to_excel(settings.DATA_DIR + "/" + settings.FILE_NAME_EXCEL, index=False)
    with pandas.ExcelWriter(settings.DATA_DIR + "/" + settings.FILE_NAME_EXCEL, mode='a', engine='openpyxl') as writer:
        for market, products in results_map.items():
            df_market = pandas.DataFrame(products)
            df_market.to_excel(writer, sheet_name=market, index=False)
