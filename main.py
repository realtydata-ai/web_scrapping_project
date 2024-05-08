from functions_scrapping import *
import concurrent.futures
from flask import Flask  # Importa la clase Flask del módulo flask
import concurrent.futures  # Importa concurrent.futures para manejar ejecuciones concurrentes
from flask import send_file
from io import BytesIO
import pandas as pd
import tempfile

app = Flask(__name__)  # Crea una instancia de la aplicación Flask

# Define la función que ejecuta tu código
def process_urls():
    # URL base para los anuncios de alquiler en Córdoba
    url_base = "https://www.zonaprop.com.ar/inmuebles-alquiler-cordoba.html"
    
    # Construye una lista de URLs de las páginas a procesar
    urls = [f"{url_base}-pagina-{i}.html" for i in range(1, 2)]

    print("Procesando páginas...")

    # Ejecución concurrente de la función process_page_wrapper para cada URL
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_page_wrapper, urls)

    # Combina los resultados de las ejecuciones en una lista de datos
    data_arr = [item for sublist in results for item in sublist]
    return data_arr

# Define la ruta principal ('/') de la aplicación
@app.route('/')
def index():
    """
    Función que se ejecuta cuando se accede a la ruta principal ('/') de la aplicación.

    Returns:
        Archivo CSV: El archivo CSV generado.
    """
    # Ejecuta tu código cuando se acceda a la ruta principal
    data_arr = process_urls()  # Ejecuta la función process_urls para procesar las páginas
    
    # Crear DataFrame
    df = pd.DataFrame(data_arr)
    
    # Guardar DataFrame como CSV en un archivo temporal
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_file:
        df.to_csv(temp_file.name, index=False)
    
    # Devolver el archivo CSV generado como respuesta HTTP
    return send_file(temp_file.name,
                     mimetype='text/csv',
                     as_attachment=True,
                     download_name='data.csv')



# Inicia la aplicación Flask cuando el script se ejecuta directamente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)  # Inicia el servidor Flask en modo de depuración
