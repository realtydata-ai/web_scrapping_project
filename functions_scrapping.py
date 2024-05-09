import random
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium_stealth import stealth
from bs4 import BeautifulSoup as bs
import concurrent.futures

def create_dict_features(data):
    """
    Crea un diccionario de características a partir de una cadena de datos.

    :param data: Una cadena de datos que contiene pares de clave:valor y características.
    :return: Un diccionario que contiene las características y los pares de clave:valor.
    """
    # Dividir la cadena de datos en líneas
    lines = data.strip().split('\n')

    # Inicializar el diccionario
    result_dict = {"caracteristicas": []}

    # Iterar sobre cada línea
    for line in lines:
        # Dividir la línea en clave y valor usando ":"
        parts = line.split(':')

        # Si la línea tiene ":", añadir clave y valor al diccionario
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            result_dict[key] = value
        # Si no tiene ":", agregar el contenido como característica
        else:
            result_dict["caracteristicas"].append(line.strip())

    # Convertir la lista de características en una cadena separada por comas
    result_dict["caracteristicas"] = ', '.join(result_dict["caracteristicas"])

    return result_dict

def features_info(buttons, driver):
    """
    Extrae información de características haciendo clic en botones y leyendo el contenido generado.

    :param buttons: Una lista de elementos de botón para hacer clic.
    :param driver: El controlador de Selenium utilizado para interactuar con el navegador web.
    :return: Una cadena que contiene la información de características extraída.
    """
    data = ""  # Inicializar una cadena vacía para almacenar la información

    # Iterar sobre cada botón y hacer clic en él
    for button in buttons:
        # Obtener el texto del botón actual
        button_text = button.find_element(By.CSS_SELECTOR, 'span').text

        # Desplazar la página hacia abajo
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        button.click()
        time.sleep(2)  # Esperar unos segundos para que se cargue el contenido después del clic

        # Encontrar el primer div con el id "reactGeneralFeatures"
        react_general_features_div = driver.find_element(By.ID, 'reactGeneralFeatures')
        
        # Encontrar el primer div dentro de react_general_features_div
        first_div_inside_react_general_features = react_general_features_div.find_element(By.CSS_SELECTOR, 'div')

        # Encontrar el último div dentro del primer div
        last_div_inside_first_div = first_div_inside_react_general_features.find_elements(By.CSS_SELECTOR, 'div')[-1]

        # Obtener la información dentro del último div y añadirla a la cadena de datos
        data += '\n' + last_div_inside_first_div.text

    return data

def get_main_property(text):
    """
    Extrae información principal de una cadena de texto que describe una propiedad.

    :param text: La cadena de texto que describe la propiedad.
    :return: Una tupla que contiene el tipo de propiedad, la superficie cubierta, la cantidad de ambientes/dormitorios y si hay cochera.
    """
    # Dividir la cadena utilizando el carácter '·' como separador
    elementos = text.split('·')

    # Limpiar los elementos eliminando espacios al principio y al final
    elementos_limpios = [elemento.strip() for elemento in elementos]

    # Determinar el tipo de propiedad, la superficie cubierta, la cantidad de ambientes/dormitorios y si hay cochera
    type_property = elementos_limpios[0] if len(elementos_limpios) > 0 else None
    sup_cub = elementos_limpios[1] if len(elementos_limpios) > 1 else None
    ambientes_dormitorios = elementos_limpios[2] if len(elementos_limpios) > 2 else None
    cochera = elementos_limpios[3] if len(elementos_limpios) > 3 else None
    
    return type_property, sup_cub, ambientes_dormitorios, cochera



def get_location(img_map):
    """
    Extrae la ubicación (latitud y longitud) de un mapa de una imagen.

    :param img_map: Un diccionario que contiene la información de la imagen del mapa.
    :return: Una tupla que contiene la latitud y longitud de la ubicación del mapa.
    """
    # Obtener la fuente de la imagen del mapa
    src = img_map['src']

    # Patrón para buscar las coordenadas de los marcadores en la URL
    pattern = r"markers=([-+]?\d*\.?\d+),([-+]?\d*\.?\d+)"

    # Buscar las coordenadas en la URL usando el patrón
    match = re.search(pattern, src)

    if match:
        # Extraer las coordenadas (latitud y longitud) si se encuentra una coincidencia
        latitud = float(match.group(1))
        longitud = float(match.group(2))
    else:
        # Si no se encuentran coordenadas, establecer latitud y longitud como None
        latitud = None
        longitud = None

    return latitud, longitud

def extract_info_from_list(div_tag):
    """
    Extrae información de una lista de características de un elemento div.

    :param div_tag: La etiqueta div que contiene la lista de características.
    :return: Un diccionario que contiene la información extraída de la lista.
    """
    # Definir las claves necesarias con sus valores iniciales como None
    keys = [
        'icon-stotal', 'icon-scubierta', 'icon-ambiente', 'icon-bano', 
        'icon-cochera', 'icon-dormitorio', 'icon-antiguedad', 
        'icon-disposicion', 'icon-orientacion'
    ]
    
    # Inicializar un diccionario con las claves y valores iniciales como None
    info_dict = {key: None for key in keys}
    
    # Encontrar la lista dentro del div
    ul_tag = div_tag.find('ul', class_='section-icon-features')
    
    if ul_tag:
        # Encontrar todos los elementos li dentro de la lista
        li_tags = ul_tag.find_all('li', class_='icon-feature')
        
        # Iterar sobre cada elemento li
        for li_tag in li_tags:
            # Encontrar la etiqueta i dentro del elemento li
            i_tag = li_tag.find('i')
            
            if i_tag:
                # Extraer el nombre de la clase de la etiqueta i
                class_name = i_tag['class'][0]
                
                # Obtener el texto del elemento li
                text = li_tag.get_text(strip=True)
                
                # Si la clase está en las claves necesarias, actualizar el diccionario
                if class_name in keys:
                    # Extraer solo los números de los valores asociados a las claves necesarias
                    numbers = re.findall(r'\d+', text)
                    
                    # Si la clave es 'icon-antiguedad', tomar el número si existe, de lo contrario, el texto completo
                    if class_name == 'icon-antiguedad':
                        info_dict[class_name] = numbers[0] if numbers else text.strip()
                    # Si la clave es 'icon-disposicion' o 'icon-orientacion', tomar el texto completo
                    elif class_name == 'icon-disposicion' or class_name == 'icon-orientacion':
                        info_dict[class_name] = text.strip()
                    # Si la clave no es 'icon-antiguedad', tomar el primer número si existe, de lo contrario, None
                    else:
                        info_dict[class_name] = numbers[0] if numbers else None
                
    
    return info_dict

import re

def extract_middle_path(src):
    """
    Extrae una parte específica de la ruta media de una URL.

    :param src: La URL de la que se extraerá la ruta media.
    :return: Una cadena que representa la parte específica de la ruta media, o None si no se encuentra.
    """
    # Definir el patrón de la expresión regular para capturar los números específicos de la URL
    pattern = r'/(\d+)/(\d+)/(\d+)/(\d+)/(\d+)/(\d+)/'
    
    # Buscar coincidencias con el patrón en la URL
    match = re.search(pattern, src)
    
    if match:
        # Obtener los grupos capturados (segmentos numéricos)
        segments = match.groups()
        
        # Eliminar el primer segmento numérico si es igual a "1"
        if segments[0] == "1":
            segments = segments[1:]
        
        # Eliminar los ceros iniciales de los números capturados
        cleaned_segments = [segment.lstrip('0') for segment in segments]
        
        # Unir los segmentos numéricos específicos y eliminar las barras
        result = ''.join(cleaned_segments)
        
        return result
    else:
        return None

def get_property_overall_data(html_page):
    """
    Extrae información general de una página HTML que describe una propiedad.

    :param html_page: La página HTML que contiene la información de la propiedad.
    :return: Un diccionario que contiene la información general de la propiedad.
    """
    # Parsear la página HTML con BeautifulSoup
    soup = bs(html_page, "lxml")
    
    # Extraer el tipo de propiedad, superficie cubierta, cantidad de ambientes/dormitorios y si hay cochera
    h2_element = soup.find('h2', class_='title-type-sup-property')
    if h2_element:
        type_property, sup_cub, ambientes_dormitorios, cochera = get_main_property(h2_element.text)
    
    # Extraer la ubicación (latitud y longitud) del mapa de la propiedad
    img_map = soup.find('img', id='static-map')
    if img_map:
        lat, long = get_location(img_map)
    
    # Extraer características adicionales de la propiedad
    features = soup.find('div', class_='section-main-features mt-24')
    if features:
        dict_features_property = extract_info_from_list(features)
    
    # Extraer la fecha de publicación de la propiedad
    user_view = soup.find('div', class_='view-users-container')
    if user_view:
        p_tag = user_view.find('p')
        if p_tag:
            publicated_since = p_tag.get_text(strip=True)
    
    # Extraer información del publicador de la propiedad
    publisher_div = soup.find('div', class_='ContainerCard-sc-orxlzl-0 flHWUR')
    if publisher_div:
        img_tag = publisher_div.find('img')
        if publisher_div.find('div', class_='InfoName-sc-orxlzl-4 lnGFmk'):
            name_publisher = publisher_div.find('div', class_='InfoName-sc-orxlzl-4 lnGFmk').get_text(strip=True)
        else:
            name_publisher = None
        if img_tag:
            src = img_tag['src']
            publisher_id = extract_middle_path(src)
        else:
            publisher_id = None
    else:
        name_publisher = None
        publisher_id = None
    
    # Construir el diccionario que contiene la información general de la propiedad
    dict_property = {
        'type_property': type_property,
        'lat': lat,
        'long': long,
        'publicated_since': publicated_since,
        'name_publisher': name_publisher,
        'publisher_id': publisher_id
    }
    
    # Actualizar el diccionario con las características adicionales de la propiedad
    dict_property.update(dict_features_property)
    
    return dict_property

def process_property(to_post):
    """
    Procesa la información de una propiedad para su publicación.

    :param to_post: La URL de la propiedad que se va a procesar.
    :return: Un diccionario que contiene la información procesada de la propiedad.
    """
    ips = ['43.229.10.151:5197']
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


    #options.add_argument(f'user-agent={user_agent}')

    proxy = random.choice(ips)
    # Agrega las opciones del proxy al navegador
    options.add_argument(f'--proxy-server={proxy}')

    options.add_experimental_option("excludeSwitches",["enable-automation"])
    options.add_experimental_option("useAutomationExtension",False)
    #options.page_load_strategy = 'normal'

    driver = webdriver.Chrome(options=options)
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    
    
    # Construir la URL completa de la propiedad a procesar
    url_base = 'https://www.zonaprop.com.ar'
    url_final = url_base + to_post
    
    # Abrir la URL en el navegador
    driver.get(url_final)
    
    # Esperar un tiempo aleatorio para simular el comportamiento humano
    time.sleep(random.randint(20, 30))
    
    # Obtener el código fuente HTML de la página
    html = driver.page_source
    soup = bs(html, "lxml")
    # Esperar unos segundos adicionales para asegurar que la página haya cargado completamente
    time.sleep(20)
    print(soup)
    if soup.find('div',class_='main-container-property'):

        # Obtener la información general de la propiedad
        dict_property = get_property_overall_data(html)

        # Encontrar todos los botones dentro del div con el id "reactGeneralFeatures"
        buttons = driver.find_elements(By.CSS_SELECTOR, '#reactGeneralFeatures button')

        # Extraer información detallada de las características de la propiedad
        data = features_info(buttons, driver)

        # Crear un diccionario con las características de la propiedad
        dict_page = create_dict_features(data)
        
        # Actualizar el diccionario de la propiedad con las características detalladas
        dict_property.update(dict_page)
        
        # Cerrar el navegador
        driver.quit()
        
        return dict_property
    else:
        print("No se encontro la página del articulo, cargando nuevamente")
        process_property(to_post)

def process_page(url):
    """
    Procesa una página de anuncios.

    :param browser: El navegador web utilizado para acceder a la página.
    :param url: La URL de la página que se va a procesar.
    :return: El resultado del procesamiento de la página.
    """
    ips = ['43.229.10.151:5197']
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
    
    # Abrir la URL en el navegador
    browser.get(url) 
    
    # Esperar un tiempo aleatorio para simular el comportamiento humano
    time.sleep(random.randint(4, 8))
    
    # Obtener el código fuente HTML de la página
    html = browser.page_source
    
    # Crear un objeto BeautifulSoup para analizar el HTML
    soup = bs(html, "lxml")

    # Buscar el contenedor de anuncios en la página
    div_postings_container = soup.find('div', class_='postings-container')

    # Verificar si se encontró el contenedor antes de intentar seleccionar elementos
    if div_postings_container:
        # Seleccionar todos los anuncios dentro del contenedor
        anuncios = div_postings_container.find_all(class_='CardContainer-sc-1tt2vbg-5 fvuHxG')

        
        # Procesar los anuncios de la página y devolver el resultado
        return process_list_anuncios(anuncios, url)
    else:
        print(html)
        # Si no se encontró el contenedor, imprimir un mensaje y volver a cargar la página
        print(f'No se encontró el contenedor en la página {url}. Recargando la página...')
        browser.refresh()
        time.sleep(random.randint(10, 12))
        return process_page(url)

def process_list_anuncios(anuncios, url):
    """
    Procesa una lista de anuncios de propiedades.

    :param anuncios: La lista de anuncios que se va a procesar.
    :param url: La URL de la página que contiene los anuncios.
    :return: Una lista de diccionarios que contiene la información procesada de los anuncios.
    """
    data_arr = []  # Lista para almacenar los datos procesados de los anuncios
    
    # Iterar sobre cada anuncio en la lista de anuncios
    for anuncio in anuncios:
        # Encontrar la información principal del anuncio
        div_maininfo_anuncio = anuncio.find("div", class_="PostingCardLayout-sc-i1odl-0 egwEUc")

        # Definir el precio del estado del anuncio
        div_price = anuncio.find("div", attrs={"data-qa": "POSTING_CARD_PRICE"}).get_text(strip=True) if anuncio.find("div", attrs={"data-qa": "POSTING_CARD_PRICE"}) else None

        # Definir el precio de los gastos del anuncio
        div_expense = anuncio.find("div", attrs={"data-qa": "expensas"}).get_text(strip=True) if anuncio.find("div", attrs={"data-qa": "expensas"}) else None

        # Definir el vecindario, ciudad y dirección del anuncio
        div_locationinfo = anuncio.find("div", class_=re.compile(".*LocationBlock.*"))
        if div_locationinfo:
            address = div_locationinfo.find("div", class_=re.compile(".*LocationAddress.*")).get_text(strip=True) if div_locationinfo.find("div", class_=re.compile(".*LocationAddress.*")) else None
            neigh, city = div_locationinfo.find("h2", attrs={"data-qa": "POSTING_CARD_LOCATION"}).get_text(strip=True).split(",") if div_locationinfo.find("h2", attrs={"data-qa": "POSTING_CARD_LOCATION"}) else (None, None)
        else:
            address, neigh, city = (None, None, None)

        # Procesar la página del anuncio y obtener su información detallada
        dict_page = process_property(div_maininfo_anuncio.get('data-to-posting'))

        # Construir un diccionario con la información procesada del anuncio
        data = {
            'data_id': div_maininfo_anuncio.get('data-id'),
            'data_posting_type': div_maininfo_anuncio.get('data-posting-type'),
            'data_qa': div_maininfo_anuncio.get('data-qa'),
            'data_to_posting': div_maininfo_anuncio.get('data-to-posting'),
            'page': url,
            'price': div_price,
            'expenses': div_expense,
            'address': address,
            'neigh': neigh,
            'city': city
        }
        
        # Agregar las claves y valores del diccionario dict_page a data
        data.update(dict_page)
        
        # Imprimir los datos del anuncio
        print(data)
        
        # Agregar el diccionario de datos a la lista de datos
        data_arr.append(data)
    
    return data_arr

def process_page_wrapper(url):
    """
    Envuelve el proceso de una página para manejar excepciones.

    :param url: La URL de la página que se va a procesar.
    :return: El resultado del procesamiento de la página o una lista vacía si se produce un error.
    """
    try:
            # Procesar la página y devolver el resultado
            return process_page(url)
    except Exception as e:
        # Manejar cualquier excepción que ocurra durante el procesamiento de la página
        print(f'Error al procesar la página {url}: {e}')
        return []

