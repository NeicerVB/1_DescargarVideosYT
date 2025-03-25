"""
Módulo para gestionar el historial de descargas.
"""

import json
import os
import time
from typing import List, Dict, Any

from utils.config import HISTORIAL_ARCHIVO

def guardar_historial(videos_descargados: List[Dict[str, Any]]) -> None:
    """
    Guarda la lista de videos descargados en un archivo JSON.
    
    Args:
        videos_descargados: Lista de diccionarios con información de videos
    """
    try:
        with open(HISTORIAL_ARCHIVO, 'w', encoding='utf-8') as f:
            json.dump(videos_descargados, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error al guardar historial: {str(e)}")

def cargar_historial() -> List[Dict[str, Any]]:
    """
    Carga la lista de videos descargados desde un archivo JSON.
    
    Returns:
        Lista de diccionarios con información de videos descargados
    """
    if not os.path.exists(HISTORIAL_ARCHIVO):
        return []
    
    try:
        with open(HISTORIAL_ARCHIVO, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar historial: {str(e)}")
        return []

def agregar_video_historial(nombre_video: str, ruta_guardado: str) -> None:
    """
    Agrega un nuevo video al historial de descargas.
    
    Args:
        nombre_video: Nombre del video
        ruta_guardado: Ruta donde se guardó el archivo
    """
    historial = cargar_historial()
    timestamp = time.time()
    
    # Añadir al inicio para que aparezca primero en la lista
    historial.insert(0, {
        "nombre": nombre_video,
        "ruta": ruta_guardado,
        "fecha": timestamp
    })
    
    guardar_historial(historial)
