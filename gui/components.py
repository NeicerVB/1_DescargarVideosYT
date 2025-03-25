"""
Componentes reutilizables de la interfaz gráfica.
"""

import os
import tkinter as tk
from tkinter import ttk
from typing import Optional
import platform
import subprocess
from PIL import Image, ImageTk

class DescargarItem:
    """
    Representa un elemento visual de una descarga en la lista.
    
    Attributes:
        frame: Frame contenedor del item
        nombre_var: Variable de texto para el nombre
        progreso: Barra de progreso (solo en descargas activas)
        info_var: Variable de texto para información adicional
    """
    
    def __init__(self, frame_padre: tk.Frame, url: str, nombre: Optional[str] = None, 
                 es_descarga_activa: bool = True, ruta_archivo: Optional[str] = None,
                 tamano_archivo: Optional[str] = None):
        """
        Inicializa un nuevo elemento de descarga.
        
        Args:
            frame_padre: Frame donde se añadirá este elemento
            url: URL del video (puede estar vacía si se proporciona nombre)
            nombre: Nombre del video a mostrar (opcional)
            es_descarga_activa: Si es una descarga en curso o un elemento del historial
            ruta_archivo: Ruta al archivo descargado (para videos completados)
            tamano_archivo: Tamaño del archivo formateado (para videos completados)
        """
        self.url = url
        self.ruta_archivo = ruta_archivo
        self.tamano_archivo = tamano_archivo
        
        # Usar el color de fondo del padre para mantener consistencia visual
        bg_color = frame_padre.cget("bg")
        
        # Añadir color de fondo al frame para una mejor visualización
        self.frame = tk.Frame(frame_padre, bg=bg_color)
        self.frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Para videos completados, añadir botón para abrir el archivo
        if not es_descarga_activa and ruta_archivo:
            self._agregar_boton_abrir()
        
        # Label para el nombre (ahora con mayor ancho para los videos descargados)
        nombre_texto = f"Descargando: {url[:30]}..." if nombre is None else nombre
        self.nombre_var = tk.StringVar(value=nombre_texto)
        
        # El ancho varía según si es activo o completado
        nombre_ancho = 25 if es_descarga_activa else 38
        
        # Adaptar el color de fondo de la etiqueta al del padre
        self.nombre_label = tk.Label(self.frame, textvariable=self.nombre_var, 
                                    anchor="w", width=nombre_ancho, bg=bg_color)
        self.nombre_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Si es un video completado, hacer que el nombre sea clickeable
        if not es_descarga_activa and ruta_archivo:
            self.nombre_label.config(cursor="hand2", foreground="blue")
            self.nombre_label.bind("<Button-1>", self._abrir_archivo)
            # Efecto de hover
            self.nombre_label.bind("<Enter>", lambda e: self.nombre_label.config(foreground="#0066cc"))
            self.nombre_label.bind("<Leave>", lambda e: self.nombre_label.config(foreground="blue"))
        
        # Barra de progreso (solo para descargas activas)
        self.progreso = None
        self.info_label = None
        self.info_var = None
        
        if es_descarga_activa:
            self.progreso = ttk.Progressbar(self.frame, orient="horizontal", length=150, mode="determinate")
            self.progreso.pack(side=tk.LEFT, padx=5)
            
            # Label para mostrar la velocidad y porcentaje (adaptada al fondo)
            self.info_var = tk.StringVar(value="0% - 0.00 MB/s")
            self.info_label = tk.Label(self.frame, textvariable=self.info_var, 
                                     width=15, anchor="w", bg=bg_color)
            self.info_label.pack(side=tk.LEFT, padx=5)
        else:
            # Para videos ya descargados, mostrar un indicador de completado con tamaño
            info_texto = f"✓ {tamano_archivo}" if tamano_archivo else "✓ Completado"
            self.info_var = tk.StringVar(value=info_texto)
            self.info_label = tk.Label(self.frame, textvariable=self.info_var, width=15, 
                                      anchor="w", foreground="green", bg=bg_color)
            self.info_label.pack(side=tk.LEFT, padx=5)
    
    def _agregar_boton_abrir(self):
        """Agrega un botón con ícono para abrir el archivo directamente."""
        try:
            # Cargar la imagen y redimensionarla
            ruta_icono = os.path.join("assets", "archivo.png")
            img_original = Image.open(ruta_icono)
            img_redimensionada = img_original.resize((16, 16), Image.LANCZOS)
            
            # Convertir a formato compatible con tkinter
            self.icono_btn = ImageTk.PhotoImage(img_redimensionada)
            
            # Crear botón con la imagen - cambiado a _abrir_archivo
            self.btn_abrir = tk.Button(
                self.frame, 
                image=self.icono_btn, 
                command=self._abrir_archivo,  # Cambio: ahora abre el archivo directamente
                relief=tk.FLAT,
                bd=0,
                highlightthickness=0,
                cursor="hand2"
            )
            self.btn_abrir.pack(side=tk.LEFT, padx=(2, 5))
            
            # Actualizar el tooltip para reflejar la funcionalidad
            self._crear_tooltip(self.btn_abrir, "Abrir archivo")
            
        except Exception as e:
            print(f"Error al cargar el ícono del botón: {str(e)}")
    
    def _crear_tooltip(self, widget, texto):
        """Crea un tooltip para un widget."""
        def mostrar_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            # Crear ventana emergente con estilo mejorado
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
    
    def _abrir_ubicacion(self, event=None):
        """Abre el explorador de archivos en la ubicación del archivo descargado."""
        if not self.ruta_archivo or not os.path.exists(self.ruta_archivo):
            print(f"No se puede encontrar la ubicación del archivo: {self.ruta_archivo}")
            return
            
        try:
            # Obtener el directorio que contiene el archivo
            directorio = os.path.dirname(self.ruta_archivo)
            
            # Abrir el explorador de archivos en la ubicación del archivo
            if platform.system() == 'Windows':
                os.startfile(directorio)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', directorio])
            else:  # Linux y otros
                subprocess.call(['xdg-open', directorio])
        except Exception as e:
            print(f"Error al abrir la ubicación del archivo: {str(e)}")
    
    def _abrir_archivo(self, event=None):
        """Abre el archivo descargado con la aplicación predeterminada."""
        if not self.ruta_archivo or not os.path.exists(self.ruta_archivo):
            print(f"No se puede abrir el archivo: {self.ruta_archivo}")
            return
            
        try:
            # Abrir el archivo con la aplicación predeterminada según el sistema operativo
            if platform.system() == 'Windows':
                os.startfile(self.ruta_archivo)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', self.ruta_archivo])
            else:  # Linux y otros
                subprocess.call(['xdg-open', self.ruta_archivo])
        except Exception as e:
            print(f"Error al abrir el archivo: {str(e)}")
    
    def actualizar(self, porcentaje: float, velocidad: float) -> None:
        """
        Actualiza el estado visual de la descarga.
        
        Args:
            porcentaje: Porcentaje de progreso (0-100)
            velocidad: Velocidad de descarga en MB/s
        """
        if self.progreso:
            self.progreso["value"] = porcentaje
            self.info_var.set(f"{porcentaje:.1f}% - {velocidad:.2f} MB/s")
    
    def completado(self, nombre_video: str, ruta_archivo: str = None, tamano_archivo: str = None) -> None:
        """
        Actualiza el elemento para mostrar que la descarga ha finalizado.
        
        Args:
            nombre_video: Nombre del video descargado
            ruta_archivo: Ruta al archivo descargado
            tamano_archivo: Tamaño del archivo formateado
        """
        # Guardar la ruta del archivo
        if ruta_archivo:
            self.ruta_archivo = ruta_archivo
        
        # Guardar el tamaño del archivo
        if tamano_archivo:
            self.tamano_archivo = tamano_archivo
        
        # Obtener el color de fondo del padre
        bg_color = self.frame.cget("bg")
        
        # Actualizar la interfaz para mostrar que se completó la descarga
        self.nombre_var.set(nombre_video)
        
        # Ampliar el ancho de la etiqueta de nombre para mostrar más del título
        self.nombre_label.config(width=38)
        
        # Hacer que el nombre sea clickeable
        self.nombre_label.config(cursor="hand2", foreground="blue", bg=bg_color)
        self.nombre_label.bind("<Button-1>", self._abrir_archivo)
        # Efecto de hover
        self.nombre_label.bind("<Enter>", lambda e: self.nombre_label.config(foreground="#0066cc"))
        self.nombre_label.bind("<Leave>", lambda e: self.nombre_label.config(foreground="blue"))
        
        # Agregar botón para abrir la ubicación del archivo
        self._agregar_boton_abrir()
        
        # Ocultar la barra de progreso si existe
        if self.progreso:
            self.progreso.pack_forget()
            self.progreso = None
        
        # Actualizar la etiqueta de información para incluir el tamaño
        info_texto = f"✓ {self.tamano_archivo}" if self.tamano_archivo else "✓ Completado"
        self.info_var.set(info_texto)
        
        # Ajustar el ancho de la etiqueta de información y mantener el color de fondo
        self.info_label.config(width=15, foreground="green", bg=bg_color)
