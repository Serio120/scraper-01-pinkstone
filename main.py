"""Scraper de citas de quotes.toscrape.com con exportación a Excel."""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://quotes.toscrape.com"
OUTPUT_FILE = "citas.xlsx"
REQUEST_TIMEOUT = 15
MAX_WORKERS = 10

logger = logging.getLogger(__name__)


def configure_logging(log_file: str | Path | None = "scraper.log") -> logging.Logger:
    """Configura logging una sola vez; no crea archivos al importar el módulo."""
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def scrape_page(url: str, timeout: float = REQUEST_TIMEOUT) -> list[dict[str, str]]:
    """Extrae citas de una página. Un error de red devuelve una lista vacía."""
    logger.info("Iniciando scraping de: %s", url)

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        logger.exception("Fallo al solicitar %s", url)
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    page_data: list[dict[str, str]] = []

    for quote in soup.find_all("div", class_="quote"):
        text_node = quote.find("span", class_="text")
        author_node = quote.find("small", class_="author")

        if text_node is None or author_node is None:
            logger.warning("Se omite una cita con estructura incompleta en %s", url)
            continue

        tags_container = quote.find("div", class_="tags")
        tags = (
            [tag.get_text(strip=True) for tag in tags_container.find_all("a", class_="tag")]
            if tags_container is not None
            else []
        )

        page_data.append(
            {
                "Cita": text_node.get_text(strip=True),
                "Autor": author_node.get_text(strip=True),
                "Etiquetas": ", ".join(tags),
            }
        )

    logger.info("Finalizado scraping de %s. Citas encontradas: %s", url, len(page_data))
    return page_data


def save_to_excel(
    all_data: list[dict[str, str]], filename: str | Path = OUTPUT_FILE
) -> bool:
    """Guarda las citas en Excel y devuelve True si la exportación termina bien."""
    if not all_data:
        logger.warning("No hay datos para guardar.")
        return False

    try:
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        dataframe = pd.DataFrame(all_data, columns=["Cita", "Autor", "Etiquetas"])
        dataframe.to_excel(output_path, index=False)
    except (OSError, ValueError, ImportError):
        logger.exception("No se pudo guardar el archivo Excel: %s", filename)
        return False

    logger.info("Archivo Excel guardado: %s (%s registros)", filename, len(all_data))
    return True


def main(
    base_url: str = BASE_URL,
    pages: int = 10,
    output_file: str | Path = OUTPUT_FILE,
    max_workers: int = MAX_WORKERS,
    timeout: float = REQUEST_TIMEOUT,
) -> int:
    """Descarga las páginas en paralelo y devuelve el número de citas extraídas."""
    if pages < 1:
        raise ValueError("pages debe ser mayor que cero")
    if max_workers < 1:
        raise ValueError("max_workers debe ser mayor que cero")
    if timeout <= 0:
        raise ValueError("timeout debe ser mayor que cero")

    configure_logging()
    urls = [f"{base_url.rstrip('/')}/page/{page}/" for page in range(1, pages + 1)]
    logger.info("Se procesarán %s páginas con hasta %s trabajadores.", pages, max_workers)

    all_quotes: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(lambda url: scrape_page(url, timeout=timeout), urls)
        for page_quotes in results:
            all_quotes.extend(page_quotes)

    logger.info("Scraping finalizado. Total de citas: %s", len(all_quotes))
    save_to_excel(all_quotes, output_file)
    return len(all_quotes)


if __name__ == "__main__":
    main()
