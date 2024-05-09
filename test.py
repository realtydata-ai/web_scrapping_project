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
    user_agents = [
    # Add your list of user agents here
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
]
    
    ips = ['45.238.220.1:8181','200.61.16.80:8080']
    


    # Configura las opciones del navegador Chrome WebDriver
    options = webdriver.ChromeOptions()
    #run in headless mode
    options.add_argument("--headless")

    # disable the AutomationControlled feature of Blink rendering engine
    options.add_argument('--disable-blink-features=AutomationControlled')

    # disable pop-up blocking
    options.add_argument('--disable-popup-blocking')

    # start the browser window in maximized mode
    options.add_argument('--start-maximized')

    # disable extensions
    options.add_argument('--disable-extensions')

    # disable sandbox mode
    options.add_argument('--no-sandbox')

    # disable shared memory usage
    options.add_argument('--disable-dev-shm-usage')

    #
    options.add_argument("--log-level=3")

    user_agent = random.choice(user_agents)

    #options.add_argument(f'user-agent={user_agent}')

    proxy = random.choice(ips)
    # Agrega las opciones del proxy al navegador
    options.add_argument(f'--proxy-server={proxy}')

    options.add_experimental_option("excludeSwitches",["enable-automation"])
    options.add_experimental_option("useAutomationExtension",False)
    #options.page_load_strategy = 'normal'

    browser = webdriver.Chrome(options=options)
    stealth(browser,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    url = "https://www.zonaprop.com.ar/inmuebles-alquiler-cordoba.html"
    browser.get(url)

    time.sleep(random.randint(20, 30))

    html = browser.page_source
    print(html)
    
@app.route('/')
def index():
    process_page()

# Inicia la aplicación Flask cuando el script se ejecuta directamente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)  # Inicia el servidor Flask en modo de depuración