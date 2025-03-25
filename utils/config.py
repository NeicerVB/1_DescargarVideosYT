"""
Configuraciones y constantes para la aplicación.
"""

import os

# Rutas de directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")

# Archivo de historial
HISTORIAL_ARCHIVO = os.path.join(BASE_DIR, "historial_descargas.json")

# Configuración de la interfaz
ANCHO_VENTANA = 550
ALTO_VENTANA = 500
TITULO_APP = "Descargador de YouTube"
ICONO_APP = os.path.join(ASSETS_DIR, "ico-youtube.ico")

# Configuración de la descarga
FORMATO_VIDEO = 'bestvideo+bestaudio/best'
INTERVALO_ACTUALIZACION_UI = 50  # milisegundos
