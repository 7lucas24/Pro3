# pyrefly: ignore [missing-import]
import ray
import numpy as np
import requests
import os
import io
import zipfile

if not os.path.exists("accidentes/"):
    print("Descargando datos...")

    url = "https://www.inegi.org.mx/contenidos/programas/accidentes/datosabiertos/conjunto_de_datos_atus_anual_csv.zip"
    response = requests.get(url)
    response = requests.get(url)

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall("accidentes/")
    print("Listo!")
else:
    print("Los datos ya existen, omitiendo descarga.")# Conectarse al clúster real (no local)
ray.init(address="ray://localhost:10001")

print(ray.cluster_resources())  # Verás los recursos de TODOS los nodos

@ray.remote
def tarea(x):
    import socket
    # Esto te muestra en qué contenedor corrió la tarea
    return f"resultado={x*2} | nodo={socket.gethostname()}"

futures = [tarea.remote(i) for i in range(20)]
resultados = ray.get(futures)

for r in resultados:
    print(r)