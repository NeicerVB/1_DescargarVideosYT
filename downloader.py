"""
Módulo para gestionar la descarga de videos de YouTube.
"""

import os
import re
import threading
from typing import Callable, Optional, Dict

import yt_dlp

from utils.config import obtener_directorio_descargas, FORMATO_VIDEO

# Diccionario para almacenar eventos de cancelación para cada descarga
_eventos_cancelacion: Dict[int, threading.Event] = {}

def limpiar_nombre_archivo(nombre: str) -> str:
    """
    Limpia el nombre del archivo eliminando caracteres especiales que pueden
    causar problemas en los sistemas de archivos.
    
    Args:
        nombre: Nombre del archivo a limpiar
        
    Returns:
        Nombre del archivo limpio
    """
    # Lista de caracteres ilegales en nombres de archivo
    caracteres_ilegales = r'[\\/:*?"<>|]'
    
    # Reemplazar caracteres ilegales con guión bajo
    nombre_limpio = re.sub(caracteres_ilegales, '_', nombre)
    
    # También podemos quitar espacios al principio y al final
    nombre_limpio = nombre_limpio.strip()
    
    # Asegurar que el nombre no esté vacío después de la limpieza
    if not nombre_limpio:
        nombre_limpio = "video"
    
    return nombre_limpio

class ProgresoCallback:
    """Clase para gestionar el callback de progreso de descarga."""
    
    id_descarga = None
    
    @staticmethod
    def progreso_descarga(d: dict) -> None:
        """
        Función de callback para el progreso de la descarga.
        
        Args:
            d: Diccionario con información del progreso de descarga
        """
        # Verificar si la descarga ha sido cancelada usando el ID almacenado
        if (ProgresoCallback.id_descarga is not None and 
            ProgresoCallback.id_descarga in _eventos_cancelacion and 
            _eventos_cancelacion[ProgresoCallback.id_descarga].is_set()):
            # Señalizar la cancelación a yt-dlp
            raise Exception("Descarga cancelada por el usuario")
            
        if d['status'] == 'downloading':
            # Extraer información de progreso
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes', 0)
            
            # Si no hay total_bytes, usar total_bytes_estimate
            if total == 0:
                total = d.get('total_bytes_estimate', 1)  # Usar 1 para evitar división por cero
            
            # Calcular el porcentaje
            if total > 0:
                porcentaje = (downloaded / total) * 100
            else:
                # Si no se puede obtener información de bytes, intentar con _percent_str
                p_str = d.get('_percent_str', '0%')
                try:
                    porcentaje = float(p_str.replace('%', '').strip())
                except ValueError:
                    porcentaje = 0
            
            # También podemos obtener la velocidad para mostrarla
            velocidad = d.get('speed', 0)
            if velocidad:
                velocidad_mb = velocidad / 1048576  # Convertir a MB/s
            else:
                velocidad_mb = 0
            
            # Información de progreso para debugging
            print(f"Progreso: {porcentaje:.1f}%, Velocidad: {velocidad_mb:.2f} MB/s")
            
            # Llamar al callback con el porcentaje y la velocidad
            if hasattr(ProgresoCallback, 'callback') and callable(ProgresoCallback.callback):
                ProgresoCallback.callback(porcentaje, velocidad_mb)
            
            # Verificar cancelación después de cada actualización (para respuesta más rápida)
            if (ProgresoCallback.id_descarga is not None and 
                ProgresoCallback.id_descarga in _eventos_cancelacion and 
                _eventos_cancelacion[ProgresoCallback.id_descarga].is_set()):
                raise Exception("Descarga cancelada por el usuario")

def cancelar_descarga(id_descarga: int) -> bool:
    """
    Cancela una descarga en progreso.
    
    Args:
        id_descarga: ID de la descarga a cancelar
    
    Returns:
        True si se inició el proceso de cancelación, False si la descarga no existe
    """
    if id_descarga in _eventos_cancelacion:
        print(f"Cancelando descarga con ID: {id_descarga}")
        _eventos_cancelacion[id_descarga].set()  # Activar evento de cancelación
        return True
    print(f"ID de descarga {id_descarga} no encontrado para cancelar")
    return False

def descargar_video(url: str, progreso_callback: Optional[Callable[[float, float], None]] = None, 
                   calidad: str = "", id_descarga: int = None) -> str:
    """
    Descarga un video de YouTube.
    
    Args:
        url: URL del video a descargar
        progreso_callback: Función de callback para notificar el progreso
        calidad: ID del formato a descargar (vacío para la mejor calidad)
        id_descarga: ID único para la descarga
        
    Returns:
        Ruta donde se guardó el video
        
    Raises:
        Exception: Si ocurre un error durante la descarga
    """
    # Asegurar que tenemos un ID de descarga
    if id_descarga is None:
        id_descarga = threading.get_ident()
    
    # Almacenar el ID en la clase de callback
    ProgresoCallback.id_descarga = id_descarga
    
    # Crear evento de cancelación para esta descarga
    _eventos_cancelacion[id_descarga] = threading.Event()
    print(f"Registrando descarga con ID: {id_descarga}")
    
    # Asignar el callback a la clase
    ProgresoCallback.callback = progreso_callback
    
    if progreso_callback:
        progreso_callback(0.0, 0.0)  # Inicializa el progreso en 0%
    
    # Obtener el directorio de descargas actual
    directorio_descargas = obtener_directorio_descargas()
    
    # Asegurar que existe el directorio de descargas
    if not os.path.exists(directorio_descargas):
        os.makedirs(directorio_descargas)
    
    # Configurar el formato según la calidad seleccionada
    formato_video = calidad if calidad else FORMATO_VIDEO
    
    # Nombre del archivo temporal
    temp_filename = f"temp_download_{id_descarga}.%(ext)s"
    extension = "mp4"  # Valor por defecto
    
    # Método más simple: descargar primero con nombre temporal y luego renombrar
    opciones = {
        'format': formato_video,
        'outtmpl': os.path.join(directorio_descargas, temp_filename),
        'progress_hooks': [ProgresoCallback.progreso_descarga],
        'quiet': False,
        'no_warnings': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(opciones) as ydl:
            # Extraer info antes de descargar para obtener el nombre y extensión
            pre_info = ydl.extract_info(url, download=False)
            extension = pre_info.get('ext', 'mp4')
            
            # Verificar cancelación antes de comenzar la descarga
            if _eventos_cancelacion[id_descarga].is_set():
                raise Exception("Descarga cancelada por el usuario")
            
            # Iniciar la descarga
            info = ydl.extract_info(url, download=True)
            
            # Generar nombre limpio
            titulo_original = info['title']
            titulo_limpio = limpiar_nombre_archivo(titulo_original)
            
            # Rutas de archivo
            ruta_temporal = os.path.join(directorio_descargas, f"temp_download_{id_descarga}.{extension}")
            ruta_final = os.path.join(directorio_descargas, f"{titulo_limpio}.{extension}")
            
            # Renombrar el archivo
            if os.path.exists(ruta_temporal):
                # Si existe un archivo con el mismo nombre final, lo eliminamos
                if os.path.exists(ruta_final):
                    os.remove(ruta_final)
                os.rename(ruta_temporal, ruta_final)
            
            # Limpiar el evento de cancelación ya que la descarga se completó
            if id_descarga in _eventos_cancelacion:
                del _eventos_cancelacion[id_descarga]
                
            return ruta_final
    except Exception as e:
        print(f"Error durante la descarga (ID: {id_descarga}): {str(e)}")
        
        # Limpiar archivos parciales si fue cancelada
        try:
            archivo_parcial = os.path.join(directorio_descargas, f"temp_download_{id_descarga}.{extension}")
            if os.path.exists(archivo_parcial):
                # No eliminamos automáticamente, dejamos que el gestor lo decida
                pass
        except Exception as clean_error:
            print(f"Error al manejar archivo parcial: {str(clean_error)}")
        
        # Limpiar el evento de cancelación
        if id_descarga in _eventos_cancelacion:
            del _eventos_cancelacion[id_descarga]
            
        raise
