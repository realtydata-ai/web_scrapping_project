import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from flask import Flask  # Importa la clase Flask del módulo flask
import undetected_chromedriver as uc

app = Flask(__name__)  # Crea una instancia de la aplicación Flask

def process_page():
    url = "https://www.zonaprop.com.ar/inmuebles-alquiler-cordoba.html"
    options = webdriver.EdgeOptions()
    options.use_chromium = True
    options.add_argument("start-maximized")
    options.add_argument("--headless")  # Ejecutar en modo headless (sin interfaz gráfica)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # Iniciar el navegador Edge
    browser = webdriver.Edge(options=options)
    # stealth(browser,
    #     languages=["en-US", "en"],
    #     vendor="Debian",
    #     platform="Linux x86_64",
    #     webgl_vendor="Intel Inc.",
    #     renderer="Intel Iris OpenGL Engine",
    #     fix_hairline=True,
    # )


    # Abrir la URL en el navegador
    browser.get(url) 

    # Esperar un tiempo aleatorio para simular el comportamiento humano
    time.sleep(random.randint(4, 8))

    # Obtener el código fuente HTML de la página
    html = browser.page_source
    print(html)

@app.route('/')
def index():
    process_page()

# Inicia la aplicación Flask cuando el script se ejecuta directamente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)  # Inicia el servidor Flask en modo de depuración