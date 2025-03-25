"""
Punto de entrada principal de la aplicación.
"""

import os
from utils.config import DOWNLOADS_DIR, ASSETS_DIR, cargar_configuracion

def inicializar_directorios():
    """Inicializa los directorios necesarios para la aplicación."""
    # Cargar la configuración para obtener la carpeta de descargas actual
    cargar_configuracion()
    
    for directorio in [DOWNLOADS_DIR, ASSETS_DIR]:
        if not os.path.exists(directorio):
            try:
                os.makedirs(directorio)
                print(f"Directorio creado: {directorio}")
            except Exception as e:
                print(f"Error al crear directorio {directorio}: {str(e)}")

def main():
    """Función principal de la aplicación."""
    # Inicializar directorios necesarios
    inicializar_directorios()
    
    # Iniciar la aplicación gráfica
    from gui.app import YoutubeDownloaderApp
    app = YoutubeDownloaderApp()
    app.iniciar()

if __name__ == "__main__":
    main()