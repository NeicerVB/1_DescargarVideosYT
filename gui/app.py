"""
Clase principal de la interfaz gráfica.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import platform
import subprocess
from PIL import Image, ImageTk

from utils.config import (
    ANCHO_VENTANA, ALTO_VENTANA, TITULO_APP, ICONO_APP, 
    guardar_configuracion, obtener_directorio_descargas, registrar_callback_cambio_directorio
)
from gui.download_manager import DownloadManager
from utils.historial import cargar_historial

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
        except Exception:
            print(f"No se pudo cargar el icono: {ICONO_APP}")
        
        # Centrar la ventana
        self._centrar_ventana(ANCHO_VENTANA, ALTO_VENTANA)
        
        # Hacer que la ventana tenga un tamaño fijo (no redimensionable)
        self.ventana.resizable(False, False)
        
        # Registrar callback para cambios en la carpeta de descargas
        registrar_callback_cambio_directorio(self._actualizar_etiqueta_carpeta)
        
        # Construir la interfaz
        self._crear_widgets()
        
        # Iniciar el gestor de descargas
        self.download_manager = DownloadManager(
            self.ventana, 
            self.frame_activas, 
            self.frame_completadas,
            self.actualizar_contador_videos
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
        
        # Sección de descargas activas (ahora fuera del scrollbar)
        self._crear_seccion_descargas_activas()
        
        # Área de lista de videos descargados (con scrollbar)
        self._crear_area_videos_descargados()
        
        # Botón para abrir carpeta de descargas (ahora fuera del scrollbar)
        self._crear_boton_ubicacion()
    
    def _crear_barra_entrada(self) -> None:
        """Crea la barra de entrada de URL y botón de descarga."""
        frame_entrada = tk.Frame(self.ventana)
        frame_entrada.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_entrada, text="URL del video:").pack(side=tk.LEFT, padx=(0, 5))
        self.entrada_url = tk.Entry(frame_entrada, width=40)
        self.entrada_url.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Contenedor para los botones (para organizarlos mejor)
        frame_botones = tk.Frame(frame_entrada)
        frame_botones.pack(side=tk.RIGHT)
        
        # Botón para seleccionar carpeta de destino
        try:
            # Cargar ícono para el botón
            ruta_icono = os.path.join("assets", "carpeta-abierta.png")
            img_original = Image.open(ruta_icono)
            img_redimensionada = img_original.resize((20, 20), Image.LANCZOS)
            self.icono_carpeta_destino = ImageTk.PhotoImage(img_redimensionada)
            
            boton_seleccionar_carpeta = tk.Button(
                frame_botones,
                image=self.icono_carpeta_destino,
                command=self._seleccionar_carpeta_destino,
                relief=tk.FLAT,
                bd=1,
                highlightthickness=0,
                cursor="hand2"
            )
            boton_seleccionar_carpeta.pack(side=tk.LEFT, padx=2)
            
            # Añadir tooltip
            self._crear_tooltip(boton_seleccionar_carpeta, "Seleccionar carpeta de destino")
        except Exception as e:
            print(f"Error al crear botón de carpeta destino: {str(e)}")
        
        # Botón de descarga
        boton_descargar = tk.Button(
            frame_botones, 
            text="Descargar", 
            command=self._iniciar_descarga
        )
        boton_descargar.pack(side=tk.LEFT, padx=5)
    
    def _seleccionar_carpeta_destino(self):
        """Abre un diálogo para seleccionar la carpeta de destino de las descargas."""
        # Obtener directorio actual
        directorio_actual = obtener_directorio_descargas()
        
        carpeta_seleccionada = filedialog.askdirectory(
            title="Seleccionar carpeta de destino",
            initialdir=directorio_actual
        )
        
        if carpeta_seleccionada:
            # Actualizar la configuración
            if guardar_configuracion(carpeta_seleccionada):
                # Mostrar mensaje informativo
                messagebox.showinfo(
                    "Carpeta de destino", 
                    f"Las descargas se guardarán en:\n{carpeta_seleccionada}"
                )
                
                # Actualizar etiqueta con la ruta actual
                self._actualizar_etiqueta_carpeta(carpeta_seleccionada)
            else:
                messagebox.showerror(
                    "Error", 
                    "No se pudo establecer la carpeta de destino.\nVerifique que tiene permisos de escritura."
                )
    
    def _crear_tooltip(self, widget, texto):
        """Crea un tooltip para un widget."""
        def mostrar_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Crear ventana emergente
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(self.tooltip, text=texto, bg="#FFFFDD", 
                           relief=tk.SOLID, borderwidth=1, padx=5, pady=2)
            label.pack()
            
        def ocultar_tooltip(event):
            if hasattr(self, "tooltip"):
                self.tooltip.destroy()
                
        widget.bind("<Enter>", mostrar_tooltip)
        widget.bind("<Leave>", ocultar_tooltip)
    
    def _crear_seccion_descargas_activas(self) -> None:
        """Crea la sección de descargas activas fuera del scrollbar con altura fija."""
        frame_titulo = tk.Frame(self.ventana)
        frame_titulo.pack(fill=tk.X, padx=20, pady=(5,0))
        
        # Etiqueta de título para la sección
        tk.Label(frame_titulo, text="Descargas activas:", anchor="w", 
                font=("Helvetica", 10, "bold")).pack(fill=tk.X, pady=(0, 2))
        
        # Contenedor con altura fija para las descargas activas
        frame_contenedor = tk.Frame(self.ventana)
        frame_contenedor.pack(fill=tk.X, padx=20, pady=(0,5))
        
        # Crear un canvas con altura fija
        self.canvas_activas = tk.Canvas(frame_contenedor, height=80, highlightthickness=0)
        self.canvas_activas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Frame interno para los elementos de descarga activa
        self.frame_activas_contenido = tk.Frame(self.canvas_activas)
        self.canvas_activas.create_window((0, 0), window=self.frame_activas_contenido, anchor="nw", width=ANCHO_VENTANA-45)
        
        # Actualizar el canvas cuando el contenido cambie
        def _configurar_scroll_activas(event):
            self.canvas_activas.configure(scrollregion=self.canvas_activas.bbox("all"))
        
        self.frame_activas_contenido.bind("<Configure>", _configurar_scroll_activas)
        
        # Este es el frame que se usará para añadir elementos de descarga
        self.frame_activas = self.frame_activas_contenido
        
        # Añadir scrollbar vertical - solo será visible si es necesario
        scrollbar_activas = tk.Scrollbar(frame_contenedor, orient="vertical", command=self.canvas_activas.yview)
        self.canvas_activas.configure(yscrollcommand=scrollbar_activas.set)
        scrollbar_activas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Borde para distinguir la sección
        separador = tk.Frame(self.ventana, height=1, bg="#D0D0D0")
        separador.pack(fill=tk.X, padx=15, pady=(0,5))
    
    def _crear_area_videos_descargados(self) -> None:
        """Crea el área donde se muestran los videos descargados con scrollbar."""
        # Obtener el número de videos descargados
        num_videos = len(cargar_historial())
        
        # Etiqueta con contador de videos descargados (fuera del scrollbar)
        self.etiqueta_videos = tk.StringVar(value=f"Videos descargados - {num_videos}")
        tk.Label(self.ventana, textvariable=self.etiqueta_videos, anchor="w", 
                font=("Helvetica", 10, "bold")).pack(fill=tk.X, padx=20, pady=(5, 2))
        
        # Marco para la lista de descargas con scrollbar
        frame_contenedor = tk.Frame(self.ventana)
        frame_contenedor.pack(fill=tk.X, padx=20, pady=5)  # Cambiado de BOTH a X y quitado expand=True
        
        # Scrollbar
        scrollbar = tk.Scrollbar(frame_contenedor)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Definir la altura fija para el canvas
        ALTURA_LISTA = 220  # Reducida de 170 a 120 píxeles
        
        # Canvas para hacer scroll de la lista con altura explícitamente establecida
        canvas = tk.Canvas(
            frame_contenedor, 
            yscrollcommand=scrollbar.set,
            bg="#E8E8E8", 
            highlightbackground="#AAAAAA",
            highlightthickness=1,
            height=ALTURA_LISTA  # Establecer altura directamente aquí
        )
        canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)
        scrollbar.config(command=canvas.yview)
        
        # Frame contenedor principal dentro del canvas
        lista_frame = tk.Frame(canvas, bg="#E8E8E8")
        
        # Crear la ventana dentro del canvas con un ancho específico
        canvas.create_window((0, 0), window=lista_frame, anchor="nw", width=ANCHO_VENTANA-45)
        
        # Frame para los videos completados
        self.frame_completadas = tk.Frame(lista_frame, bg="#E8E8E8")
        self.frame_completadas.pack(fill=tk.X, expand=True)
        
        # Configurar el scrolling - simplemente actualiza la región de scroll, no la altura
        def configurar_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        lista_frame.bind("<Configure>", configurar_scroll)
    
    def _crear_boton_ubicacion(self):
        """Crea un botón que abre la carpeta de descargas (ahora fuera del scrollbar)."""
        frame_boton = tk.Frame(self.ventana)
        # Aún más reducido el padding vertical
        frame_boton.pack(fill=tk.X, pady=1)
        
        # Etiqueta con la ruta actual de la carpeta de descargas - compactada
        self.etiqueta_ruta_carpeta = tk.StringVar()
        self._actualizar_etiqueta_carpeta(obtener_directorio_descargas())
        
        tk.Label(frame_boton, textvariable=self.etiqueta_ruta_carpeta, 
                 anchor="center", font=("Helvetica", 8)).pack(fill=tk.X, pady=0)
        
        try:
            # Cargar ícono para el botón
            ruta_icono = os.path.join("assets", "carpeta-abierta.png")
            img_original = Image.open(ruta_icono)
            img_redimensionada = img_original.resize((20, 20), Image.LANCZOS)
            self.icono_carpeta = ImageTk.PhotoImage(img_redimensionada)
            
            # Crear botón con ícono y texto (centrado)
            btn_ubicacion = tk.Button(
                frame_boton,
                text="Abrir carpeta de descargas",
                image=self.icono_carpeta,
                compound=tk.LEFT,
                command=self._abrir_carpeta_descargas,
                padx=10,
                pady=5,
                cursor="hand2"
            )
            btn_ubicacion.pack(side=tk.TOP, anchor=tk.CENTER)
            
        except Exception as e:
            # Si hay error al cargar ícono, crear botón sin ícono
            print(f"Error al cargar ícono de carpeta: {str(e)}")
            btn_ubicacion = tk.Button(
                frame_boton,
                text="Abrir carpeta de descargas",
                command=self._abrir_carpeta_descargas,
                padx=10,
                pady=5
            )
            btn_ubicacion.pack(side=tk.TOP, anchor=tk.CENTER)
    
    def _abrir_carpeta_descargas(self):
        """Abre la carpeta de descargas en el explorador de archivos."""
        directorio = obtener_directorio_descargas()
        
        try:
            if platform.system() == 'Windows':
                os.startfile(directorio)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', directorio])
            else:  # Linux y otros
                subprocess.call(['xdg-open', directorio])
        except Exception as e:
            print(f"Error al abrir carpeta de descargas: {str(e)}")
            messagebox.showerror(
                "Error", 
                f"No se pudo abrir la carpeta de descargas.\n{str(e)}"
            )
    
    def actualizar_contador_videos(self, num_videos):
        """Actualiza el contador de videos descargados en la interfaz."""
        self.etiqueta_videos.set(f"Videos descargados - {num_videos}")
    
    def _actualizar_etiqueta_carpeta(self, ruta):
        """Actualiza la etiqueta que muestra la carpeta de destino."""
        if hasattr(self, 'etiqueta_ruta_carpeta'):
            # Acortar la ruta si es muy larga
            ruta_mostrada = ruta
            if len(ruta) > 50:
                ruta_mostrada = "..." + ruta[-47:]
            self.etiqueta_ruta_carpeta.set(f"Carpeta de destino: {ruta_mostrada}")
    
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
