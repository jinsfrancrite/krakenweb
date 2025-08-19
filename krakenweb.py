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
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Proxy
    proxy_user = "informatica_criterion_com_py-dc"
    proxy_pass = "CriterioN2k19"
    proxy_host = "la.residential.rayobyte.com"
    proxy_port = "8000"

    proxy_url = f"{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }

    try:
        html_string = None
        status_code = None

        if "abc.com.py" in url:
            # Usar CURL con proxy
            result = subprocess.run(
                ["curl", "-k", "-s", "-x", proxy_url, "-w", "%{http_code}", url],
                capture_output=True, text=True
            )

            # El contenido y el código HTTP van juntos, los separamos
            if result.returncode != 0:
                escribir_log(f"Error CURL: {result.stderr.strip()}")
                return False, None, f"Error CURL: {result.stderr.strip()}"

            html_string = result.stdout[:-3]  # quitar últimos 3 caracteres (código HTTP)
            status_code = result.stdout[-3:]  # los últimos 3 son el código
            capturar = ['link', 'img']
            escribir_log(f"Sale por CURL con proxy - {url} HTTP {status_code}")

            if not html_string:
                escribir_log(f"Error al descargar {url} - No se recibió contenido.")
                return False, status_code, "Sin contenido recibido"

        else:
            # Usar requests con proxy
            try:
                response = requests.get(url, verify=False, proxies=proxies, timeout=30)
                status_code = response.status_code
                html_string = response.text
                capturar = ['link', 'img', 'script']
                escribir_log(f"Sale por REQUESTS con proxy - {url} HTTP {status_code}")

                if status_code != 200:
                    return False, status_code, f"Error HTTP {status_code}"

            except requests.RequestException as e:
                escribir_log(f"Error de conexión: {e}")
                return False, None, f"Error de conexión: {e}"

        # Si llegamos aquí, tenemos HTML y status_code
        soup = BeautifulSoup(html_string, 'html.parser')

        # Descargar recursos
        for tag in soup.find_all(capturar):
            if tag.name == 'link' and tag.get('href'):
                if 'stylesheet' in tag.get('rel', []):
                    resource_url = urljoin(url, tag['href'])
                    resource_name = os.path.basename(urlparse(resource_url).path)
                    download_resource(resource_url, folder, resource_name)
                    tag['href'] = resource_name
            
            elif tag.name == 'img' and tag.get('src'):
                resource_url = urljoin(url, tag['src'])
                resource_name = os.path.basename(urlparse(resource_url).path)
                download_resource(resource_url, folder, resource_name)
                tag['src'] = resource_name

            elif tag.name == 'script' and tag.get('src'):
                resource_url = urljoin(url, tag['src'])
                resource_name = os.path.basename(urlparse(resource_url).path)
                download_resource(resource_url, folder, resource_name)
                tag['src'] = resource_name

        with open(os.path.join(folder, "index.html"), 'w', encoding='utf-8') as file:
            file.write(str(soup))

        return True, status_code, "Descarga exitosa"

    except Exception as e:
        escribir_log(f"Error al procesar {url}: {str(e)}")
        return False, None, f"Error: {str(e)}"


def download_resource(url, folder, filename):
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
    # Ruta base desde variable de entorno
    log_path = get_env_variable('FOLDER_PATH')
    
    if not log_path:
        raise ValueError("La variable de entorno 'FOLDER_PATH' no está definida o es inválida.")

    logs_dir = os.path.join(log_path, "logs")
    
    # Crear carpeta si no existe
    os.makedirs(logs_dir, exist_ok=True)
    
    # Ruta completa del archivo de log
    log_file_path = os.path.join(logs_dir, archivo)
    
    # Escribir en el log
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {mensaje}\n")

# Función para obtener variables de entorno con valor por defecto
def get_env_variable(variable_name, default=None):
    """
    Obtiene el valor de una variable de entorno.
    Si no existe, devuelve el valor por defecto.
    Para FOLDER_PATH, si no existe usa un valor fijo.
    """
    value = os.getenv(variable_name, default)
    
    # Validación específica para FOLDER_PATH
    if variable_name == 'FOLDER_PATH' and not value:
        value = "/var/www/html/paginas_archivo/"  # Tu ruta fija aquí
    
    return value

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

    success, code, msg = download_url(url, folder)
    if success:
        datos = {"web_code": random_code, "path_folder": folder,"http_code": code}
        response_json(True, "Pagina descargada.",datos)
    else:
        datos = {"http_code": code, "message_error": msg}
        response_json(False, "Error al descargar la página web "+url, datos)
