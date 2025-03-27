import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import shutil
import random
import string
import json
import sys
from datetime import datetime
from dotenv import load_dotenv
import urllib3
import time
import argparse
import subprocess
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_url(url, folder):
    # Crear la carpeta si no existe
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Descargar el contenido de la URL
    try:

        # Guardar el contenido HTML
        html_file = os.path.join(folder, "index.html")
        capturar = []
        #Si es una URL de abc.com.py usar CURL sino el método con Request
        if "abc.com.py" in url:
            # Código a ejecutar si la URL contiene "abc.com.py"
            result = subprocess.run(["curl", "-k", "-s", url], capture_output=True, text=True, check=True)
            html_string = result.stdout
            capturar = ['link', 'img']
            escribir_log("Sale por CURL")
            if not html_string:
                escribir_log(f"Error al descargar {url} - No se recibió contenido.")
                html_string = None  # O manejarlo según sea necesario
        else:
            response = requests.get(url, verify=False)
            html_string = response.text
            capturar = ['link', 'img','script']
            escribir_log("Sale por REQUESTS")
            if response.status_code != 200:
                #print(f"Error al descargar {url} - Código de estado: {response.status_code}")
                escribir_log("Error al descargar "+url+" - Código de estado: "+response.status)
                return False 

        # Parsear el HTML para encontrar recursos
        soup = BeautifulSoup(html_string, 'html.parser')

        # Descargar y guardar recursos (CSS, imágenes), excluyendo JS
        for tag in soup.find_all(capturar):
            if tag.name == 'link' and tag.get('href'):
                # Solo descargar CSS, ignorar otros tipos de links
                if 'stylesheet' in tag.get('rel', []):
                    resource_url = urljoin(url, tag['href'])
                    resource_name = os.path.basename(urlparse(resource_url).path)
                    download_resource(resource_url, folder, resource_name)
                    tag['href'] = resource_name  # Modificar la referencia en el HTML
            
            elif tag.name == 'img' and tag.get('src'):
                resource_url = urljoin(url, tag['src'])
                resource_name = os.path.basename(urlparse(resource_url).path)
                download_resource(resource_url, folder, resource_name)
                tag['src'] = resource_name  # Modificar la referencia en el HTML

            elif tag.name == 'script' and tag.get('src'):
                resource_url = urljoin(url, tag['src'])
                resource_name = os.path.basename(urlparse(resource_url).path)
                download_resource(resource_url, folder, resource_name)
                tag['src'] = resource_name  # Modificar la referencia en el HTML
        
        with open(html_file, 'w', encoding='utf-8') as file:
            #file.write(response.text)
            file.write(str(soup))

        return True

    except Exception as e:
        #print(f"Error al procesar {url}: {str(e)}")
        escribir_log("Error al procesar "+url+": "+str(e))
        return False

def download_resource(url, folder, filename):
    # Verificar si es un archivo JavaScript (aunque ya lo filtramos antes)
    #if filename.lower().endswith('.js'):
    #    print(f"Omitiendo archivo JavaScript: {filename}")
    #    escribir_log("Omitiendo archivo JavaScript: "+filename)
    #    return False

    # Descargar el recurso
    try:
        response = requests.get(url, stream=True, verify=False)
        if response.status_code == 200:
            file_path = os.path.join(folder, filename)
            with open(file_path, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
            #print(f"Descargado: {filename}")
            return True
        else:
            #print(f"Error al descargar {url} - Código de estado: {response.status_code}")
            escribir_log("Error al descargar "+url+" - Código de estado: "+response.status_code)
            return False
    except Exception as e:
        #print(f"Error al descargar {url}: {str(e)}")
        escribir_log("Error al descargar "+url+": "+str(e))
        return False

def generate_random_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

#Funcion JSON para retornar en pantalla
def response_json(boolret, msg,data=None):
    jsonret = json.dumps({"message": msg, "status": boolret, "data": data})
    print(jsonret)
    sys.exit(1)

#Funcion que escribe Log de Operaciones
def escribir_log(mensaje, archivo="app.log"):
    with open(archivo, "a") as log_file:  # "a" para añadir sin sobrescribir
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {mensaje}\n")

# Función para obtener variables de entorno con valor por defecto
def get_env_variable(variable_name, default=None):
    """
    Obtiene el valor de una variable de entorno.
    Si no existe, devuelve el valor por defecto.
    """
    return os.getenv(variable_name, default)

if __name__ == "__main__":
    # Cargar las variables de entorno desde el archivo .env
    load_dotenv()
    # Ingresar URL o Leer desde consola
    parser = argparse.ArgumentParser(description="Descargar y procesar recursos de una página web.")
    parser.add_argument("url", help="URL de la página web")
    args = parser.parse_args()

    url = args.url.strip()

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    folder_path = get_env_variable('FOLDER_PATH')    
    timestamp = int(time.time())
    rcode = generate_random_code()
    random_code = f"{timestamp}_{rcode}"
    if not folder_path:
        folder_path = "/var/www/html/paginas_archivo/"
    
    folder = os.path.join(folder_path, random_code)

    if download_url(url, folder):
        datos = {"web_code": random_code, "path_folder": folder}
        response_json(True, "Pagina descargada.",datos)
    else:
        response_json(False, "Error al descargar la página web "+url)
