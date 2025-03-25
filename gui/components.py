"""
Componentes reutilizables de la interfaz gráfica.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

class DescargarItem:
    """
    Representa un elemento visual de una descarga en la lista.
    
    Attributes:
        frame: Frame contenedor del item
        nombre_var: Variable de texto para el nombre
        progreso: Barra de progreso (solo en descargas activas)
        info_var: Variable de texto para información adicional
    """
    
    def __init__(self, frame_padre: tk.Frame, url: str, nombre: Optional[str] = None, es_descarga_activa: bool = True):
        """
        Inicializa un nuevo elemento de descarga.
        
        Args:
            frame_padre: Frame donde se añadirá este elemento
            url: URL del video (puede estar vacía si se proporciona nombre)
            nombre: Nombre del video a mostrar (opcional)
            es_descarga_activa: Si es una descarga en curso o un elemento del historial
        """
        self.url = url
        self.frame = tk.Frame(frame_padre)
        self.frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Label para el nombre (ahora con mayor ancho para los videos descargados)
        nombre_texto = f"Descargando: {url[:30]}..." if nombre is None else nombre
        self.nombre_var = tk.StringVar(value=nombre_texto)
        
        # El ancho varía según si es activo o completado
        nombre_ancho = 25 if es_descarga_activa else 40
        
        self.nombre_label = tk.Label(self.frame, textvariable=self.nombre_var, 
                                    anchor="w", width=nombre_ancho)
        self.nombre_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Barra de progreso (solo para descargas activas)
        self.progreso = None
        self.info_label = None
        self.info_var = None
        
        if es_descarga_activa:
            self.progreso = ttk.Progressbar(self.frame, orient="horizontal", length=150, mode="determinate")
            self.progreso.pack(side=tk.LEFT, padx=5)
            
            # Label para mostrar la velocidad y porcentaje
            self.info_var = tk.StringVar(value="0% - 0.00 MB/s")
            self.info_label = tk.Label(self.frame, textvariable=self.info_var, width=15, anchor="w")
            self.info_label.pack(side=tk.LEFT, padx=5)
        else:
            # Para videos ya descargados, mostrar un indicador de completado más compacto
            self.info_var = tk.StringVar(value="✓ Completado")
            self.info_label = tk.Label(self.frame, textvariable=self.info_var, width=12, 
                                      anchor="w", foreground="green")
            self.info_label.pack(side=tk.LEFT, padx=5)
    
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
    
    def completado(self, nombre_video: str) -> None:
        """
        Actualiza el elemento para mostrar que la descarga ha finalizado.
        
        Args:
            nombre_video: Nombre del video descargado
        """
        # Actualizar la interfaz para mostrar que se completó la descarga
        self.nombre_var.set(nombre_video)
        
        # Ampliar el ancho de la etiqueta de nombre para mostrar más del título
        self.nombre_label.config(width=40)
        
        # Ocultar la barra de progreso si existe
        if self.progreso:
            self.progreso.pack_forget()
            self.progreso = None
        
        # Actualizar la etiqueta de información con un texto más compacto
        self.info_var.set("✓ Completado")
        
        # Ajustar el ancho de la etiqueta de información para que sea más compacta
        self.info_label.config(width=12, foreground="green")
