"""
Controles para la gestión de la carpeta de descargas.
"""

import os
import platform
import subprocess
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox

from utils.config import obtener_directorio_descargas

class FolderControls:
    """
    Controles para la gestión de la carpeta de descargas.
    """
    
    def __init__(self, parent):
        """
        Inicializa los controles de carpeta.
        
        Args:
            parent: Widget padre donde se colocarán estos controles
        """
        self.parent = parent
        self._crear_controles()
    
    def _crear_controles(self):
        """Crea los controles de carpeta de descargas."""
        frame_boton = tk.Frame(self.parent)
        frame_boton.pack(fill=tk.X, pady=1)
        
        # Etiqueta con la ruta actual de la carpeta de descargas
        self.etiqueta_ruta_carpeta = tk.StringVar()
        self.actualizar_etiqueta_carpeta(obtener_directorio_descargas())
        
        tk.Label(frame_boton, textvariable=self.etiqueta_ruta_carpeta, 
                 anchor="center", font=("Helvetica", 8)).pack(fill=tk.X, pady=0)
        
        self._crear_boton_abrir_carpeta(frame_boton)
    
    def _crear_boton_abrir_carpeta(self, frame_padre):
        """
        Crea el botón para abrir la carpeta de descargas.
        
        Args:
            frame_padre: Frame donde se colocará el botón
        """
        try:
            # Cargar ícono para el botón
            ruta_icono = os.path.join("assets", "carpeta-abierta.png")
            img_original = Image.open(ruta_icono)
            img_redimensionada = img_original.resize((20, 20), Image.LANCZOS)
            self.icono_carpeta = ImageTk.PhotoImage(img_redimensionada)
            
            # Crear botón con ícono y texto
            btn_ubicacion = tk.Button(
                frame_padre,
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
                frame_padre,
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
    
    def actualizar_etiqueta_carpeta(self, ruta):
        """
        Actualiza la etiqueta que muestra la carpeta de destino.
        
        Args:
            ruta: Ruta de la carpeta a mostrar
        """
        if hasattr(self, 'etiqueta_ruta_carpeta'):
            # Acortar la ruta si es muy larga
            ruta_mostrada = ruta
            if len(ruta) > 50:
                ruta_mostrada = "..." + ruta[-47:]
            self.etiqueta_ruta_carpeta.set(f"Carpeta de destino: {ruta_mostrada}")
