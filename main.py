import store_process
import settings
import threading
from configparser import ConfigParser

def main():
    #getting user input and setting variables
    settings.log("iniciando processo.")
    settings.ensure_dirs(settings.LOG_DIR, settings.DATA_DIR, settings.RESUME_DIR)
    product_search = input("Digite o nome do produto: ")
    name_in_product = input("O nome do produto está presente no título do anúncio? (s/n): ").lower()
    
    if name_in_product != "s": name_in_product = "n"
    settings.FILE_NAME_EXCEL = f"{product_search}_{settings.FILE_NAME_EXCEL}"
    settings.log(f"procurando por: {product_search}.", "VARIABLE")
    settings.log(f"Nome do produto presente no título do anúncio: {name_in_product}.", "VARIABLE")
    
    # read marketplace names from elements.ini
    config = ConfigParser()
    config.read("elements.ini")
    markets = config.sections()

    # helper for thread body
    def run_market(driver, search, name_flag, market, output_list):
        results = store_process.main_process_marketplace(driver, search, name_flag, market)
        output_list.extend(results)

    threads = []
    results_map = {}

    #applying process for each marketplace in a separate thread
    for idx, market in enumerate(markets, start=1):
        # debugging Amazon
        #if market == "Mercado Livre": continue
        
        url = config[market].get("url")
        driver = store_process.start_driver(f"Edge{idx}", url)
        results_map[market] = []
        t = threading.Thread(
            target=run_market,
            args=(driver, product_search, name_in_product, market, results_map[market])
        )
        threads.append((t, market))

    # start all threads
    for t, _ in threads:
        t.start()
    # wait for completion
    for t, _ in threads:
        t.join()

    # write excel sheets for each market
    store_process.products_to_excel(results_map)
    
if __name__ == "__main__":
    main()
