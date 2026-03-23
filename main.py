import store_process
import settings
from threading import Thread
from configparser import ConfigParser

def main():
    settings.ensure_dirs()
    settings.log("iniciando processo.", txt=False)

    product_search = input("Digite o nome do produto a ser pesquisado: ")

    for key in settings.FILES_NAMES:
        settings.FILES_NAMES[key] = f"{product_search.replace(' ', '_')}_{settings.FILES_NAMES[key]}"
    settings.log(f"procurando por: {product_search}", "VARIABLE")

    config = ConfigParser()
    config.read("config.ini")
    name_in_product = config.getboolean("settings", "name_in_product")
    settings.LOG_DEBUG = config.getboolean("settings", "log_debug")
    settings.log(f"DEBUG mode enabled: {settings.LOG_DEBUG}")
    
    markets_elements = ConfigParser()
    markets_elements.read("elements.ini")
    markets = markets_elements.sections()
    settings.log(f"Marketplaces carregados: {markets}", "DEBUG")
    for market in markets:
        settings.CACHE[market] = []
    settings.log(f"Cache inicializado para marketplaces: {settings.CACHE}", "DEBUG")

    def run_market(driver, search, name_flag, market):
        results = store_process.main_process_marketplace(driver, search, name_flag, market)
        settings.CACHE[market] = results

    threads = []
    for idx, market in enumerate(markets, start=1):
        if market in config.get("settings", "ignore_markets"):
            continue

        url = markets_elements[market].get("url")
        settings.log(f"Iniciando driver #{idx} para {market} em {url}", "DEBUG")
        driver = store_process.start_driver(f"Edge{idx}", url)
        t = Thread(
            target=run_market,
            args=(driver, product_search, name_in_product, market)
        )
        threads.append((t, market))
        settings.log(f"Thread criada para {market}", "DEBUG")

    settings.log(f"Iniciando {len(threads)} threads de coleta", "DEBUG")
    for t, market in threads:
        settings.log(f"Iniciando thread para {market.upper()}")
        t.start()
    for t, market in threads:
        t.join()
        settings.log(f"Thread de {market.upper()} finalizada", "DEBUG")
    
    settings.log(f"Todas threads finalizadas. Processando {len(settings.CACHE)} marketplaces")
    store_process.products_to_excel()
    store_process.make_resume()
    
if __name__ == "__main__":
    main()
