import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from flask import Flask  # Importa la clase Flask del módulo flask
from pyvirtualdisplay import Display
import undetected_chromedriver as uc

app = Flask(__name__)  # Crea una instancia de la aplicación Flask

def process_page():
    # Configura el proxy
    proxy = 'http://190.220.1.173:56974'
    proxy_options = {
        'proxy': {
            'http': proxy,
            'https': proxy,
            'no_proxy': '',
            'proxyType': 'MANUAL',
        }
    }

    # Configura las opciones del navegador Chrome WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('start-maximized')
    options.add_argument('enable-automation')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")

    # Agrega las opciones del proxy al navegador
    options.add_experimental_option('prefs', proxy_options)

    browser = webdriver.Chrome(options=options)
    stealth(browser,
            languages=["es"],
            vendor="Debian",
            platform="Linux x86_64",
            webgl_vendor="AMD",
            renderer="AMD Inc."
            )

    url = "https://www.zonaprop.com.ar/inmuebles-alquiler-cordoba.html"
    browser.get(url)

    time.sleep(random.randint(4, 8))

    html = browser.page_source
    print(html)
    
@app.route('/')
def index():
    process_page()

# Inicia la aplicación Flask cuando el script se ejecuta directamente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)  # Inicia el servidor Flask en modo de depuración