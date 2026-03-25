# Coleta de Dados de Preços em Marketplaces

## Descrição
Web scraper que coleta dados de produtos (nome, preço, link) de múltiplos marketplaces simultaneamente usando Selenium com execução paralela por threads.

## Características
- ✓ Coleta de dados em paralelo de múltiplos marketplaces
- ✓ Exportação automática para Excel
- ✓ Sistema de logging detalhado com modo DEBUG
- ✓ Tratamento de exceções específicas por marketplace
- ✓ Suporte a navegação de múltiplas páginas

## Requisitos
- Python 3.8+
- Microsoft Edge
- MSEdgeDriver (baixar em https://developer.microsoft.com/microsoft-edge/tools/webdriver/)

## Instalação

1. Crie um ambiente virtual:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure os marketplaces:**
   - Edite `elements.ini` com os XPaths dos seus marketplaces
   - Edite a def `approach` na pasta `settings.py` caso necessário

## Uso

```bash
python main.py
```

Saída:
- Arquivos Excel em `data/`
- Logs em `logs/`
- Resumo em `resume/`

## Estrutura do Projeto

```
.
├── main.py              # Orquestrador principal
├── store_process.py     # Lógica de scraping
├── settings.py          # Funções auxiliares
├── config.ini           # Configurações
├── elements.ini         # XPaths dos marketplaces
└── requirements.txt     # Dependências
```

### config.ini
- `name_in_product`: Filtrar por nome (True/False)
- `log_debug`: Ativar DEBUG (True/False)
- `ignore_markets`: Marketplaces a ignorar

## Adicionando Novos Marketplaces

Edite `elements.ini` e adicione uma seção:

```ini
[Seu_Marketplace]
url = https://site.com/
search = //input[@id="search"]
products_cards = //div[@class="product"]
card_name = .//*[@class="name"]
card_value = .//*[@class="price"]
card_link = .//*[@class="link"]
next_page = //a[@class="next"]
```

## Troubleshooting

- **XPath não encontrado**: Inspecione o HTML (F12) e ajuste em `elements.ini`
- **MSEdgeDriver erro**: Baixe a versão compatível com seu Edge
- **Nenhum produto extraído**: Verifique se os XPaths estão corretos
