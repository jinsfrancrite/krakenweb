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

def download_url(url, folder):
    # Crear la carpeta si no existe
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Descargar el contenido de la URL
    try:
        response = requests.get(url, verify=False)
        if response.status_code != 200:
            print(f"Error al descargar {url} - Código de estado: {response.status_code}")
            escribir_log("Error al descargar "+url+" - Código de estado: "+response.status)
            return False

        # Guardar el contenido HTML
        html_file = os.path.join(folder, "index.html")
        

        # Parsear el HTML para encontrar recursos
        soup = BeautifulSoup(response.text, 'html.parser')

        # Descargar y guardar recursos (CSS, imágenes), excluyendo JS
        for tag in soup.find_all(['link', 'img','script']):
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
                print("--> "+resource_name)    
        
        with open(html_file, 'w', encoding='utf-8') as file:
            #file.write(response.text)
            file.write(str(soup))

        return True

    except Exception as e:
        print(f"Error al procesar {url}: {str(e)}")
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
            print(f"Descargado: {filename}")
            return True
        else:
            print(f"Error al descargar {url} - Código de estado: {response.status_code}")
            escribir_log("Error al descargar "+url+" - Código de estado: "+response.status_code)
            return False
    except Exception as e:
        print(f"Error al descargar {url}: {str(e)}")
        escribir_log("Error al descargar "+url+": "+str(e))
        return False

def generate_random_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

##Funcion JSON para retornar en pantalla
def response_json(boolret, msg):
    jsonret = json.dumps({"message": msg, "status": boolret})
    print(jsonret)
    sys.exit(1)

#Funcion que escribe Log de Operaciones
def escribir_log(mensaje, archivo="app.log"):
    with open(archivo, "a") as log_file:  # "a" para añadir sin sobrescribir
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] {mensaje}\n")

if __name__ == "__main__":
    url = input("Introduce la URL de la página web: ").strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    escribir_log("Descargando la página web: "+url)
    random_code = generate_random_code()    
    folder = os.path.join("paginas", f"dl_{random_code}")
    if download_url(url, folder):
        response_json(True, "Pagina y recursos (sin JS) descargados en la carpeta: "+folder)
    else:
        response_json(False, "Error al descargar la página web "+url)
