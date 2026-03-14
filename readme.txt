# Coleta de Dados de Preços em Marketplaces

## Descrição
Web scraper que coleta dados de produtos (nome, preço, link) de múltiplos marketplaces simultaneamente usando Selenium com threads paralelas.

## Requisitos
- Python 3.8+
- Microsoft Edge (WebDriver)
- Bibliotecas listadas em requirements.txt

## Instalação
1. Clone o repositório
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure os XPaths dos marketplaces em `elements.ini`

## Uso
```
python main.py
```
O script solicitará:
- Nome do produto a buscar
- Se o nome deve estar presente no título do anúncio (s/n)

Saída:
- Arquivos Excel com os dados coletados em `data/`
- Logs detalhados em `logs/`
- Resumes em `resume/`

## Estrutura do Projeto
- `main.py`: Orquestrador principal com threading
- `store_process.py`: Lógica de scraping do Selenium
- `settings.py`: Funções auxiliares e configurações
- `elements.ini`: XPaths e URLs dos marketplaces
- `data/`: Arquivos Excel com dados coletados
- `logs/`: Arquivos de log
- `resume/`: Resumos de execução

## Adicionando Novos Marketplaces
1. Abra `elements.ini`
2. Adicione uma novo section com o nome do marketplace
3. Configure os XPaths para: url, search, products_cards, card_name, card_value, card_link, next_page

## Troubleshooting
- Se houver erros de extração, ajuste os XPaths em `elements.ini`
- Se houver problemas com exceções específicas, customize em `settings.py`

