import requests
import random
import json

# 1. Leer el archivo JSON
with open('proxylist.json', 'r', encoding='utf-8') as file:
    # 2. Cargar el contenido del archivo JSON en una variable
    proxies = json.load(file)

proxy = {"http": random.choice(proxies), "https": random.choice(proxies)}
print("Proxy: ", proxy)
response = requests.get("https://www.abc.com.py/politica/2025/03/18/diputados-deja-sin-quorum-la-sesion-para-salvar-a-baran/", proxies=proxy, verify=False)
print(response)