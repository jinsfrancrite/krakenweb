import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import shutil

def download_url(url, folder):
    # Crear la carpeta si no existe
    if not os.path.exists(folder):
        os.makedirs(folder)

    # Descargar el contenido de la URL
    response = requests.get(url,verify=False)
    print(response)
    if response.status_code != 200:
        print(f"Error al descargar {url}")
        return False

    # Guardar el contenido HTML
    html_file = os.path.join(folder, "index.html")
    with open(html_file, 'w', encoding='utf-8') as file:
        file.write(response.text)

    # Parsear el HTML para encontrar recursos
    soup = BeautifulSoup(response.text, 'html.parser')

    # Descargar y guardar recursos (CSS, JS, imágenes, etc.)
    for tag in soup.find_all(['link', 'script', 'img']):
        if tag.name == 'link' and tag.get('href'):
            resource_url = urljoin(url, tag['href'])
            resource_name = os.path.basename(urlparse(resource_url).path)
            download_resource(resource_url, folder, resource_name)
        elif tag.name == 'script' and tag.get('src'):
            resource_url = urljoin(url, tag['src'])
            resource_name = os.path.basename(urlparse(resource_url).path)
            download_resource(resource_url, folder, resource_name)
        elif tag.name == 'img' and tag.get('src'):
            resource_url = urljoin(url, tag['src'])
            resource_name = os.path.basename(urlparse(resource_url).path)
            download_resource(resource_url, folder, resource_name)

def download_resource(url, folder, filename):
    # Descargar el recurso
    response = requests.get(url, stream=True)
    print(response)
    if response.status_code == 200:
        file_path = os.path.join(folder, filename)
        with open(file_path, 'wb') as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)
        print(f"Descargado: {filename}")
        return True
    else:
        print(f"Error al descargar {url}")
        return False

if __name__ == "__main__":
    url = input("Introduce la URL de la página web: ")
    folder = "paginas/"+urlparse(url).netloc
    dowRet = download_url(url, folder)
    if dowRet:
        print(f"Página y recursos descargados en la carpeta: {folder}")
    else:
        print(f"Error al descargar la página web {url}")