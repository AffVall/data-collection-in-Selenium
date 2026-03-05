import store_process
from settings import log

def main():
    #getting user input and setting variables
    log("iniciando processo.")
    product_search = input("Digite o nome do produto: ")
    name_in_product = input("O nome do produto está presente no título do anúncio? (s/n): ").lower()
    if name_in_product != "s": name_in_product = "n"
    log(f"procurando por: {product_search}.", "VARIABLE")
    log(f"Nome do produto presente no título do anúncio: {name_in_product}.", "VARIABLE")

    driver1 = store_process.start_driver("Edge1", "https://www.mercadolivre.com.br/")
    #driver2 = store_process.start_driver("Edge2", "https://www.amazon.com.br/ref=nav_logo")

    log("iniciando processo de armazenamento de dados.")
    products_mercado_livre = store_process.main_process_marketplace(
        driver1, product_search, name_in_product, marketplace="Mercado Livre"
        )
    
    store_process.products_to_excel(products_mercado_livre, "Mercado Livre")
    #store_process.main_process_amazon(driver2, product_search, name_in_product)

if __name__ == "__main__":
    main()
