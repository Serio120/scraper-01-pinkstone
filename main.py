
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
import concurrent.futures

# --- CONFIGURACIÓN DEL LOGGER ---

def setup_logging():
    """Configura el sistema de logging para consola y archivo."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        return logger
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('scraper.log', mode='w')
    file_handler.setFormatter(log_format)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

logger = setup_logging()

# --- MÓDULO DE EXTRACCIÓN (OPTIMIZADO PARA PARALELISMO) ---

def scrape_page(url):
    """Scrapea una única página y devuelve solo los datos de las citas."""
    try:
        logger.info(f"Iniciando scraping de: {url}")
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        quotes_html = soup.find_all('div', class_='quote')
        page_data = []

        for i, quote in enumerate(quotes_html):
            try:
                text = quote.find('span', class_='text').get_text(strip=True)
                author = quote.find('small', class_='author').get_text(strip=True)
                tags_html = quote.find('div', class_='tags').find_all('a', class_='tag')
                tags = [tag.get_text(strip=True) for tag in tags_html]
                page_data.append({'Cita': text, 'Autor': author, 'Etiquetas': ', '.join(tags)})
            except AttributeError:
                logger.error(f"Error de parsing en una cita de {url}. Estructura HTML inválida.")
                continue
        
        logger.info(f"Finalizado scraping de: {url}. Citas encontradas: {len(page_data)}")
        return page_data

    except requests.exceptions.RequestException as e:
        logger.error(f"Fallo al scrapear {url}: {e}")
        return [] # Devuelve lista vacía en caso de error de red
    except Exception as e:
        logger.exception(f"Error inesperado procesando {url}")
        return []

# --- MÓDULO DE ALMACENAMIENTO ---

def save_to_excel(all_data, filename="citas.xlsx"):
    """Guarda los datos en Excel, con logging."""
    if not all_data:
        logger.warning("No se encontraron datos para guardar.")
        return
    try:
        logger.info(f"Guardando {len(all_data)} registros en {filename}.")
        df = pd.DataFrame(all_data)
        df.to_excel(filename, index=False)
        logger.info(f"¡Éxito! El archivo se ha guardado correctamente.")
    except Exception:
        logger.exception("Error crítico al guardar el archivo Excel.")

# --- FUNCIÓN PRINCIPAL (ORQUESTADOR PARALELO) ---

def main():
    """Orquesta el scraping en paralelo de todas las páginas de citas."""
    logger.info("="*50)
    logger.info("INICIANDO PROCESO DE SCRAPING PARALELO")
    logger.info("="*50)

    base_url = "http://quotes.toscrape.com"
    # Generamos la lista de todas las URLs que vamos a atacar
    urls_to_scrape = [f"{base_url}/page/{i}/" for i in range(1, 11)]
    logger.info(f"{len(urls_to_scrape)} páginas serán procesadas en paralelo.")

    all_quotes = []
    # Usamos ThreadPoolExecutor para lanzar peticiones en hilos paralelos
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 'executor.map' aplica 'scrape_page' a cada URL de la lista
        # y mantiene el orden de los resultados.
        results = executor.map(scrape_page, urls_to_scrape)

        for page_quotes in results:
            if page_quotes:
                all_quotes.extend(page_quotes)

    logger.info(f"Scraping paralelo finalizado. Total de citas recolectadas: {len(all_quotes)}.")
    save_to_excel(all_quotes)
    logger.info("FIN DEL PROCESO.")

if __name__ == "__main__":
    main()
