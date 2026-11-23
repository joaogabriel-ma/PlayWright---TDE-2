# Robô de Coleta de Preços com Playwright

Trabalho Final — Tópicos Especiais em Análise e Desenvolvimento de Sistemas (ADS)
Tema 4: **Playwright** (biblioteca da Microsoft para automação de navegadores)

## Integrantes

| Nome completo |
|---|
| João Gabriel [SOBRENOME] |
| [NOME COMPLETO] Sanquetta |
| [NOME COMPLETO] Gustavo |

## O que o projeto faz

O robô abre um navegador real, percorre as páginas do catálogo do site
[Books to Scrape](https://books.toscrape.com), extrai **título, preço, disponibilidade e avaliação**
de cada produto e salva tudo em um arquivo CSV (`precos.csv`).

O site foi escolhido porque foi criado especificamente para treinar web scraping
(uso liberado). Em qualquer site real, consulte antes o `robots.txt` e os termos de uso.

## Requisitos

- Python 3.9 ou superior
- Conexão com a internet

## Instalação

```bash
# 1. (opcional) criar ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. instalar as dependências
pip install -r requirements.txt

# 3. baixar os navegadores usados pelo Playwright
playwright install
```

## Como executar o robô

```bash
python scraper.py                          # 3 páginas, navegador visível
python scraper.py --paginas 5              # coleta 5 páginas
python scraper.py --headless               # sem abrir a janela
python scraper.py --navegador firefox      # chromium (padrão), firefox ou webkit
python scraper.py --trace                  # grava trace.zip para o Trace Viewer
```

Ao final é gerado o arquivo **`precos.csv`** (separador `;`, abre direto no Excel).

## Ferramentas do Playwright

**Codegen** — grava suas ações no navegador e gera o código Python:

```bash
playwright codegen https://books.toscrape.com
```

**Trace Viewer** — reprodução passo a passo da execução (DOM, rede, screenshots):

```bash
python scraper.py --trace
playwright show-trace trace.zip
```

## Testes (pytest-playwright)

```bash
pytest -v                       # roda os testes
pytest -v --headed              # vendo o navegador
pytest -v --browser firefox     # em outro navegador
```

Os testes verificam que a página inicial lista 20 livros, que o botão *next* leva à
página 2, que todo livro tem preço válido e que as funções auxiliares funcionam.

## Estrutura

```
.
├── scraper.py            # robô de coleta (API síncrona do Playwright)
├── tests/
│   └── test_site.py      # testes com pytest-playwright
├── requirements.txt
└── README.md
```

## Como o código funciona

1. `sync_playwright()` inicia o Playwright e `launch()` abre o navegador escolhido.
2. `page.goto()` acessa o site; o **auto-wait** espera a página carregar sozinho.
3. `page.locator("article.product_pod")` localiza os cartões de produto; para cada um,
   `inner_text()` e `get_attribute()` extraem os dados.
4. `li.next a` com `.click()` avança de página (o Playwright espera o botão ficar clicável).
5. Os dados vão para o CSV com o módulo `csv`.

## Playwright x Selenium (resumo)

| Aspecto | Playwright | Selenium |
|---|---|---|
| Espera por elementos | Automática (auto-wait) | Manual (`WebDriverWait`) |
| Navegadores | Chromium, Firefox, WebKit | Chrome, Firefox, Edge, Safari |
| Gravador de código | `codegen` nativo | Selenium IDE (extensão) |
| Depuração | Trace Viewer | Logs e screenshots manuais |
| API sync/async | Ambas | Apenas síncrona |
| Maturidade e comunidade | Mais recente (2020) | Mais antigo (2004), maior comunidade |

## Referências

- Documentação oficial: https://playwright.dev/python
- Repositório do Playwright: https://github.com/microsoft/playwright-python
- Selenium: https://www.selenium.dev/documentation/
- Site de treino: https://books.toscrape.com
