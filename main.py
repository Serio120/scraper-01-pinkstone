
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_quotes():
    """
    Esta función recolecta citas de la página 'http://quotes.toscrape.com',
    las procesa y las guarda en un archivo Excel.
    """
    # URL del sitio a scrapear
    url = "http://quotes.toscrape.com/"

    print(f"Iniciando scraping de {url}...")

    try:
        # Realizamos la petición GET a la página
        response = requests.get(url)
        # Lanzamos una excepción si la petición no fue exitosa (código de estado no es 200)
        response.raise_for_status()

        # Analizamos el contenido HTML con BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Buscamos todos los contenedores de citas, que tienen la clase CSS 'quote'
        quotes_html = soup.find_all('div', class_='quote')

        if not quotes_html:
            print("No se encontraron citas en la página.")
            return

        # Creamos una lista para almacenar los datos extraídos
        scraped_data = []

        # Iteramos sobre cada cita encontrada
        for quote in quotes_html:
            # Extraemos el texto de la cita (etiqueta 'span' con clase 'text')
            text = quote.find('span', class_='text').get_text(strip=True)
            # Extraemos el autor (etiqueta 'small' con clase 'author')
            author = quote.find('small', class_='author').get_text(strip=True)
            # Extraemos las etiquetas (todas las etiquetas 'a' dentro de la 'div' con clase 'tags')
            tags_html = quote.find('div', class_='tags').find_all('a', class_='tag')
            tags = [tag.get_text(strip=True) for tag in tags_html]

            # Guardamos los datos extraídos en un diccionario
            scraped_data.append({
                'Cita': text,
                'Autor': author,
                'Etiquetas': ', '.join(tags) # Unimos las etiquetas en un solo string
            })
        
        # Creamos un DataFrame de pandas con los datos recolectados
        df = pd.DataFrame(scraped_data)

        # Nombre del archivo de salida
        output_filename = "citas.xlsx"

        # Guardamos el DataFrame en un archivo Excel, sin el índice
        df.to_excel(output_filename, index=False)

        print(f"¡Éxito! Se han guardado {len(scraped_data)} citas en el archivo '{output_filename}'.")

    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la petición HTTP: {e}")
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")

# Punto de entrada principal del script
if __name__ == "__main__":
    scrape_quotes()
