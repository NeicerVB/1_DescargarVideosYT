"""
Clase principal de la interfaz gráfica.
"""

import tkinter as tk

from utils.config import (
    ANCHO_VENTANA, ALTO_VENTANA, TITULO_APP, ICONO_APP,
    registrar_callback_cambio_directorio
)
from gui.download_manager import DownloadManager
from gui.components.input_panel import InputPanel
from gui.components.active_downloads import ActiveDownloadsPanel
from gui.components.completed_downloads import CompletedDownloadsPanel
from gui.components.folder_controls import FolderControls
from gui.utils.ui_helpers import centrar_ventana

class YoutubeDownloaderApp:
    """
    Aplicación principal del descargador de YouTube.
    
    Attributes:
        ventana: Ventana principal de Tkinter
        download_manager: Gestor de descargas
    """
    
    def __init__(self):
        """Inicializa la aplicación."""
        self.ventana = tk.Tk()
        self.ventana.title(TITULO_APP)
        
        # Configurar ventana
        self._configurar_icono()
        centrar_ventana(self.ventana, ANCHO_VENTANA, ALTO_VENTANA)
        self.ventana.resizable(False, False)
        
        # Crear componentes
        self._crear_componentes()
        
        # Iniciar el gestor de descargas
        self.download_manager = DownloadManager(
            self.ventana, 
            self.active_downloads.frame, 
            self.completed_downloads.frame,
            self.completed_downloads.actualizar_contador
        )
        
        # Conectar eventos entre componentes
        self._conectar_eventos()
        
        # Configurar manejo de rueda del ratón a nivel de aplicación
        self._configurar_desplazamiento_global()
    
    def _configurar_icono(self):
        """Configura el icono de la aplicación si está disponible."""
        try:
            self.ventana.iconbitmap(ICONO_APP)
        except Exception:
            print(f"No se pudo cargar el icono: {ICONO_APP}")
    
    def _crear_componentes(self):
        """Crea todos los componentes de la interfaz."""
        # Panel de entrada de URL
        self.input_panel = InputPanel(self.ventana)
        
        # Panel de descargas activas
        self.active_downloads = ActiveDownloadsPanel(self.ventana)
        
        # Panel de descargas completadas
        self.completed_downloads = CompletedDownloadsPanel(self.ventana)
        
        # Controles de carpeta de destino
        self.folder_controls = FolderControls(self.ventana)
        
        # Registrar callback para cambios en la carpeta de descargas
        registrar_callback_cambio_directorio(self.folder_controls.actualizar_etiqueta_carpeta)
    
    def _conectar_eventos(self):
        """Conecta los eventos entre los diferentes componentes."""
        # Conectar botón de descarga con el gestor de descargas
        self.input_panel.set_download_callback(self._iniciar_descarga)
    
    def _iniciar_descarga(self, url, calidad=""):
        """
        Callback para el botón de descarga.
        
        Args:
            url: URL del video a descargar
            calidad: ID del formato de calidad seleccionado (opcional)
        """
        if url:
            # Iniciar la descarga a través del gestor, pasando la calidad seleccionada
            self.download_manager.iniciar_descarga(url, calidad)
    
    def iniciar(self):
        """Inicia el bucle principal de la aplicación."""
        self.ventana.mainloop()
    
    def _configurar_desplazamiento_global(self):
        """
        Configura el comportamiento de desplazamiento global para la aplicación.
        Esta función garantiza que todos los widgets con capacidad de desplazamiento
        respondan correctamente a los eventos de la rueda del ratón.
        """
        # Definimos una función que permitirá que el widget bajo el cursor
        # reciba los eventos de la rueda del ratón
        def _redirigir_evento_scroll(event):
            # Obtener el widget bajo el cursor
            x, y = event.x_root, event.y_root
            widget_bajo_cursor = event.widget.winfo_containing(x, y)
            
            # Verificar si el widget o alguno de sus padres es un canvas
            widget_actual = widget_bajo_cursor
            while widget_actual is not None:
                if isinstance(widget_actual, tk.Canvas) and widget_actual.winfo_ismapped():
                    # Redirigir el evento al canvas encontrado
                    widget_actual.event_generate("<MouseWheel>", 
                                              delta=event.delta, 
                                              rootx=event.x_root, 
                                              rooty=event.y_root)
                    return "break"
                # Subir en la jerarquía de widgets
                parent_widget = widget_actual.master
                if parent_widget == widget_actual:
                    break
                widget_actual = parent_widget
            
            # Si no encontramos un canvas, dejamos que el evento se procese normalmente
            return ""
