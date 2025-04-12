"""
Gestión de descargas en la interfaz gráfica.
"""

import os
import threading
import queue
from typing import Callable, Dict

import tkinter as tk
from tkinter import messagebox

from downloader import descargar_video, cancelar_descarga
from gui.components.descargar_item import DescargarItem
from utils.historial import agregar_video_historial, cargar_historial, formatear_tamano, eliminar_video_historial

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
        self.hilos_descarga = {}  # Diccionario para relacionar ID con hilo
        self.actualizar_contador_callback = actualizar_contador_callback
        self.archivos_temporales: Dict[int, str] = {}  # Para rastrear archivos temporales por ID de descarga
        self.ultimo_id_descarga = 0  # Para generar IDs únicos
        
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
                tamano_archivo=video.get("tamano", ""),  # Obtener el tamaño si existe
                fecha_descarga=video.get("fecha"),  # Obtener la fecha de descarga del historial
                on_eliminar_callback=self.eliminar_video  # Añadir callback para eliminar
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
                elif tipo == "cancelado":
                    self._procesar_descarga_cancelada(*valores)
                    
        except Exception as e:
            print(f"Error en actualizar_progreso: {str(e)}")
    
    def _procesar_inicio_descarga(self, url: str, id_descarga: int) -> None:
        """Procesa el inicio de una nueva descarga."""
        # Crear nuevo elemento de descarga en el frame de activas
        item = DescargarItem(
            self.frame_activas, 
            url, 
            es_descarga_activa=True, 
            on_cancelar_callback=self.cancelar_descarga,
            id_descarga=id_descarga
        )
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
            
            # Guardar en el historial y obtener la fecha actual que se asignó
            fecha_descarga = agregar_video_historial(nombre_video, ruta_guardado)
            
            # Actualizar el elemento de la lista con la ruta del archivo, su tamaño y la fecha
            self.items_descarga[id_descarga].completado(
                nombre_video, 
                ruta_guardado, 
                tamano_formateado,
                fecha_descarga
            )
            
            # Configurar el callback de eliminación para este elemento
            self.items_descarga[id_descarga].on_eliminar_callback = self.eliminar_video
            
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
            
            # Si el error no fue por cancelación del usuario, mostrar mensaje
            if "cancelada por el usuario" not in error_mensaje.lower():
                messagebox.showerror("Error", f"No se pudo descargar el video.\n{error_mensaje}")
    
    def _procesar_descarga_cancelada(self, id_descarga: int, ruta_temporal: str = None) -> None:
        """Procesa la cancelación de una descarga."""
        if id_descarga in self.items_descarga:
            # Almacenar la ruta temporal para posible limpieza posterior
            if ruta_temporal and os.path.exists(ruta_temporal):
                self.archivos_temporales[id_descarga] = ruta_temporal
                
            # Actualizar la interfaz de usuario
            self.items_descarga[id_descarga].info_var.set("Cancelado")
            
            # Preguntar si quiere eliminar el archivo parcial
            if ruta_temporal and os.path.exists(ruta_temporal):
                respuesta = messagebox.askyesno(
                    "Descarga Cancelada", 
                    "La descarga ha sido cancelada.\n\n¿Desea eliminar el archivo parcialmente descargado?"
                )
                
                if respuesta:
                    try:
                        os.remove(ruta_temporal)
                        print(f"Archivo parcial eliminado: {ruta_temporal}")
                    except Exception as e:
                        print(f"Error al eliminar archivo parcial: {str(e)}")
            
            # Eliminar del diccionario y reorganizar
            del self.items_descarga[id_descarga]
            if id_descarga in self.archivos_temporales:
                del self.archivos_temporales[id_descarga]
                
            self._reorganizar_lista()
    
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
            # Incluir la ruta del archivo, su tamaño y fecha
            item = DescargarItem(
                self.frame_completadas, 
                "", 
                nombre=video["nombre"], 
                es_descarga_activa=False,
                ruta_archivo=video["ruta"],
                tamano_archivo=video.get("tamano", ""),
                fecha_descarga=video.get("fecha"),  # Obtener la fecha de descarga
                on_eliminar_callback=self.eliminar_video  # Añadir callback para eliminar
            )
        
        # Reconstruir las descargas activas (estas irán encima)
        for id_descarga, item in self.items_descarga.items():
            # Recrear el elemento en el frame de descargas activas
            nuevo_item = DescargarItem(
                self.frame_activas, 
                item.url,
                on_cancelar_callback=self.cancelar_descarga,
                id_descarga=id_descarga  # Pasar el ID de descarga
            )
            # Copiar el estado actual
            if hasattr(item, 'progreso') and item.progreso:
                nuevo_item.actualizar(item.progreso["value"], 0)
            # Reemplazar la referencia en el diccionario
            self.items_descarga[id_descarga] = nuevo_item
    
    def iniciar_descarga(self, url: str, calidad: str = "") -> None:
        """
        Inicia la descarga de un video.
        
        Args:
            url: URL del video a descargar
            calidad: ID del formato a descargar (vacío para la mejor calidad)
        """
        if not url:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una URL válida.")
            return
        
        # Generar un ID único para esta descarga
        self.ultimo_id_descarga += 1
        id_descarga = self.ultimo_id_descarga
        
        # Crear y comenzar el hilo de descarga
        hilo_descarga = threading.Thread(
            target=self._descargar_en_hilo,
            args=(url, calidad, id_descarga)
        )
        hilo_descarga.daemon = True
        
        # Guardar referencia al hilo
        self.hilos_descarga[id_descarga] = hilo_descarga
        
        # Iniciar el hilo
        hilo_descarga.start()
    
    def cancelar_descarga(self, id_descarga: int) -> None:
        """
        Cancela una descarga en progreso.
        
        Args:
            id_descarga: ID de la descarga a cancelar
        """
        if id_descarga not in self.items_descarga:
            print(f"ID de descarga no encontrado: {id_descarga}")
            return
            
        # Actualizar la interfaz primero para mostrar que se está cancelando
        self.items_descarga[id_descarga].info_var.set("Cancelando...")
        self.ventana.update_idletasks()  # Forzar actualización de UI
        
        # Iniciar la cancelación real
        if cancelar_descarga(id_descarga):
            print(f"Cancelando descarga: {id_descarga}")
            # La actualización real ocurrirá cuando el hilo de descarga detecte la cancelación
        else:
            print(f"No se pudo cancelar la descarga: {id_descarga}")
            # Si no se pudo cancelar, actualizar el estado a error
            self.cola_actualizaciones.put(("error", id_descarga, "No se pudo cancelar la descarga"))
    
    def _descargar_en_hilo(self, url: str, calidad: str = "", id_descarga: int = None) -> None:
        """
        Realiza la descarga en un hilo separado.
        
        Args:
            url: URL del video a descargar
            calidad: ID del formato a descargar
            id_descarga: ID único para identificar esta descarga
        """
        try:
            # Notificar inicio de descarga
            self.cola_actualizaciones.put(("inicio_descarga", url, id_descarga))
            
            # Realizar la descarga
            ruta_guardado = descargar_video(url, 
                                            lambda p, v: self._progreso_callback(p, v, id_descarga), 
                                            calidad,
                                            id_descarga)
            
            # Notificar que se completó
            self.cola_actualizaciones.put(("completado", id_descarga, ruta_guardado))
        except Exception as e:
            print(f"Error o cancelación en descarga: {str(e)}")
            error_mensaje = str(e)
            
            # Detectar si fue una cancelación
            if "cancelada por el usuario" in error_mensaje.lower():
                # Buscar directorio de descargas para encontrar el archivo temporal
                from utils.config import obtener_directorio_descargas
                directorio = obtener_directorio_descargas()
                # Buscar archivos temporales que puedan coincidir con esta descarga
                try:
                    import glob
                    archivos = glob.glob(os.path.join(directorio, f"temp_download_{id_descarga}.*"))
                    archivo_temporal = archivos[0] if archivos else None
                    
                    # Notificar cancelación
                    self.cola_actualizaciones.put(("cancelado", id_descarga, archivo_temporal))
                except Exception as e2:
                    print(f"Error al buscar archivo temporal: {str(e2)}")
                    self.cola_actualizaciones.put(("cancelado", id_descarga))
            else:
                # Notificar error normal
                self.cola_actualizaciones.put(("error", id_descarga, str(e)))
        finally:
            # Limpiar la referencia al hilo
            if id_descarga in self.hilos_descarga:
                del self.hilos_descarga[id_descarga]
    
    def _progreso_callback(self, porcentaje: float, velocidad: float = 0, id_descarga: int = None) -> None:
        """
        Callback para actualizar el progreso de descarga.
        
        Args:
            porcentaje: Porcentaje de progreso (0-100)
            velocidad: Velocidad de descarga en MB/s
            id_descarga: ID único de la descarga
        """
        self.cola_actualizaciones.put(("progreso", id_descarga, porcentaje, velocidad))
    
    def eliminar_video(self, ruta_archivo: str, eliminar_archivo: bool = False) -> None:
        """
        Elimina un video del historial y opcionalmente del sistema de archivos.
        
        Args:
            ruta_archivo: Ruta del archivo a eliminar
            eliminar_archivo: Si es True, también elimina el archivo físico
        """
        exito, mensaje = eliminar_video_historial(ruta_archivo, eliminar_archivo)
        
        if exito:
            # Reorganizar la lista después de eliminar del historial
            self._reorganizar_lista()
            
            # Actualizar contador de videos descargados
            self._actualizar_contador()
            
            # Mostrar mensaje informativo
            messagebox.showinfo("Información", mensaje)
        else:
            # Mostrar error
            messagebox.showerror("Error", mensaje)
