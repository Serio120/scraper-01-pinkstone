
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_all_quotes():
    """
    Esta función recolecta TODAS las citas del sitio 'http://quotes.toscrape.com'
    navegando a través de la paginación. Luego, guarda los datos en un archivo Excel.
    """
    # URL base para construir las URLs de las páginas siguientes
    base_url = "http://quotes.toscrape.com"
    # URL relativa inicial, comenzando en la primera página
    relative_url = "/"
    # Lista para almacenar TODOS los datos extraídos de todas las páginas
    all_scraped_data = []
    
    print("Iniciando scraping con paginación...")

    while relative_url:
        # Construimos la URL completa para la página actual
        current_url = base_url + relative_url
        print(f"Scrapeando página: {current_url}")

        try:
            response = requests.get(current_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            quotes_html = soup.find_all('div', class_='quote')

            if not quotes_html and not all_scraped_data:
                print("No se encontraron citas en la página inicial.")
                return

            for quote in quotes_html:
                text = quote.find('span', class_='text').get_text(strip=True)
                author = quote.find('small', class_='author').get_text(strip=True)
                tags_html = quote.find('div', class_='tags').find_all('a', class_='tag')
                tags = [tag.get_text(strip=True) for tag in tags_html]

                all_scraped_data.append({
                    'Cita': text,
                    'Autor': author,
                    'Etiquetas': ', '.join(tags)
                })
            
            # Buscamos el botón "Next" para la paginación
            next_button = soup.find('li', class_='next')
            if next_button:
                # Si existe, obtenemos el enlace (href) y preparamos para la siguiente iteración
                relative_url = next_button.find('a')['href']
                time.sleep(1) # Pequeña pausa para ser respetuosos con el servidor
            else:
                # Si no hay botón "Next", terminamos el bucle
                relative_url = None
                print("No hay más páginas. Finalizando scraping.")

        except requests.exceptions.RequestException as e:
            print(f"Error en la página {current_url}: {e}")
            break # Salimos del bucle si hay un error de red
        except Exception as e:
            print(f"Ha ocurrido un error inesperado: {e}")
            break

    if not all_scraped_data:
        print("No se pudo recolectar ninguna cita.")
        return

    # Creamos el DataFrame y lo guardamos en Excel
    df = pd.DataFrame(all_scraped_data)
    output_filename = "citas.xlsx"
    df.to_excel(output_filename, index=False)

    print(f"\n¡Éxito! Se han guardado {len(all_scraped_data)} citas en el archivo '{output_filename}'.")

if __name__ == "__main__":
    scrape_all_quotes()
