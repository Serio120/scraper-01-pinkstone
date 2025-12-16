
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging

# --- CONFIGURACIÓN DEL LOGGER ---

def setup_logging():
    """Configura el sistema de logging para consola y archivo."""
    logger = logging.getLogger(__name__) # Usa el nombre del módulo
    logger.setLevel(logging.INFO) # Nivel mínimo de severidad

    # Evita añadir handlers duplicados si se llama varias veces
    if logger.hasHandlers():
        return logger

    # Formato del log
    log_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Handler para escribir en el archivo 'scraper.log' (modo 'w' para sobrescribir)
    file_handler = logging.FileHandler('scraper.log', mode='w')
    file_handler.setFormatter(log_format)

    # Handler para mostrar en la consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)

    # Añadir handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Inicializa el logger para que esté disponible en todo el script
logger = setup_logging()

# --- MÓDULO DE EXTRACCIÓN ---

def scrape_page(url):
    """Scrapea una página, registrando el proceso y manejando errores."""
    try:
        logger.info(f"Accediendo a la página: {url}")
        response = requests.get(url, timeout=15) # Timeout para evitar esperas infinitas
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
                page_data.append({
                    'Cita': text, 'Autor': author, 'Etiquetas': ', '.join(tags)
                })
            except AttributeError:
                logger.error(f"Error de parsing en la cita #{i+1} de {url}. La estructura del HTML puede haber cambiado.")
                continue # Continúa con la siguiente cita

        next_button = soup.find('li', class_='next')
        next_page_url = next_button.find('a')['href'] if next_button else None
        return page_data, next_page_url

    except requests.exceptions.Timeout:
        logger.error(f"Timeout al intentar acceder a {url}.")
        return [], None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error de red al acceder a {url}: {e}")
        return [], None
    except Exception as e:
        logger.exception(f"Error inesperado al procesar {url}. Detalles:")
        return [], None

# --- MÓDULO DE ALMACENAMIENTO ---

def save_to_excel(all_data, filename="citas.xlsx"):
    """Guarda los datos en Excel, con logging."""
    if not all_data:
        logger.warning("No hay datos para guardar en el archivo Excel.")
        return
    try:
        logger.info(f"Creando DataFrame y guardando {len(all_data)} registros en {filename}.")
        df = pd.DataFrame(all_data)
        df.to_excel(filename, index=False)
        logger.info(f"¡Éxito! El archivo se ha guardado correctamente.")
    except Exception:
        logger.exception("Error crítico al intentar guardar el archivo Excel. Detalles:")

# --- FUNCIÓN PRINCIPAL (ORQUESTADOR) ---

def main():
    """Función principal que orquesta el scraping con logging."""
    logger.info("="*50)
    logger.info("INICIANDO NUEVO PROCESO DE SCRAPING DE CITAS")
    logger.info("="*50)
    
    base_url = "http://quotes.toscrape.com"
    relative_url = "/"
    all_quotes = []

    while relative_url:
        current_url = base_url + relative_url
        page_quotes, next_page_relative_url = scrape_page(current_url)
        
        if page_quotes: all_quotes.extend(page_quotes)
        if not next_page_relative_url and page_quotes: logger.info("Se ha alcanzado la última página.")
        
        relative_url = next_page_relative_url
        if relative_url: time.sleep(1)

    logger.info(f"Proceso de scraping finalizado. Total de citas encontradas: {len(all_quotes)}.")
    save_to_excel(all_quotes)
    logger.info("FIN DEL PROCESO.")

if __name__ == "__main__":
    main()
