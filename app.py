# pyrefly: ignore [missing-import]
import ray
import numpy as np
import requests
import os
import io
import zipfile
import subprocess


if not os.path.exists("accidentes/"):
    print("Descargando datos...")

    url = "https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/conjunto_de_datos_atus_anual_csv.zip"
    response = requests.get(url)

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall("accidentes/")
    print("Listo!")
else:
    print("Los datos ya existen, omitiendo descarga.")# Conectarse al clúster real (no local)

print("Ejecutando procesar_datos.py...")
subprocess.run(["python", "procesar_datos.py"], check=True)

print("Iniciando Streamlit dashboard...")
subprocess.run(["streamlit", "run", "dashboard.py"], check=True)