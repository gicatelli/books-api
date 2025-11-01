# scripts/scrape_books.py
"""
Script de scraping que coleta todos os livros de https://books.toscrape.com/
Salva o resultado em CSV no caminho definido por api.config.settings.DATA_PATH
"""

import os
import time
import logging
from urllib.parse import urljoin
import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
import pandas as pd

# carregamos as configurações do projeto
from api.config import settings

# configurar logging básico conforme LOG_LEVEL
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger = logging.getLogger(__name__)

# função de conversão de rating textual para inteiro
def rating_to_int(rating_str: str) -> int | None:
    mapping = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return mapping.get(rating_str, None)

# cria sessão com retry para maior robustez em requisições
def create_requests_session() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.headers.update({"User-Agent": "books-scraper/1.0 (+https://example.com)"})
    return session

# parse da página de detalhe do livro
def parse_book_page(session: requests.Session, book_url: str) -> dict:
    resp = session.get(book_url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # título
    title = soup.select_one("div.product_main > h1").get_text(strip=True)

    # preço (ex.: '£53.74')
    price = soup.select_one("p.price_color").get_text(strip=True)

    # disponibilidade
    availability = soup.select_one("p.availability").get_text(strip=True)

    # rating: <p class="star-rating Three">
    rating_tag = soup.select_one("p.star-rating")
    rating = None
    if rating_tag:
        classes = rating_tag.get("class", [])
        for c in classes:
            if c != "star-rating":
                rating = rating_to_int(c)

    # categoria pelo breadcrumb (terceiro link)
    category_name = None
    crumbs = soup.select("ul.breadcrumb li a")
    if len(crumbs) >= 3:
        category_name = crumbs[2].get_text(strip=True)

    # imagem (src relativo -> torna-se absoluto)
    img_tag = soup.select_one("div.thumbnail img")
    image_url = None
    if img_tag:
        src = img_tag.get("src")
        image_url = urljoin(book_url, src)

    return {
        "title": title,
        "price": price,
        "rating": rating,
        "availability": availability,
        "category": category_name,
        "image_url": image_url,
        "book_url": book_url
    }

# função principal que percorre todas as páginas e livros
def scrape_all_books(output_path: str = settings.DATA_PATH) -> list:
    session = create_requests_session()
    books = []

    page_url = settings.SCRAPER_BASE_URL  # começa na raiz do site
    while True:
        logger.info("Buscando página: %s", page_url)
        resp = session.get(page_url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # encontra todos os links de livro na página
        for a in soup.select("article.product_pod h3 a"):
            href = a.get("href")
            book_url = urljoin(page_url, href)
            try:
                book = parse_book_page(session, book_url)
                books.append(book)
                logger.debug("Livro coletado: %s", book["title"])
                # pequeno delay para não sobrecarregar o servidor
                time.sleep(0.2)
            except Exception as e:
                logger.warning("Erro ao coletar %s: %s", book_url, str(e))

        # detecta link "next" para paginação; se não houver, encerra
        next_tag = soup.select_one("li.next > a")
        if next_tag:
            next_href = next_tag.get("href")
            page_url = urljoin(page_url, next_href)
            time.sleep(0.5)
        else:
            break

    # salva CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(books)
    df.insert(0, "id", range(1, len(df) + 1))
    df.to_csv(output_path, index=False)
    logger.info("Salvo %d livros em %s", len(df), output_path)
    return books

# execução direta
if __name__ == "__main__":
    scrape_all_books()