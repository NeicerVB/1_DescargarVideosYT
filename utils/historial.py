"""
Módulo para gestionar el historial de descargas.
"""

import json
import os
import time
from typing import List, Dict, Any, Tuple, Optional

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

def eliminar_video_historial(ruta_archivo: str, eliminar_archivo: bool = False) -> Tuple[bool, str]:
    """
    Elimina un video del historial de descargas y opcionalmente el archivo físico.
    
    Args:
        ruta_archivo: Ruta del archivo a eliminar del historial
        eliminar_archivo: Si es True, también elimina el archivo físico
        
    Returns:
        Tupla con (éxito, mensaje)
    """
    historial = cargar_historial()
    
    # Buscar el elemento a eliminar
    indice_a_eliminar = None
    for i, video in enumerate(historial):
        if video["ruta"] == ruta_archivo:
            indice_a_eliminar = i
            break
    
    if indice_a_eliminar is None:
        return False, "El video no se encontró en el historial"
    
    # Eliminar del historial
    historial.pop(indice_a_eliminar)
    guardar_historial(historial)
    
    mensaje = "Video eliminado del historial"
    
    # Si se solicitó, eliminar también el archivo físico
    if eliminar_archivo and os.path.exists(ruta_archivo):
        try:
            os.remove(ruta_archivo)
            mensaje += " y el archivo fue borrado del disco"
        except Exception as e:
            return True, f"Video eliminado del historial, pero no se pudo borrar el archivo: {str(e)}"
    
    return True, mensaje

def buscar_video_por_ruta(ruta_archivo: str) -> Optional[Dict[str, Any]]:
    """
    Busca un video en el historial por su ruta.
    
    Args:
        ruta_archivo: Ruta del archivo a buscar
        
    Returns:
        Diccionario con información del video o None si no se encuentra
    """
    historial = cargar_historial()
    
    for video in historial:
        if video["ruta"] == ruta_archivo:
            return video
    
    return None
