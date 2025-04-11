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
            historial = json.load(f)
        
        # Verificar si es necesario actualizar el historial con información de tamaño
        historial_actualizado = False
        for item in historial:
            if ("tamano" not in item or not item["tamano"]) and os.path.exists(item["ruta"]):
                # Calcular y agregar información de tamaño
                tamano_bytes = os.path.getsize(item["ruta"])
                item["tamano_bytes"] = tamano_bytes
                item["tamano"] = formatear_tamano(tamano_bytes)
                historial_actualizado = True
        
        # Si hubo cambios, guardar el historial actualizado
        if historial_actualizado:
            guardar_historial(historial)
            
        return historial
    except Exception as e:
        print(f"Error al cargar historial: {str(e)}")
        return []

def formatear_tamano(tamano_bytes: int) -> str:
    """
    Formatea un tamaño en bytes a una representación legible (KB, MB, GB).
    
    Args:
        tamano_bytes: Tamaño en bytes
        
    Returns:
        Cadena formateada con unidades apropiadas
    """
    # Convertir a unidades apropiadas
    if tamano_bytes < 1024:
        return f"{tamano_bytes} B"
    elif tamano_bytes < 1024 * 1024:
        return f"{tamano_bytes/1024:.1f} KB"
    elif tamano_bytes < 1024 * 1024 * 1024:
        return f"{tamano_bytes/(1024*1024):.1f} MB"
    else:
        return f"{tamano_bytes/(1024*1024*1024):.1f} GB"

def agregar_video_historial(nombre_video: str, ruta_guardado: str) -> float:
    """
    Agrega un nuevo video al historial de descargas.
    
    Args:
        nombre_video: Nombre del video
        ruta_guardado: Ruta donde se guardó el archivo
        
    Returns:
        El timestamp de la fecha de descarga que se ha agregado
    """
    historial = cargar_historial()
    timestamp = time.time()
    
    # Obtener el tamaño del archivo
    tamano_bytes = os.path.getsize(ruta_guardado)
    tamano_formateado = formatear_tamano(tamano_bytes)
    
    # Añadir al inicio para que aparezca primero en la lista
    historial.insert(0, {
        "nombre": nombre_video,
        "ruta": ruta_guardado,
        "fecha": timestamp,
        "tamano_bytes": tamano_bytes,
        "tamano": tamano_formateado
    })
    
    guardar_historial(historial)
    
    # Devolver el timestamp para que pueda ser utilizado
    return timestamp
