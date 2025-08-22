import os
import requests
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs, unquote
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

def download_url(url, folder, folder_cache, main_domain):
    # Crear la carpeta si no existe
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Descargar el contenido de la URL
    try:
        # Datos del proxy
        proxy_user = "informatica_criterion_com_py-dc"
        proxy_pass = "CriterioN2k19"
        proxy_host = "la.residential.rayobyte.com"
        proxy_port = "8000"

        proxy_url = f"{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        # Guardar el contenido HTML
        html_file = os.path.join(folder, "index.html")
        capturar = []
        if "abc.com.py" in url:
            # Sale por CURL usando proxy
            #proxy_arg = f"-x {proxy_url}"
            result = subprocess.run(
                ["curl", "-k", "-s", "-x", proxy_url, url],
                capture_output=True, text=True, check=True
            )
            
            html_string = result.stdout
            capturar = ['link', 'img']
            escribir_log("Sale por CURL con proxy")

            if not html_string:
                escribir_log(f"Error al descargar {url} - No se recibió contenido.")
                html_string = None
        else:
            # Sale por REQUESTS usando proxy
            try:
                response = requests.get(url, verify=False, proxies=proxies, timeout=50)
                html_string = response.text
                capturar = ['link', 'img', 'script']
                escribir_log("Sale por REQUESTS con proxy")

                if response.status_code != 200:
                    escribir_log(f"Error al descargar {url} - Código de estado: {response.status_code}")
                    return False
            except requests.RequestException as e:
                escribir_log(f"Error de conexión: {e}")
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
                    
                    cached_path = download_resource(resource_url, folder, resource_name, folder_cache, main_domain)
                    
                    if cached_path:
                        tag['href'] = cached_path  # Apunta al recurso que hay en cache

            elif tag.name == 'img' and tag.get('src'):
                resource_url = urljoin(url, tag['src'])
                resource_name = obtener_nombre_archivo(resource_url)
                cached_path = download_resource(resource_url, folder, resource_name, folder_cache, main_domain)
                if cached_path:
                    tag['src'] = cached_path  # Apunta al recurso que hay en cache


            elif tag.name == 'script' and tag.get('src'):
                resource_url = urljoin(url, tag['src'])
                resource_name = os.path.basename(urlparse(resource_url).path)
                cached_path = download_resource(resource_url, folder, resource_name, folder_cache, main_domain)
                if cached_path:
                    tag['src'] = cached_path  # Apunta al recurso que hay en cache 
        #Guardar HTML actualizado en el folder con las rutas correspondientes existentes en cache
        html_file = os.path.join(folder, "index.html")            
        with open(html_file, 'w', encoding='utf-8') as file:
            #file.write(response.text)
            file.write(str(soup))
        escribir_log("Página guardada en: " + html_file)
        return html_file
        #return True
    
    except Exception as e:
        print(f"Error al procesar {url}: {str(e)}")
        escribir_log("Error al procesar "+url+": "+str(e))
        return False



def obtener_nombre_archivo(url: str) -> str:
    parsed = urlparse(url)
    # 1. Intentamos sacar el nombre del archivo desde la query (?url=...)
    query_params = parse_qs(parsed.query)
    archivo_url = query_params.get("url", [None])[0]
    if archivo_url:  
        archivo_url = unquote(archivo_url)
        nombre = os.path.basename(urlparse(archivo_url).path)
    else:
        nombre = os.path.basename(parsed.path) if parsed.path else None

    if not nombre or "." not in nombre:
        hash_val = hashlib.md5(url.encode()).hexdigest()
        nombre = f"{hash_val}.bin"
    return nombre
    # 2. Si no hay query con archivo, usamos el path directamente
   # return os.path.basename(parsed.path) if parsed.path else None

#CACHE_FOLDER = 'cache'
ALLOWED_EXTENSIONS = {".css", ".js", ".png", ".jpg", ".jpeg"}
def download_resource(url, folder, filename, folder_cache, main_domain):
    parsed = urlparse(url)
    domain = parsed.netloc
    resource_path = parsed.path.lstrip("/")   # ejemplo: "archivos/Noticias/2025/CONDENA_2/14_web.jpg"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return None  # Ignorar archivos no permitidos

    main_cache_folder = os.path.join(folder_cache, main_domain)
    
    if domain != main_domain:
        file_path = os.path.join(main_cache_folder, domain, resource_path)
        relative_path = os.path.join("../cache", main_domain, domain, resource_path).replace("\\", "/")
    else:
        file_path = os.path.join(main_cache_folder, resource_path)
        relative_path = os.path.join("../cache", main_domain, resource_path).replace("\\", "/")

    #file_path = os.path.join(domain_cache_folder, resource_path)

    os.makedirs(os.path.dirname(file_path), exist_ok=True) # Asegurarse de que la carpeta exista
    
    #relative_path = os.path.join("../cache", domain, resource_path).replace("\\", "/") #ruta relativa que se deberia de insertar en el HTML
    
    #print(f"FILEPATH:  {file_path}")
    
    if os.path.exists(file_path):
        escribir_log(f"El archivo {filename} ya existe en {relative_path}. Usando...")
        return relative_path

    try:
        response = requests.get(url, stream=True, timeout=15, verify=False)
        if response.status_code == 200:
            #file_path = os.path.join(folder, filename)
            with open(file_path, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
                escribir_log(f"Descargado: {relative_path}")
            #return True
            return relative_path
        else:
            escribir_log("Error al descargar "+url+" - Código de estado: "+str(response.status_code))
            return False
    except Exception as e:
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
    """
    return os.getenv(variable_name, default)


def obtener_dominio(url: str) -> str:
    parsed = urlparse(url) #ejemplo de dominio www.ministeriopublico.gov.py
    return parsed.netloc

def get_cache_domain_folder(folder_cache: str, url: str) -> str:
    dominio = obtener_dominio(url)
    domain_folder = os.path.join(folder_cache,dominio)
    os.makedirs(domain_folder, exist_ok=True)
    return domain_folder

def normalize_domain(domain):
    if not domain:
        return None

    domain = domain.lower().strip()
    if domain.startswith("www."):
        domain = domain[4:]

    return domain  


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
    
    parsed=urlparse(url)
    main_domain = normalize_domain(parsed.netloc)

    #print(f"Dominio Principal: {main_domain}")
    folder_path = get_env_variable('FOLDER_PATH')
    folder_cache = get_env_variable('CACHE_FOLDER')

    timestamp = int(time.time())
    rcode = generate_random_code()
    random_code = f"{timestamp}_{rcode}"

    if not folder_path:
        folder_path = "/var/www/html/paginas_archivo/"
    
    if not folder_cache:
        folder_cache = "/var/www/html/paginas_archivo/cache/" #valor por defecto si no existe la variable de entorno
        #folder_cache = os.path.join(folder_path, "cache")

    folder = os.path.join(folder_path, random_code)
    if download_url(url, folder, folder_cache, main_domain):

        datos = {"web_code": random_code, "path_folder": folder}
        response_json(True, "Pagina descargada.",datos)
    else:
        response_json(False, "Error al descargar la página web "+url+folder)
