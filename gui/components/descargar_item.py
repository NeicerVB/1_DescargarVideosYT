"""
Componente que representa un elemento de descarga en la interfaz gráfica.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os
import platform
import subprocess

class DescargarItem:
    """
    Representa un elemento de descarga en la interfaz gráfica.
    """
    
    # Colores para la interfaz
    COLOR_TITULO_ACTIVO = "#000000"  # Negro para descargas activas
    COLOR_TITULO_COMPLETADO = "#0066cc"  # Azul para descargas completadas
    COLOR_FONDO_HOVER = "#f0f0ff"  # Color de fondo al pasar el mouse
    
    def __init__(self, parent, url, nombre="", es_descarga_activa=True, 
                 ruta_archivo=None, tamano_archivo="", fecha_descarga=None):
        """
        Inicializa un nuevo elemento de descarga.
        
        Args:
            parent: Widget padre donde se colocará este elemento
            url: URL del video
            nombre: Nombre del video
            es_descarga_activa: True si la descarga está activa, False si está completada
            ruta_archivo: Ruta del archivo descargado
            tamano_archivo: Tamaño del archivo descargado
            fecha_descarga: Timestamp de cuando se completó la descarga
        """
        self.parent = parent
        self.url = url
        self.nombre = nombre if nombre else url
        self.es_descarga_activa = es_descarga_activa
        self.ruta_archivo = ruta_archivo
        self.tamano_archivo = tamano_archivo
        self.fecha_descarga = fecha_descarga
        
        # Crear widgets
        self._crear_widgets()
        
        # Si es una descarga completada, configurar para abrir el archivo
        if not self.es_descarga_activa and self.ruta_archivo:
            self._configurar_interactividad()
    
    def _crear_widgets(self):
        """Crea los widgets para mostrar la información de descarga."""
        # Frame principal
        self.frame = tk.Frame(self.parent, padx=5, pady=5, relief=tk.GROOVE, bd=1)
        self.frame.pack(fill=tk.X, padx=5, pady=3)
        
        # Info variable para mostrar el estado o info adicional
        self.info_var = tk.StringVar(value="Pendiente" if self.es_descarga_activa else "Completado")
        
        # Mostrar información diferente según si es activa o completada
        if self.es_descarga_activa:
            self._crear_widgets_descarga_activa()
        else:
            self._crear_widgets_descarga_completada()
    
    def _crear_widgets_descarga_activa(self):
        """Crea los widgets para una descarga activa."""
        # Título/URL con color negro
        titulo_texto = self._truncar_texto(self.nombre if self.nombre else self.url, 50)
        self.titulo_label = tk.Label(
            self.frame, 
            text=titulo_texto, 
            anchor="w", 
            font=("Helvetica", 9, "bold"), 
            fg=self.COLOR_TITULO_ACTIVO,
            wraplength=350
        )
        self.titulo_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Barra de progreso
        self.progreso = ttk.Progressbar(self.frame, orient="horizontal", length=350, mode="determinate")
        self.progreso.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=2)
        
        # Etiqueta de información (estado, velocidad, etc.)
        info_label = tk.Label(self.frame, textvariable=self.info_var, anchor="w", font=("Helvetica", 8))
        info_label.grid(row=2, column=0, sticky="w", padx=5)
        
        # Fecha/hora
        fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
        fecha_label = tk.Label(self.frame, text=f"Iniciado: {fecha_hora}", anchor="e", font=("Helvetica", 8))
        fecha_label.grid(row=2, column=1, sticky="e", padx=5)
        
        # Configurar grid
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
    
    def _crear_widgets_descarga_completada(self):
        """Crea los widgets para una descarga completada."""
        # Nombre del video con color azul
        self.titulo_label = tk.Label(
            self.frame, 
            text=self._truncar_texto(self.nombre, 50), 
            anchor="w", 
            font=("Helvetica", 9, "bold"), 
            fg=self.COLOR_TITULO_COMPLETADO,
            cursor="hand2",  # Cursor de mano para indicar que es clickeable
            wraplength=350
        )
        self.titulo_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=2)
        
        # Ruta y tamaño
        if self.ruta_archivo:
            ruta_texto = self._truncar_texto(f"Ruta: {self.ruta_archivo}", 60)
            ruta_label = tk.Label(self.frame, text=ruta_texto, anchor="w", font=("Helvetica", 8))
            ruta_label.grid(row=1, column=0, sticky="w", padx=5)
        
        if self.tamano_archivo:
            tamano_label = tk.Label(self.frame, text=f"Tamaño: {self.tamano_archivo}", 
                                  anchor="e", font=("Helvetica", 8))
            tamano_label.grid(row=1, column=1, sticky="e", padx=5)
        
        # Fecha/hora de descarga
        if self.fecha_descarga:
            # Convertir el timestamp a formato de fecha legible
            fecha_hora = datetime.fromtimestamp(self.fecha_descarga).strftime("%d/%m/%Y %H:%M")
        else:
            # Usar la fecha actual solo si no tenemos fecha guardada
            fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
            
        fecha_label = tk.Label(self.frame, text=f"Completado: {fecha_hora}", 
                             anchor="e", font=("Helvetica", 8))
        fecha_label.grid(row=2, column=1, sticky="e", padx=5)
        
        # Estado
        estado_label = tk.Label(self.frame, textvariable=self.info_var, 
                              anchor="w", font=("Helvetica", 8))
        estado_label.grid(row=2, column=0, sticky="w", padx=5)
    
    def _configurar_interactividad(self):
        """Configura la interactividad para elementos completados."""
        # Cambiar cursor al pasar sobre el elemento
        self.frame.config(cursor="hand2")
        
        # Eventos para el frame completo
        self.frame.bind("<Button-1>", self._abrir_video)
        self.frame.bind("<Enter>", self._on_enter)
        self.frame.bind("<Leave>", self._on_leave)
        
        # Eventos para el título
        self.titulo_label.bind("<Button-1>", self._abrir_video)
        self.titulo_label.bind("<Enter>", self._on_enter)
        self.titulo_label.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Cambia el color de fondo al entrar con el mouse."""
        self.frame.config(background=self.COLOR_FONDO_HOVER)
        for widget in self.frame.winfo_children():
            widget.config(background=self.COLOR_FONDO_HOVER)
    
    def _on_leave(self, event):
        """Restaura el color de fondo al salir con el mouse."""
        bg_color = self.parent.cget("background")
        self.frame.config(background=bg_color)
        for widget in self.frame.winfo_children():
            widget.config(background=bg_color)
    
    def actualizar(self, porcentaje, velocidad=0):
        """
        Actualiza el progreso y la velocidad de descarga.
        """
        if hasattr(self, 'progreso'):
            self.progreso['value'] = porcentaje
            
            # Actualizar etiqueta de información
            if velocidad > 0:
                self.info_var.set(f"{porcentaje:.1f}% - {velocidad:.2f} MB/s")
            else:
                self.info_var.set(f"{porcentaje:.1f}%")
    
    def completado(self, nombre, ruta_archivo, tamano_archivo="", fecha_descarga=None):
        """
        Marca la descarga como completada y actualiza la información.
        
        Args:
            nombre: Nombre del video descargado
            ruta_archivo: Ruta donde se guardó el archivo
            tamano_archivo: Tamaño del archivo descargado
            fecha_descarga: Timestamp de cuando se completó la descarga
        """
        self.nombre = nombre
        self.ruta_archivo = ruta_archivo
        self.tamano_archivo = tamano_archivo
        self.fecha_descarga = fecha_descarga
        self.es_descarga_activa = False
        self.info_var.set("Completado")
        
        # Si existe, actualizar la barra de progreso al 100%
        if hasattr(self, 'progreso'):
            self.progreso['value'] = 100
        
        # Destruir widgets existentes y recrear como completados
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        self._crear_widgets_descarga_completada()
        self._configurar_interactividad()
    
    def _abrir_video(self, event=None):
        """Abre el video descargado utilizando el sistema operativo predeterminado."""
        if not self.ruta_archivo:
            messagebox.showerror("Error", "Ruta de archivo no disponible")
            return
        
        if not os.path.exists(self.ruta_archivo):
            messagebox.showerror(
                "Error", 
                f"El archivo no existe en la ruta especificada:\n{self.ruta_archivo}"
            )
            return
            
        try:
            if platform.system() == "Windows":
                os.startfile(self.ruta_archivo)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", self.ruta_archivo], check=True)
            else:  # Linux y otros
                subprocess.run(["xdg-open", self.ruta_archivo], check=True)
                
            print(f"Archivo abierto correctamente: {self.ruta_archivo}")
        except Exception as e:
            mensaje_error = f"No se pudo abrir el archivo.\nError: {str(e)}"
            print(mensaje_error)
            messagebox.showerror("Error", mensaje_error)
    
    def _truncar_texto(self, texto, longitud_max):
        """
        Trunca el texto si excede la longitud máxima.
        """
        if len(texto) > longitud_max:
            return texto[:longitud_max - 3] + "..."
        return texto
