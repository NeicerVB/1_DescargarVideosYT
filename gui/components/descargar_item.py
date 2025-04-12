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
    COLOR_BOTON_ELIMINAR = "#ff4d4d"  # Rojo claro para botón eliminar
    COLOR_BOTON_CANCELAR = "#ff8c00"  # Naranja para botón cancelar
    COLOR_BOTON_HOVER = "#ff3333"  # Rojo más intenso para hover
    
    def __init__(self, parent, url, nombre="", es_descarga_activa=True, 
                 ruta_archivo=None, tamano_archivo="", fecha_descarga=None,
                 on_eliminar_callback=None, on_cancelar_callback=None, id_descarga=None):
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
            on_eliminar_callback: Función a llamar cuando se solicita eliminar el elemento
            on_cancelar_callback: Función a llamar cuando se solicita cancelar la descarga
            id_descarga: ID de la descarga para identificarla (proporcionado por DownloadManager)
        """
        self.parent = parent
        self.url = url
        self.nombre = nombre if nombre else url
        self.es_descarga_activa = es_descarga_activa
        self.ruta_archivo = ruta_archivo
        self.tamano_archivo = tamano_archivo
        self.fecha_descarga = fecha_descarga
        self.on_eliminar_callback = on_eliminar_callback
        self.on_cancelar_callback = on_cancelar_callback
        self.id_descarga = id_descarga  # Guardar el ID de descarga
        
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
        
        # Botón de cancelación
        if self.on_cancelar_callback:
            self._crear_boton_cancelar()
        
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
        
        # Botón eliminar
        if self.on_eliminar_callback:
            self._crear_boton_eliminar()
    
    def _crear_boton_eliminar(self):
        """Crea un botón para eliminar el video de la lista."""
        # Frame para el botón en la esquina superior derecha
        boton_frame = tk.Frame(self.frame)
        boton_frame.place(relx=1.0, y=0, anchor="ne")
        
        # Botón eliminar con estilo
        self.boton_eliminar = tk.Button(
            boton_frame, 
            text="✕", 
            font=("Helvetica", 8, "bold"),
            fg="white",
            bg=self.COLOR_BOTON_ELIMINAR,
            activebackground=self.COLOR_BOTON_HOVER,
            relief=tk.FLAT,
            width=2,
            height=1,
            command=self._confirmar_eliminar
        )
        self.boton_eliminar.pack(padx=1, pady=1)
        
        # Añadir tooltip (mensaje emergente)
        self._create_tooltip(self.boton_eliminar, "Eliminar de la lista")
    
    def _crear_boton_cancelar(self):
        """Crea un botón para cancelar la descarga en progreso."""
        # Frame para el botón en la esquina superior derecha
        boton_frame = tk.Frame(self.frame)
        boton_frame.place(relx=1.0, y=0, anchor="ne")
        
        # Botón cancelar con estilo
        self.boton_cancelar = tk.Button(
            boton_frame, 
            text="⏹", 
            font=("Helvetica", 9, "bold"),
            fg="white",
            bg=self.COLOR_BOTON_CANCELAR,
            activebackground=self.COLOR_BOTON_HOVER,
            relief=tk.FLAT,
            width=2,
            height=1,
            command=self._cancelar_descarga
        )
        self.boton_cancelar.pack(padx=1, pady=1)
        
        # Añadir tooltip (mensaje emergente)
        self._create_tooltip(self.boton_cancelar, "Cancelar descarga")
    
    def _create_tooltip(self, widget, text):
        """Crea un tooltip (mensaje emergente) para un widget."""
        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            
            # Crear una ventana emergente temporal
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            
            label = tk.Label(
                self.tooltip, text=text, bg="#FFFFDD", 
                relief=tk.SOLID, borderwidth=1,
                font=("Helvetica", 8), padx=2, pady=1
            )
            label.pack()
            
        def leave(event):
            if hasattr(self, "tooltip") and self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def _confirmar_eliminar(self):
        """Muestra un diálogo de confirmación antes de eliminar el video."""
        if not self.ruta_archivo:
            messagebox.showerror("Error", "Ruta de archivo no disponible")
            return
        
        # Verificar si el archivo físico existe
        archivo_existe = os.path.exists(self.ruta_archivo)
        
        if archivo_existe:
            # Preguntar si quiere eliminar también el archivo
            respuesta = messagebox.askyesnocancel(
                "Confirmar eliminación", 
                f"¿Desea eliminar '{self.nombre}' de la lista?\n\n"
                "Presione:\n"
                "- 'Sí' para eliminar de la lista y borrar el archivo del disco\n"
                "- 'No' para eliminar solo de la lista\n"
                "- 'Cancelar' para no hacer nada"
            )
            
            if respuesta is None:  # Cancelar
                return
                
            # Llamar al callback con la decisión del usuario
            if self.on_eliminar_callback:
                self.on_eliminar_callback(self.ruta_archivo, respuesta)
        else:
            # Si el archivo no existe, solo confirmar eliminar de la lista
            respuesta = messagebox.askyesno(
                "Confirmar eliminación", 
                f"¿Desea eliminar '{self.nombre}' de la lista?\n"
                "(El archivo no se encuentra en la ruta especificada)"
            )
            
            if respuesta:
                # Llamar al callback solo para eliminar del historial
                if self.on_eliminar_callback:
                    self.on_eliminar_callback(self.ruta_archivo, False)
    
    def _cancelar_descarga(self):
        """Inicia el proceso de cancelación de la descarga actual."""
        if not self.on_cancelar_callback or not self.id_descarga:
            return
            
        # Confirmar si el usuario realmente quiere cancelar
        respuesta = messagebox.askyesno(
            "Cancelar descarga", 
            "¿Está seguro que desea cancelar esta descarga?\n\n"
            "El proceso se detendrá inmediatamente."
        )
        
        if respuesta:
            # Desactivar botón de cancelar para evitar múltiples intentos
            if hasattr(self, 'boton_cancelar') and self.boton_cancelar:
                self.boton_cancelar.config(state=tk.DISABLED)
                
            # Mostrar que la descarga está en proceso de cancelación
            self.info_var.set("Cancelando...")
            
            # Llamar al callback de cancelación con el ID correcto
            self.on_cancelar_callback(self.id_descarga)
    
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
