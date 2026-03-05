import selenium, pandas
from selenium import webdriver
from selenium.webdriver.common.by import By
from configparser import ConfigParser
config_p = ConfigParser()

import settings

#opening browser and searching for product
def start_driver(driver_name, url):
    try:
        settings.log(f"Iniciando Driver: {driver_name} in {url}.")
        driver = webdriver.Edge()
        driver.get(url)
        settings.log("Driver iniciado com sucesso.")
        return driver
    except Exception as e:
        settings.log(f"Erro ao iniciar driver: {str(e)}", "ERROR")
        raise

def main_process_marketplace(driver, product_search, name_in_product, marketplace):
    try:
        # read the INI and grab only the requested section
        config_p.read("find_elements.ini")
        market_section = config_p[marketplace]
        settings.log(f"Arquivo find_elements.ini: \n{dict(market_section)}\n lido com sucesso.", "VARIABLE")
    except Exception as e:
        settings.log(f"Erro ao ler find_elements.ini: {str(e)}", "ERROR")
        raise

    products = []

    try:
        driver.find_element(By.XPATH, market_section.get("search")).send_keys(product_search)
        driver.find_element(By.XPATH, market_section.get("search")).submit()
        settings.log(f"Busca realizada para '{product_search}' no {marketplace}.")
    except Exception as e:
        settings.log(f"Erro na busca: {str(e)}", "ERROR")
        return products

    while True:
        #paging and loading all products
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            products_cards = driver.find_elements(By.XPATH, market_section.get("products_cards"))
        except Exception as e:
            settings.log(f"Erro ao encontrar produtos na página: {str(e)}", "ERROR")
            continue

        for product in products_cards:
            try:
                if name_in_product == "s":
                    if product_search.lower() not in product.text.lower(): continue

                #setting variables
                name = product.find_element(By.XPATH,
                    market_section.get("card_name")
                    ).text
                value_elements = product.find_element(By.XPATH,
                    market_section.get("card_value")
                    ).find_elements(By.TAG_NAME, "span")
                url = product.find_element(By.XPATH,
                    market_section.get("card_link")
                    ).get_attribute("href")

                if marketplace == "Mercado Livre": value = value_elements[2].text
                #saving data in excel
                products.append({
                    "Nome": name,
                    "Preço": f"R${value}",
                    "Link": url
                })

            except Exception as e:
                settings.log(f"Erro ao processar produto: {str(e)}", "ERROR")
                continue

        settings.log(f"Página processada. produtos na pagina [{marketplace}]: {len(products_cards)}, Total de produtos: {len(products)}.", "PAGE")
        #clicking on next page
        try:
            driver.find_element(By.XPATH, market_section.get("next_page")).click()
        except Exception as e:
            settings.log(f"Erro ao clicar na próxima página: {str(e)}. Finalizando coleta.", "ERROR")
            return products

def products_to_excel(products, marketplace):
    try:
        df = pandas.DataFrame(products)
        df.to_excel(f"data/{settings.FILE_NAME_EXCEL}", index=False, sheet_name=marketplace)
        settings.log(f"Dados salvos em Excel: {settings.FILE_NAME_EXCEL}. Total de produtos: {len(products)}.", "EXCEL")
    except Exception as e:
        settings.log(f"Erro ao salvar dados em Excel: {str(e)}", "ERROR")
        raise
