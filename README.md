# Version 1.0
- No tiene integracion con el proxy para consultas
# krakenweb
- Programa ejecutable que recibe como parámetro una URL, y la descarga en una carpeta con todos sus recursos

# Requerimientos
- Python 3.6 >=
- Requests
- Bs4
- Dotenv
- PROTONVPN (Opcional)
- 
# Instalación - Librerias Necesarias
- sudo apt update
- sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget

# Instalación 
- cd csvbuilder
- python3 -m venv env
- source env/bin/activate
- pip install requests
- pip install bs4
- pip install dotenv
- pip install wheel (Opcional)
- pip install pyinstaller
# Compilar el ejecutable
- pyinstaller --onefile krakenweb.py

# Cómo utilizar la función desde consola
- cd dist/
- ./krakenweb "$url_pagina_descargar"

## Para ejecutar el programa de forma local en linux mover a /usr/local/bin
- sudo mv dist/krakenweb /usr/local/bin/krakenweb
# Darle permisos de ejecución
- sudo chmod +x /usr/local/bin/krakenweb
# Probar el acceso global
- krakenweb
# Recursos
- Instalar WireGuard y usar datos de ProtonVPN para conectar a la VPN
https://protonvpn.com/support/wireguard-linux
