import pandas
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from configparser import ConfigParser
config_p = ConfigParser()

import settings

# Function to start the driver
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

#============================================================================================
# Main process for each marketplace: searching, extracting data, and navigating pages
#============================================================================================
def page_process(driver, market_section, product_search, name_in_product, marketplace):
    """
    Processes a single page of product results, extracting data and navigating to the next page.

    Args:
        driver: Selenium WebDriver instance
        market_section: Config section for the marketplace with XPaths
        product_search: Search term for filtering products by name
        name_in_product: Boolean flag to filter products by name
        marketplace: Name of the marketplace (for logging)

    Returns:
        bool: True if next page was successfully loaded, False if no more pages or error occurred
    """
    error_count = 0
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)
    try:
        products_cards = driver.find_elements(By.XPATH, market_section.get("products_cards"))
        settings.log(f"Produtos encontrados em {marketplace}: {len(products_cards)}", "DEBUG")
    except Exception as e:
        settings.log(f"Erro ao encontrar produtos na página: {str(e)}", "ERROR")
        error_count += 1
        return False

    for product in products_cards:
        if error_count >= 3: 
            settings.log(f"Múltiplos erros consecutivos ({error_count}) ao processar produtos. Pulando página em {marketplace}.", "ERROR")
            return False
        error = False
        name = None
        value = None
        url = None

        if name_in_product == True:
            if product_search.lower() not in product.text.lower():
                settings.log(f"Produto pulado: nome não contém '{product_search}'", "DEBUG")
                continue

        try:
            #name
            name_element = product.find_element(By.XPATH, market_section.get("card_name"))
            name = name_element.text
        except Exception as e: 
            settings.log(f"Erro ao pegar nome no {marketplace}: {str(e)}", "ERROR")
            error_count += 1
            error = True
        try:
            #price
            value_element = product.find_element(By.XPATH, market_section.get("card_value")).text
            value = value_element.replace("R$", "").replace("\n", ".").replace(",", ".")
            value = float(value)
        except Exception as e: 
            settings.log(f"Erro ao pegar valor no {marketplace}: {str(e)}", "ERROR")
            error_count += 1
            error = True
        try:
            #link
            link_element = product.find_element(By.XPATH, market_section.get("card_link"))
            url = link_element.get_attribute("href")
        except Exception as e: 
            settings.log(f"Erro ao pegar link no {marketplace}: {str(e)}", "ERROR")
            error_count += 1
            error = True
        
        try:
            settings.CACHE[marketplace].append({
                "Nome": name,
                "Preço": value,
                "Link": url
            })
        except Exception as e:
            settings.log(f"Erro ao adicionar produto à lista: {str(e)}", "ERROR")
            error_count += 1
            error = True
        if not error: error_count = 0
    settings.log(f"Página processada. produtos na pagina [{marketplace}]: {len(products_cards)}, Total de produtos: {len(settings.CACHE[marketplace])}.", "PAGE")
    try:
        #clicking on next page
        WebDriverWait(driver, 0.5).until(
            EC.element_to_be_clickable((By.XPATH, market_section.get("next_page")))
        ).click()
        settings.log(f"Próxima página clicada em {marketplace}", "DEBUG")
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, market_section.get("products_cards")))
        )
        return True
    except Exception as e:
        settings.log(f"Erro ao clicar na próxima página: {str(e)}. Finalizando coleta em {marketplace}.", "ERROR")
        return False

def main_process_marketplace(driver, product_search, name_in_product, marketplace):
    try:
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
        return settings.CACHE[marketplace]
    
    # Page processing loop
    while page_process(driver, market_section, product_search, name_in_product, marketplace):
        pass
    return settings.CACHE[marketplace]

#============================================================================================
# Functions to write data to Excel and generate a summary of results
#============================================================================================
def products_to_excel():
    try:
        with pandas.ExcelWriter(f"{settings.DIRS['DATA']}/{settings.FILES_NAMES['EXCEL']}", mode='w', engine='openpyxl') as writer:
            for market, products in settings.CACHE.items():
                df_market = pandas.DataFrame(products)
                df_market.to_excel(writer, sheet_name=market, index=False)
        return True
    except Exception as e:
        settings.log(f"Erro ao escrever dados em Excel: {str(e)}", "ERROR")
        return False

def make_resume():
    media = {}
    for market, products in settings.CACHE.items():
        settings.log(f"Resumo para {market}: {len(products)} produtos encontrados.", "RESUME")

        media[market] = 0
        for product in products:
            try:
                media[market] += float(product["Preço"])
            except (KeyError, TypeError, ValueError):
                pass
        media[market] = media[market] / len(products) if products else 1
    
    with open(f"{settings.DIRS['RESUME']}/{settings.FILES_NAMES['RESUME']}", "w", encoding="utf-8") as resume_file:
        for market, products in settings.CACHE.items():
            prices = [float(product["Preço"]) for product in products if product.get("Preço")]
            resume_file.write(f"\nResumo para {market}: {len(products)} produtos encontrados.\n")
            resume_file.write(f"Preço médio para {market}: {media[market]:.2f}\n\n")
            resume_file.write(f"Menor preço para {market}: {min(prices if prices else [None]):.2f}\n")
            resume_file.write(f"Maior preço para {market}: {max(prices if prices else [None]):.2f}\n")
    