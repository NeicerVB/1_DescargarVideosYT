"""
Gestión de descargas en la interfaz gráfica.
"""

import os
import threading
import queue
from typing import Callable

import tkinter as tk
from tkinter import messagebox

from downloader import descargar_video
from gui.components import DescargarItem
from utils.historial import agregar_video_historial, cargar_historial, formatear_tamano

class DownloadManager:
    """
    Gestiona las descargas y su visualización en la interfaz.
    
    Attributes:
        ventana: Ventana principal de la aplicación
        frame_activas: Frame para mostrar descargas activas
        frame_completadas: Frame para mostrar descargas completadas
        cola_actualizaciones: Cola para comunicación entre hilos
        items_descarga: Diccionario de items de descarga activos
        actualizar_contador_callback: Función para actualizar el contador de videos
    """
    
    def __init__(self, ventana: tk.Tk, frame_activas: tk.Frame, frame_completadas: tk.Frame, 
                 actualizar_contador_callback: Callable[[int], None] = None):
        """
        Inicializa el gestor de descargas.
        
        Args:
            ventana: Ventana principal de la aplicación
            frame_activas: Frame para mostrar descargas activas
            frame_completadas: Frame para mostrar descargas completadas
            actualizar_contador_callback: Callback para actualizar el contador de videos
        """
        self.ventana = ventana
        self.frame_activas = frame_activas
        self.frame_completadas = frame_completadas
        self.cola_actualizaciones = queue.Queue()
        self.items_descarga = {}
        self.actualizar_contador_callback = actualizar_contador_callback
        
        # Cargar historial de descargas
        self._cargar_historial_ui()
        
        # Iniciar el proceso de actualización de la interfaz
        self._iniciar_actualizacion_ui()
    
    def _actualizar_contador(self):
        """Actualiza el contador de videos descargados."""
        if self.actualizar_contador_callback:
            num_videos = len(cargar_historial())
            self.actualizar_contador_callback(num_videos)
    
    def _cargar_historial_ui(self) -> None:
        """Carga los elementos del historial en la interfaz."""
        historial = cargar_historial()
        for video in historial:
            # Crear elementos para los videos ya descargados en el frame de completadas
            DescargarItem(
                self.frame_completadas, 
                "", 
                nombre=video["nombre"], 
                es_descarga_activa=False,
                ruta_archivo=video["ruta"],
                tamano_archivo=video.get("tamano", "")  # Obtener el tamaño si existe
            )
        
        # Actualizar contador de videos descargados
        self._actualizar_contador()
    
    def _iniciar_actualizacion_ui(self) -> None:
        """Inicia el bucle de actualización de la interfaz."""
        from utils.config import INTERVALO_ACTUALIZACION_UI
        self._actualizar_progreso()
        self.ventana.after(INTERVALO_ACTUALIZACION_UI, self._iniciar_actualizacion_ui)
    
    def _actualizar_progreso(self) -> None:
        """Procesa los mensajes en la cola para actualizar la interfaz."""
        try:
            # Verificar si hay mensajes en la cola
            while not self.cola_actualizaciones.empty():
                tipo, *valores = self.cola_actualizaciones.get_nowait()
                
                if tipo == "inicio_descarga":
                    self._procesar_inicio_descarga(*valores)
                elif tipo == "progreso":
                    self._procesar_progreso_descarga(*valores)
                elif tipo == "completado":
                    self._procesar_descarga_completada(*valores)
                elif tipo == "error":
                    self._procesar_error_descarga(*valores)
                    
        except Exception as e:
            print(f"Error en actualizar_progreso: {str(e)}")
    
    def _procesar_inicio_descarga(self, url: str, id_descarga: int) -> None:
        """Procesa el inicio de una nueva descarga."""
        # Crear nuevo elemento de descarga en el frame de activas
        item = DescargarItem(self.frame_activas, url, es_descarga_activa=True)
        self.items_descarga[id_descarga] = item
    
    def _procesar_progreso_descarga(self, id_descarga: int, porcentaje: float, velocidad: float) -> None:
        """Actualiza el progreso de una descarga activa."""
        if id_descarga in self.items_descarga:
            self.items_descarga[id_descarga].actualizar(porcentaje, velocidad)
            # Forzar actualización visual
            self.ventana.update_idletasks()
    
    def _procesar_descarga_completada(self, id_descarga: int, ruta_guardado: str) -> None:
        """Procesa la finalización exitosa de una descarga."""
        if id_descarga in self.items_descarga:
            # Obtener solo el nombre del video sin extensión
            nombre_archivo = os.path.basename(ruta_guardado)
            nombre_video = os.path.splitext(nombre_archivo)[0]
            
            # Calcular el tamaño del archivo
            tamano_bytes = os.path.getsize(ruta_guardado)
            tamano_formateado = formatear_tamano(tamano_bytes)
            
            # Actualizar el elemento de la lista con la ruta del archivo y su tamaño
            self.items_descarga[id_descarga].completado(nombre_video, ruta_guardado, tamano_formateado)
            
            # Guardar en el historial
            agregar_video_historial(nombre_video, ruta_guardado)
            
            # Reorganizar la lista después de completar la descarga
            # Eliminamos este item del diccionario primero
            del self.items_descarga[id_descarga]
            self._reorganizar_lista()
            
            # Actualizar contador de videos descargados
            self._actualizar_contador()
            
            messagebox.showinfo("Éxito", f"Video guardado en:\n{ruta_guardado}")
    
    def _procesar_error_descarga(self, id_descarga: int, error_mensaje: str) -> None:
        """Procesa un error durante la descarga."""
        if id_descarga in self.items_descarga:
            self.items_descarga[id_descarga].info_var.set("Error")
            del self.items_descarga[id_descarga]  # Eliminar del diccionario
            self._reorganizar_lista()
            messagebox.showerror("Error", f"No se pudo descargar el video.\n{error_mensaje}")
    
    def _reorganizar_lista(self) -> None:
        """Reorganiza la lista para que las descargas activas estén arriba."""
        # Destruir todos los elementos (widgets) en los frames
        for widget in self.frame_activas.winfo_children():
            widget.destroy()
        
        for widget in self.frame_completadas.winfo_children():
            widget.destroy()
        
        # Reconstruir los elementos según el historial
        historial = cargar_historial()
        for video in historial:
            # Incluir la ruta del archivo y su tamaño
            item = DescargarItem(
                self.frame_completadas, 
                "", 
                nombre=video["nombre"], 
                es_descarga_activa=False,
                ruta_archivo=video["ruta"],
                tamano_archivo=video.get("tamano", "")
            )
        
        # Reconstruir las descargas activas (estas irán encima)
        for id_descarga, item in self.items_descarga.items():
            # Recrear el elemento en el frame de descargas activas
            nuevo_item = DescargarItem(self.frame_activas, item.url)
            # Copiar el estado actual
            if hasattr(item, 'progreso') and item.progreso:
                nuevo_item.actualizar(item.progreso["value"], 0)
            # Reemplazar la referencia en el diccionario
            self.items_descarga[id_descarga] = nuevo_item
    
    def iniciar_descarga(self, url: str) -> None:
        """
        Inicia la descarga de un video.
        
        Args:
            url: URL del video a descargar
        """
        if not url:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una URL válida.")
            return
        
        # Crear y comenzar el hilo de descarga
        hilo_descarga = threading.Thread(
            target=self._descargar_en_hilo,
            args=(url,)
        )
        hilo_descarga.daemon = True
        hilo_descarga.start()
    
    def _descargar_en_hilo(self, url: str) -> None:
        """
        Realiza la descarga en un hilo separado.
        
        Args:
            url: URL del video a descargar
        """
        # Usar el ID del hilo como identificador único de esta descarga
        id_descarga = threading.current_thread().ident
        try:
            # Notificar inicio de descarga
            self.cola_actualizaciones.put(("inicio_descarga", url, id_descarga))
            
            # Realizar la descarga
            ruta_guardado = descargar_video(url, self._progreso_callback)
            
            # Notificar que se completó
            self.cola_actualizaciones.put(("completado", id_descarga, ruta_guardado))
        except Exception as e:
            print(f"Error en descarga: {str(e)}")
            self.cola_actualizaciones.put(("error", id_descarga, str(e)))
    
    def _progreso_callback(self, porcentaje: float, velocidad: float = 0) -> None:
        """
        Callback para actualizar el progreso de descarga.
        
        Args:
            porcentaje: Porcentaje de progreso (0-100)
            velocidad: Velocidad de descarga en MB/s
        """
        # El primer elemento de la tupla es el ID de descarga (es pasado por _descargar_en_hilo)
        id_descarga = threading.current_thread().ident
        self.cola_actualizaciones.put(("progreso", id_descarga, porcentaje, velocidad))
