"""
Panel de descargas completadas para la interfaz gráfica.
"""

import tkinter as tk
import platform
from utils.config import ANCHO_VENTANA
from utils.historial import cargar_historial

class CompletedDownloadsPanel:
    """
    Panel que muestra las descargas completadas con scroll.
    """
    
    def __init__(self, parent):
        """
        Inicializa el panel de descargas completadas.
        
        Args:
            parent: Widget padre donde se colocará este panel
        """
        self.parent = parent
        self._crear_panel()
    
    def _crear_panel(self):
        """Crea el panel de descargas completadas con sus widgets."""
        # Crear título con contador
        self._crear_titulo()
        
        # Crear el área con scroll
        self._crear_area_scroll()
    
    def _crear_titulo(self):
        """Crea el título con contador para la sección de videos descargados."""
        # Obtener el número de videos descargados
        num_videos = len(cargar_historial())
        
        # Etiqueta con contador de videos descargados
        self.etiqueta_videos = tk.StringVar(value=f"Videos descargados - {num_videos}")
        tk.Label(self.parent, textvariable=self.etiqueta_videos, anchor="w", 
                font=("Helvetica", 10, "bold")).pack(fill=tk.X, padx=20, pady=(5, 2))
    
    def _crear_area_scroll(self):
        """Crea el área con scroll para los videos descargados."""
        frame_contenedor = tk.Frame(self.parent)
        frame_contenedor.pack(fill=tk.X, padx=20, pady=5)
        
        scrollbar = tk.Scrollbar(frame_contenedor)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ALTURA_LISTA = 220
        self.canvas = tk.Canvas(
            frame_contenedor, 
            yscrollcommand=scrollbar.set,
            bg="#E8E8E8", 
            highlightbackground="#AAAAAA",
            highlightthickness=1,
            height=ALTURA_LISTA
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        lista_frame = tk.Frame(self.canvas, bg="#E8E8E8")
        self.canvas.create_window((0, 0), window=lista_frame, anchor="nw", width=ANCHO_VENTANA-45)
        
        self.frame = tk.Frame(lista_frame, bg="#E8E8E8")
        self.frame.pack(fill=tk.X, expand=True)
        
        lista_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        # Vincular el desplazamiento cuando el usuario interactúa con el canvas
        self._configurar_eventos_desplazamiento()
    
    def _configurar_eventos_desplazamiento(self):
        """Configura los eventos de desplazamiento con la rueda del ratón."""
        # Función unificada para el desplazamiento con la rueda
        def _on_mousewheel(event):
            # Determinar la dirección y cantidad de desplazamiento según el sistema
            delta = 0
            if platform.system() == "Windows":
                delta = -1 * int(event.delta / 120)
            elif platform.system() == "Darwin":  # macOS
                delta = -1 * int(event.delta)
            else:  # Linux
                if event.num == 4:
                    delta = -1
                elif event.num == 5:
                    delta = 1
            
            # Realizar el desplazamiento
            if delta != 0:
                self.canvas.yview_scroll(delta, "units")
            
            return "break"  # Prevenir que el evento se propague
        
        # Vincular eventos solo cuando el mouse está sobre el canvas
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
        
        # Guardar la referencia a la función para poder vincular/desvincular
        self._on_mousewheel_func = _on_mousewheel

    def _bind_mousewheel(self, event):
        """Vincula los eventos de rueda del ratón cuando el cursor entra al canvas."""
        sistema = platform.system()
        if sistema == "Windows" or sistema == "Darwin":
            self.canvas.bind_all("<MouseWheel>", self._on_mousewheel_func)
        else:
            self.canvas.bind_all("<Button-4>", self._on_mousewheel_func)
            self.canvas.bind_all("<Button-5>", self._on_mousewheel_func)

    def _unbind_mousewheel(self, event):
        """Desvincula los eventos de rueda del ratón cuando el cursor sale del canvas."""
        sistema = platform.system()
        if sistema == "Windows" or sistema == "Darwin":
            self.canvas.unbind_all("<MouseWheel>")
        else:
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
    
    def actualizar_contador(self, num_videos):
        """
        Actualiza el contador de videos descargados en la interfaz.
        
        Args:
            num_videos: Número de videos descargados
        """
        self.etiqueta_videos.set(f"Videos descargados - {num_videos}")
