
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# --- MÓDULO DE EXTRACCIÓN ---

def scrape_page(url):
    """
    Scrapea una única página y devuelve las citas y el enlace a la siguiente página.

    Args:
        url (str): La URL de la página a scrapear.

    Returns:
        tuple: Una tupla conteniendo (lista_de_citas, url_siguiente_pagina).
               Retorna ([], None) si hay un error o no hay citas.
    """
    try:
        print(f"Scrapeando página: {url}")
        response = requests.get(url)
        response.raise_for_status() # Asegura que la petición fue exitosa

        soup = BeautifulSoup(response.content, 'html.parser')
        quotes_html = soup.find_all('div', class_='quote')
        page_data = []

        for quote in quotes_html:
            text = quote.find('span', class_='text').get_text(strip=True)
            author = quote.find('small', class_='author').get_text(strip=True)
            tags_html = quote.find('div', class_='tags').find_all('a', class_='tag')
            tags = [tag.get_text(strip=True) for tag in tags_html]
            page_data.append({
                'Cita': text,
                'Autor': author,
                'Etiquetas': ', '.join(tags)
            })
        
        # Buscar el enlace a la siguiente página
        next_button = soup.find('li', class_='next')
        next_page_url = next_button.find('a')['href'] if next_button else None
        
        return page_data, next_page_url

    except requests.exceptions.RequestException as e:
        print(f"Error de red al acceder a {url}: {e}")
        return [], None
    except Exception as e:
        print(f"Error inesperado al procesar {url}: {e}")
        return [], None

# --- MÓDULO DE ALMACENAMIENTO ---

def save_to_excel(all_data, filename="citas.xlsx"):
    """
    Guarda una lista de diccionarios en un archivo Excel.
    """
    if not all_data:
        print("No hay datos para guardar.")
        return

    try:
        df = pd.DataFrame(all_data)
        df.to_excel(filename, index=False)
        print(f"\n¡Éxito! Se han guardado {len(all_data)} registros en el archivo '{filename}'.")
    except Exception as e:
        print(f"Error al guardar el archivo Excel: {e}")

# --- FUNCIÓN PRINCIPAL (ORQUESTADOR) ---

def main():
    """
    Función principal que orquesta el proceso de scraping.
    """
    base_url = "http://quotes.toscrape.com"
    relative_url = "/"
    all_quotes = []

    print("Iniciando el proceso de scraping completo...")

    while relative_url:
        current_url = base_url + relative_url
        
        page_quotes, next_page_relative_url = scrape_page(current_url)
        
        if page_quotes:
            all_quotes.extend(page_quotes)
        
        relative_url = next_page_relative_url
        
        if relative_url:
            time.sleep(1) # Pausa para ser respetuoso con el servidor

    print("Proceso de scraping finalizado.")
    save_to_excel(all_quotes)

# --- PUNTO DE ENTRADA DEL SCRIPT ---

if __name__ == "__main__":
    main()
