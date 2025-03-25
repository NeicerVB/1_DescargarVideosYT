"""
Punto de entrada principal de la aplicación.
"""

import os
from utils.config import DOWNLOADS_DIR, ASSETS_DIR
from gui.app import YoutubeDownloaderApp

def inicializar_directorios():
    """Inicializa los directorios necesarios para la aplicación."""
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
    app = YoutubeDownloaderApp()
    app.iniciar()

if __name__ == "__main__":
    main()