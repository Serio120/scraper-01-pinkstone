# Scraper de citas

Scraper educativo en Python que extrae citas, autores y etiquetas de [Quotes to Scrape](https://quotes.toscrape.com/) y exporta los resultados a un archivo Excel.

## Características

- Descarga varias páginas en paralelo con `ThreadPoolExecutor`.
- Establece un timeout HTTP y comprueba los códigos de estado.
- Omite entradas con HTML incompleto sin detener el proceso.
- Exporta las columnas `Cita`, `Autor` y `Etiquetas` a Excel.
- Registra el progreso en consola y en `scraper.log`.
- Incluye pruebas automatizadas para parsing, errores de red, exportación y orquestación.

## Requisitos

- Python 3.10 o superior.
- pip.

## Instalación

Se recomienda utilizar un entorno virtual:

```bash
python -m venv .venv
```

Actívalo:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

Instala las dependencias:

```bash
python -m pip install -r requirements-dev.txt
```

## Ejecución

```bash
python main.py
```

Por defecto se consultan las diez primeras páginas y se genera `citas.xlsx` en el directorio actual. El log se escribe en `scraper.log`.

## Pruebas

```bash
pytest
```

Las pruebas utilizan respuestas HTML simuladas y no necesitan acceder a Internet.

## Estructura

```text
.
├── .github/workflows/ci.yml
├── tests/
│   └── test_main.py
├── main.py
├── requirements.txt
└── requirements-dev.txt
```

## Uso responsable

Este proyecto está pensado para practicar scraping sobre un sitio de demostración. Respeta los términos del sitio, sus límites de uso y evita aumentar el paralelismo o la frecuencia de peticiones sin motivo.
