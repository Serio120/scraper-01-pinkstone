import requests
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl

print("¡Hola desde tu aplicación de Python!")
print("Estoy listo para empezar a recolectar datos.")

# Ejemplo de cómo podrías usar las librerías:
url = "https://example.com"
response = requests.get(url)
soup = BeautifulSoup(response.content, '''html.parser''')
print(soup.title.string)

# ----> ¡Empieza a editar desde aquí! <----

# 1. Descomenta estas líneas
url = "https://quotes.toscrape.com/" # Un buen sitio para practicar
response = requests.get(url)

# 2. Usa BeautifulSoup para analizar el HTML
soup = BeautifulSoup(response.content, 'html.parser')

# 3. Extrae la información que necesitas
title = soup.find('h1')
print(f"El título de la página es: {title.text}")

# 4. Itera sobre elementos, guárdalos en una lista y luego en un Excel...