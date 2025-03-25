"""
Clase principal de la interfaz gráfica.
"""

import tkinter as tk
from tkinter import ttk

from utils.config import ANCHO_VENTANA, ALTO_VENTANA, TITULO_APP, ICONO_APP
from gui.download_manager import DownloadManager

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
        
        # Agregar icono si existe
        try:
            self.ventana.iconbitmap(ICONO_APP)
        except:
            print(f"No se pudo cargar el icono: {ICONO_APP}")
        
        # Centrar la ventana
        self._centrar_ventana(ANCHO_VENTANA, ALTO_VENTANA)
        
        # Construir la interfaz
        self._crear_widgets()
        
        # Iniciar el gestor de descargas
        self.download_manager = DownloadManager(
            self.ventana, 
            self.frame_activas, 
            self.frame_completadas
        )
    
    def _centrar_ventana(self, ancho: int, alto: int) -> None:
        """
        Centra la ventana en la pantalla.
        
        Args:
            ancho: Ancho de la ventana
            alto: Alto de la ventana
        """
        pantalla_ancho = self.ventana.winfo_screenwidth()
        pantalla_alto = self.ventana.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        self.ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    def _crear_widgets(self) -> None:
        """Crea todos los widgets de la interfaz."""
        # Campo de entrada
        self._crear_barra_entrada()
        
        # Área de lista de descargas
        self._crear_area_descargas()
    
    def _crear_barra_entrada(self) -> None:
        """Crea la barra de entrada de URL y botón de descarga."""
        frame_entrada = tk.Frame(self.ventana)
        frame_entrada.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_entrada, text="URL del video:").pack(side=tk.LEFT, padx=(0, 5))
        self.entrada_url = tk.Entry(frame_entrada, width=40)
        self.entrada_url.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Botón de descarga
        boton_descargar = tk.Button(
            frame_entrada, 
            text="Descargar", 
            command=self._iniciar_descarga
        )
        boton_descargar.pack(side=tk.RIGHT, padx=5)
    
    def _crear_area_descargas(self) -> None:
        """Crea el área donde se muestran las descargas."""
        # Marco para la lista de descargas con scrollbar
        frame_contenedor = tk.Frame(self.ventana)
        frame_contenedor.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(frame_contenedor)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas para hacer scroll de la lista
        canvas = tk.Canvas(frame_contenedor, yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=canvas.yview)
        
        # Frame contenedor principal dentro del canvas
        lista_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=lista_frame, anchor="nw")
        
        # Separar los frames: uno para descargas activas (arriba) y otro para completadas (abajo)
        tk.Label(lista_frame, text="Descargas activas:", anchor="w", 
                font=("Helvetica", 10, "bold")).pack(fill=tk.X, pady=(5, 2))
        self.frame_activas = tk.Frame(lista_frame)
        self.frame_activas.pack(fill=tk.X, expand=False)
        
        tk.Label(lista_frame, text="Videos descargados:", anchor="w", 
                font=("Helvetica", 10, "bold")).pack(fill=tk.X, pady=(10, 2))
        self.frame_completadas = tk.Frame(lista_frame)
        self.frame_completadas.pack(fill=tk.X, expand=True)
        
        # Configurar el scrolling
        def configurar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"), width=500, height=400)
        
        lista_frame.bind("<Configure>", configurar_scroll)
    
    def _iniciar_descarga(self) -> None:
        """Callback para el botón de descarga."""
        url = self.entrada_url.get()
        if url:
            # Limpiar el campo de entrada para la siguiente URL
            self.entrada_url.delete(0, tk.END)
            
            # Iniciar la descarga a través del gestor
            self.download_manager.iniciar_descarga(url)
    
    def iniciar(self) -> None:
        """Inicia el bucle principal de la aplicación."""
        self.ventana.mainloop()
