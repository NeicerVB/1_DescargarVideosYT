"""
Panel de descargas activas para la interfaz gráfica.
"""

import tkinter as tk
import platform
from utils.config import ANCHO_VENTANA

class ActiveDownloadsPanel:
    """
    Panel que muestra las descargas activas con scroll.
    """
    
    def __init__(self, parent):
        """
        Inicializa el panel de descargas activas.
        
        Args:
            parent: Widget padre donde se colocará este panel
        """
        self.parent = parent
        self._crear_panel()
    
    def _crear_panel(self):
        """Crea el panel de descargas activas con sus widgets."""
        # Crear título de sección
        self._crear_titulo()
        
        # Crear contenedor de descargas activas
        self._crear_contenedor()
        
        # Borde para distinguir la sección
        separador = tk.Frame(self.parent, height=1, bg="#D0D0D0")
        separador.pack(fill=tk.X, padx=15, pady=(0,5))
    
    def _crear_titulo(self):
        """Crea el título para la sección de descargas activas."""
        frame_titulo = tk.Frame(self.parent)
        frame_titulo.pack(fill=tk.X, padx=20, pady=(5,0))
        
        # Etiqueta de título para la sección
        tk.Label(frame_titulo, text="Descargas activas:", anchor="w", 
                font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, pady=(0, 2))
                
        # Se podría agregar aquí un botón para cancelar todas las descargas si se necesita
    
    def _crear_contenedor(self):
        """Crea el contenedor con scroll para las descargas activas."""
        frame_contenedor = tk.Frame(self.parent)
        frame_contenedor.pack(fill=tk.X, padx=20, pady=(0,5))
        
        self.canvas = tk.Canvas(frame_contenedor, height=80, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.contenido = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.contenido, anchor="nw", width=ANCHO_VENTANA-45)
        
        self.contenido.bind("<Configure>", self._configurar_scroll)
        self.frame = self.contenido
        
        scrollbar = tk.Scrollbar(frame_contenedor, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Vincular el desplazamiento solo cuando el cursor entra en el canvas
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

    def _bind_mousewheel(self, event):
        sistema = platform.system()
        if sistema == "Windows":
            self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        elif sistema == "Darwin":
            self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        else:
            self.canvas.bind("<Button-4>", self._on_mousewheel)
            self.canvas.bind("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self, event):
        sistema = platform.system()
        if sistema in ["Windows", "Darwin"]:
            self.canvas.unbind("<MouseWheel>")
        else:
            self.canvas.unbind("<Button-4>")
            self.canvas.unbind("<Button-5>")

    def _on_mousewheel(self, event):
        sistema = platform.system()
        if sistema == "Windows":
            self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")
        elif sistema == "Darwin":
            self.canvas.yview_scroll(-1 * int(event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        return "break"
    
    def _configurar_scroll(self, event):
        """Configura la región de scroll para el canvas de descargas activas."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
