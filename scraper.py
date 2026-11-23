"""
Robô de coleta de preços com Playwright (API síncrona).

Site alvo: https://books.toscrape.com  (site de treino criado para
praticar web scraping, com uso liberado).

Fluxo:
  1. Abre o navegador (Chromium, Firefox ou WebKit).
  2. Percorre as páginas do catálogo.
  3. Para cada livro, extrai título, preço, disponibilidade e avaliação.
  4. Salva tudo em CSV (precos.csv).

Uso:
    python scraper.py                      # 3 páginas, Chromium, navegador visível
    python scraper.py --paginas 5 --headless
    python scraper.py --navegador firefox --trace
"""

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

URL_BASE = "https://books.toscrape.com/"
ARQUIVO_CSV = Path("precos.csv")
CAMPOS = ["data_coleta", "pagina", "titulo", "preco", "disponibilidade", "avaliacao", "link"]

NOTAS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def converter_preco(texto: str) -> float:
    """Converte '£51.77' (ou 'Â£51.77') em 51.77."""
    numero = re.search(r"\d+(?:[.,]\d+)?", texto)
    if not numero:
        raise ValueError(f"Preço inválido: {texto!r}")
    return float(numero.group().replace(",", "."))


def converter_avaliacao(classe_css: str) -> int:
    """A nota vem como classe CSS, ex.: 'star-rating Three' -> 3."""
    for nome, valor in NOTAS.items():
        if nome in classe_css:
            return valor
    return 0


def coletar_pagina(page, numero_pagina: int) -> list[dict]:
    """Extrai os livros da página atual."""
    registros = []
    cartoes = page.locator("article.product_pod")
    cartoes.first.wait_for()  # garante que a lista carregou

    for i in range(cartoes.count()):
        cartao = cartoes.nth(i)
        link = cartao.locator("h3 a")
        classe_nota = cartao.locator("p.star-rating").get_attribute("class") or ""

        registros.append(
            {
                "data_coleta": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pagina": numero_pagina,
                "titulo": link.get_attribute("title"),
                "preco": converter_preco(cartao.locator("p.price_color").inner_text()),
                "disponibilidade": cartao.locator("p.availability").inner_text().strip(),
                "avaliacao": converter_avaliacao(classe_nota),
                "link": page.url.rsplit("/", 1)[0] + "/" + (link.get_attribute("href") or ""),
            }
        )
    return registros


def salvar_csv(registros: list[dict], caminho: Path = ARQUIVO_CSV) -> None:
    with caminho.open("w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";")
        escritor.writeheader()
        escritor.writerows(registros)


def executar(max_paginas: int, headless: bool, navegador: str, trace: bool) -> list[dict]:
    todos: list[dict] = []

    with sync_playwright() as p:
        browser = getattr(p, navegador).launch(headless=headless, slow_mo=0 if headless else 300)
        context = browser.new_context(locale="pt-BR")
        if trace:
            context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = context.new_page()
        page.goto(URL_BASE)

        for numero in range(1, max_paginas + 1):
            registros = coletar_pagina(page, numero)
            todos.extend(registros)
            print(f"Página {numero}: {len(registros)} livros coletados")

            proxima = page.locator("li.next a")
            if numero == max_paginas or proxima.count() == 0:
                break
            try:
                proxima.click()  # auto-wait: espera o botão ficar clicável
                page.wait_for_load_state("domcontentloaded")
            except PlaywrightTimeout:
                print("Tempo esgotado ao avançar de página; encerrando.")
                break

        if trace:
            context.tracing.stop(path="trace.zip")
            print("Trace salvo em trace.zip  ->  playwright show-trace trace.zip")

        browser.close()

    return todos


def main() -> None:
    parser = argparse.ArgumentParser(description="Robô de coleta de preços (Playwright)")
    parser.add_argument("--paginas", type=int, default=3, help="quantas páginas coletar")
    parser.add_argument("--headless", action="store_true", help="roda sem abrir a janela")
    parser.add_argument(
        "--navegador", choices=["chromium", "firefox", "webkit"], default="chromium"
    )
    parser.add_argument("--trace", action="store_true", help="grava trace.zip (Trace Viewer)")
    args = parser.parse_args()

    registros = executar(args.paginas, args.headless, args.navegador, args.trace)
    salvar_csv(registros)

    if registros:
        precos = [r["preco"] for r in registros]
        print(f"\nTotal: {len(registros)} produtos | "
              f"menor: £{min(precos):.2f} | maior: £{max(precos):.2f} | "
              f"média: £{sum(precos) / len(precos):.2f}")
    print(f"Arquivo gerado: {ARQUIVO_CSV.resolve()}")


if __name__ == "__main__":
    main()
