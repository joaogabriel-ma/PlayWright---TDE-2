"""
Testes com pytest-playwright.

O plugin injeta a fixture `page` automaticamente (um navegador novo por teste).

Rodar:
    pytest -v
    pytest -v --headed                 # vendo o navegador
    pytest -v --browser firefox        # outro navegador
"""

import re
import sys
from pathlib import Path

from playwright.sync_api import Page, expect

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scraper import converter_avaliacao, converter_preco  # noqa: E402

URL = "https://books.toscrape.com/"


def test_pagina_inicial_lista_20_livros(page: Page):
    page.goto(URL)
    expect(page).to_have_title(re.compile("Books to Scrape"))
    expect(page.locator("article.product_pod")).to_have_count(20)


def test_botao_next_leva_para_pagina_2(page: Page):
    page.goto(URL)
    page.get_by_role("link", name="next").click()
    expect(page).to_have_url(re.compile("page-2"))


def test_todo_livro_tem_preco_valido(page: Page):
    page.goto(URL)
    textos = page.locator("p.price_color").all_inner_texts()
    assert len(textos) == 20
    assert all(converter_preco(t) > 0 for t in textos)


# --- testes unitários das funções auxiliares (não precisam de navegador) ---

def test_converter_preco():
    assert converter_preco("£51.77") == 51.77
    assert converter_preco("Â£10.00") == 10.0


def test_converter_avaliacao():
    assert converter_avaliacao("star-rating Three") == 3
    assert converter_avaliacao("star-rating Five") == 5
    assert converter_avaliacao("star-rating") == 0
