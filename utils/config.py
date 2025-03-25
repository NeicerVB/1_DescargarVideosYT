"""
Configuraciones y constantes para la aplicación.
"""

import os
import json

# Obtener la ruta base de la aplicación
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Archivo de configuración
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# Valores predeterminados
DEFAULT_DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
FORMATO_VIDEO = 'bestvideo+bestaudio/best'
INTERVALO_ACTUALIZACION_UI = 50  # milisegundos
ANCHO_VENTANA = 550
ALTO_VENTANA = 500
TITULO_APP = "Descargador de YouTube"
ICONO_APP = os.path.join(ASSETS_DIR, "ico-youtube.ico")

# Archivo de historial
HISTORIAL_ARCHIVO = os.path.join(BASE_DIR, "historial_descargas.json")

# Carpeta de descargas (puede cambiar durante la ejecución)
DOWNLOADS_DIR = DEFAULT_DOWNLOADS_DIR

# Lista de callbacks para notificar cambios en la configuración
_callbacks_cambio_directorio = []

def registrar_callback_cambio_directorio(callback):
    """Registra un callback para ser notificado cuando cambie el directorio de descargas."""
    if callback not in _callbacks_cambio_directorio:
        _callbacks_cambio_directorio.append(callback)

def cargar_configuracion():
    """Carga la configuración desde el archivo JSON."""
    global DOWNLOADS_DIR
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                download_dir = config.get('downloads_dir', DEFAULT_DOWNLOADS_DIR)
                
                # Verificar que el directorio exista o usar el predeterminado
                if os.path.isdir(download_dir):
                    DOWNLOADS_DIR = download_dir
                else:
                    DOWNLOADS_DIR = DEFAULT_DOWNLOADS_DIR
        except Exception as e:
            print(f"Error al cargar configuración: {str(e)}")
            DOWNLOADS_DIR = DEFAULT_DOWNLOADS_DIR
    else:
        # Si no existe el archivo, usar valores predeterminados
        DOWNLOADS_DIR = DEFAULT_DOWNLOADS_DIR
    
    # Crear el directorio si no existe
    if not os.path.exists(DOWNLOADS_DIR):
        try:
            os.makedirs(DOWNLOADS_DIR)
        except Exception as e:
            print(f"Error al crear directorio de descargas: {str(e)}")
            DOWNLOADS_DIR = DEFAULT_DOWNLOADS_DIR

def guardar_configuracion(downloads_dir=None):
    """Guarda la configuración en un archivo JSON."""
    global DOWNLOADS_DIR
    
    directorio_anterior = DOWNLOADS_DIR
    
    # Actualizar la ruta de descargas si se proporciona
    if downloads_dir and os.path.isdir(downloads_dir):
        DOWNLOADS_DIR = downloads_dir
    
    config = {
        'downloads_dir': DOWNLOADS_DIR
    }
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
            
        # Notificar a los observadores si el directorio cambió
        if directorio_anterior != DOWNLOADS_DIR:
            for callback in _callbacks_cambio_directorio:
                try:
                    callback(DOWNLOADS_DIR)
                except Exception as e:
                    print(f"Error al notificar cambio de directorio: {str(e)}")
                    
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {str(e)}")
        return False

def obtener_directorio_descargas():
    """Obtiene el directorio actual de descargas."""
    return DOWNLOADS_DIR

# Cargar configuración al iniciar
cargar_configuracion()
