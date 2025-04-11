"""
Panel de entrada de URL para la interfaz gráfica.
"""

import os
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from gui.utils.tooltip import crear_tooltip
from utils.config import obtener_directorio_descargas, obtener_calidad_video, guardar_calidad_video
from tkinter import filedialog, messagebox, Toplevel
from utils.config import guardar_configuracion
from utils.video_quality import obtener_formatos_disponibles

class InputPanel:
    """
    Panel con campo de entrada de URL y botones de acción.
    """
    
    def __init__(self, parent):
        """
        Inicializa el panel de entrada.
        
        Args:
            parent: Widget padre donde se colocará este panel
        """
        self.parent = parent
        self.download_callback = None
        self.calidad_seleccionada = obtener_calidad_video()
        self._crear_panel()
    
    def _crear_panel(self):
        """Crea el panel de entrada con sus widgets."""
        frame_entrada = tk.Frame(self.parent)
        frame_entrada.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(frame_entrada, text="URL del video:").pack(side=tk.LEFT, padx=(0, 5))
        # Reducimos el ancho de la entrada para dar espacio a los botones
        self.entrada_url = tk.Entry(frame_entrada, width=35)
        self.entrada_url.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Contenedor para los botones
        frame_botones = tk.Frame(frame_entrada)
        frame_botones.pack(side=tk.RIGHT)
        
        # Crear botón para seleccionar carpeta
        self._crear_boton_seleccionar_carpeta(frame_botones)
        
        # Crear botón para seleccionar calidad
        self._crear_boton_seleccionar_calidad(frame_botones)
        
        # Botón de descarga
        boton_descargar = tk.Button(
            frame_botones, 
            text="Descargar", 
            command=self._on_download_click
        )
        boton_descargar.pack(side=tk.LEFT, padx=5)
    
    def _crear_boton_seleccionar_carpeta(self, frame_padre):
        """
        Crea el botón para seleccionar carpeta de destino.
        
        Args:
            frame_padre: Frame donde se colocará el botón
        """
        try:
            # Cargar ícono para el botón
            ruta_icono = os.path.join("assets", "carpeta-abierta.png")
            img_original = Image.open(ruta_icono)
            img_redimensionada = img_original.resize((20, 20), Image.LANCZOS)
            self.icono_carpeta_destino = ImageTk.PhotoImage(img_redimensionada)
            
            boton_seleccionar_carpeta = tk.Button(
                frame_padre,
                image=self.icono_carpeta_destino,
                command=self._seleccionar_carpeta_destino,
                relief=tk.FLAT,
                bd=1,
                highlightthickness=0,
                cursor="hand2"
            )
            boton_seleccionar_carpeta.pack(side=tk.LEFT, padx=2)
            
            # Añadir tooltip
            crear_tooltip(boton_seleccionar_carpeta, "Seleccionar carpeta de destino")
        except Exception as e:
            print(f"Error al crear botón de carpeta destino: {str(e)}")
    
    def _crear_boton_seleccionar_calidad(self, frame_padre):
        """
        Crea el botón para seleccionar la calidad del video.
        
        Args:
            frame_padre: Frame donde se colocará el botón
        """
        try:
            # Cargar ícono para el botón (actualizado a calidad.png)
            ruta_icono = os.path.join("assets", "calidad.png")
            try:
                img_original = Image.open(ruta_icono)
                img_redimensionada = img_original.resize((20, 20), Image.LANCZOS)
                self.icono_calidad = ImageTk.PhotoImage(img_redimensionada)
                
                boton_seleccionar_calidad = tk.Button(
                    frame_padre,
                    image=self.icono_calidad,
                    command=self._seleccionar_calidad_video,
                    relief=tk.FLAT,
                    bd=1,
                    highlightthickness=0,
                    cursor="hand2"
                )
            except FileNotFoundError:
                # Si no encuentra el ícono, usar texto en su lugar
                boton_seleccionar_calidad = tk.Button(
                    frame_padre,
                    text="HD",
                    font=("Helvetica", 8, "bold"),
                    width=2,
                    command=self._seleccionar_calidad_video,
                    relief=tk.FLAT,
                    bd=1,
                    highlightthickness=0,
                    cursor="hand2"
                )
            
            boton_seleccionar_calidad.pack(side=tk.LEFT, padx=2)
            
            # Añadir tooltip
            crear_tooltip(boton_seleccionar_calidad, "Seleccionar calidad del video")
        except Exception as e:
            print(f"Error al crear botón de selección de calidad: {str(e)}")
    
    def _seleccionar_calidad_video(self):
        """Abre una ventana para seleccionar la calidad del video."""
        url = self.entrada_url.get().strip()
        if not url:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una URL válida para ver las calidades disponibles.")
            return
        
        # Crear ventana emergente
        ventana_calidad = Toplevel(self.parent)
        ventana_calidad.title("Seleccionar calidad de video")
        ventana_calidad.geometry("500x480")
        ventana_calidad.resizable(False, False)
        ventana_calidad.transient(self.parent)
        ventana_calidad.grab_set()
        
        # Crear elementos de la interfaz
        frame_principal = tk.Frame(ventana_calidad)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        tk.Label(
            frame_principal, 
            text="Selecciona la calidad del video:", 
            font=("Helvetica", 11, "bold")
        ).pack(pady=(10, 5))
        
        # Mostrar la URL del video
        url_cortada = url if len(url) < 60 else url[:57] + "..."
        tk.Label(
            frame_principal, 
            text=f"URL: {url_cortada}", 
            font=("Helvetica", 9), 
            fg="#555555"
        ).pack(pady=(0, 15))
        
        # Mostrar mensaje de carga y frame de progreso
        frame_carga = tk.Frame(frame_principal)
        frame_carga.pack(fill=tk.X, pady=20)
        
        mensaje_carga = tk.Label(
            frame_carga, 
            text="Obteniendo calidades disponibles...", 
            font=("Helvetica", 10)
        )
        mensaje_carga.pack(side=tk.LEFT, padx=10)
        
        # Barra de progreso indefinida
        progreso = ttk.Progressbar(
            frame_carga, 
            orient="horizontal", 
            mode="indeterminate", 
            length=200
        )
        progreso.pack(side=tk.RIGHT, padx=10, fill=tk.X, expand=True)
        progreso.start()
        
        # Frame que contendrá la lista de formatos (inicialmente vacío)
        frame_contenido = tk.Frame(frame_principal)
        frame_contenido.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Frame para los botones
        frame_botones = tk.Frame(ventana_calidad)
        frame_botones.pack(fill=tk.X, pady=10, padx=10)
        
        # Botones iniciales (solo cancelar disponible durante la carga)
        boton_cancelar = tk.Button(
            frame_botones, 
            text="Cancelar", 
            width=10, 
            command=ventana_calidad.destroy
        )
        boton_cancelar.pack(side=tk.RIGHT, padx=5)
        
        boton_aceptar = tk.Button(
            frame_botones, 
            text="Aceptar", 
            width=10, 
            state=tk.DISABLED
        )
        boton_aceptar.pack(side=tk.RIGHT, padx=5)
        
        # Variable para almacenar el formato seleccionado
        formato_seleccionado = {'id': None, 'calidad': None}
        
        # Actualizar la ventana para mostrar la carga
        ventana_calidad.update()
        
        def mostrar_formatos(formatos):
            """Muestra los formatos en la ventana una vez cargados"""
            # Eliminar elementos de carga
            frame_carga.destroy()
            
            if not formatos:
                tk.Label(
                    frame_contenido, 
                    text="No se encontraron formatos disponibles para este video.",
                    font=("Helvetica", 10), 
                    fg="red"
                ).pack(pady=20)
                boton_aceptar.config(state=tk.DISABLED)
                return
            
            # Frame para tabla con scrollbar
            frame_tabla = tk.Frame(frame_contenido)
            frame_tabla.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Crear scrollbar
            scrollbar = tk.Scrollbar(frame_tabla)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Crear tabla para mostrar formatos
            tree = ttk.Treeview(
                frame_tabla, 
                columns=("calidad", "extension", "tam_aprox"), 
                show="headings", 
                selectmode="browse", 
                yscrollcommand=scrollbar.set,
                height=12
            )
            tree.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=tree.yview)
            
            # Configurar encabezados
            tree.heading("calidad", text="Calidad")
            tree.heading("extension", text="Formato")
            tree.heading("tam_aprox", text="Tamaño aprox.")
            
            # Configurar anchos de columna
            tree.column("calidad", width=250)
            tree.column("extension", width=80)
            tree.column("tam_aprox", width=130)
            
            # Insertar formatos en la tabla
            for formato in formatos:
                item_id = tree.insert("", "end", values=(
                    formato["calidad"],
                    formato["extension"],
                    formato["tamaño_aprox"]
                ), tags=(formato["format_id"],))
                
                # Seleccionar el formato actual por defecto
                if formato["format_id"] == self.calidad_seleccionada:
                    tree.selection_set(item_id)
                    tree.focus(item_id)
                    tree.see(item_id)  # Asegurar que el item seleccionado sea visible
                    formato_seleccionado['id'] = formato["format_id"]
                    formato_seleccionado['calidad'] = formato["calidad"]
                    boton_aceptar.config(state=tk.NORMAL)
            
            # Mostrar la calidad actual
            frame_calidad_actual = tk.Frame(frame_contenido)
            frame_calidad_actual.pack(fill=tk.X, pady=10)
            
            mensaje_calidad = tk.StringVar(
                value=f"Calidad actual: {self.calidad_seleccionada or 'Mejor calidad (por defecto)'}"
            )
            tk.Label(
                frame_calidad_actual, 
                textvariable=mensaje_calidad,
                font=("Helvetica", 9),
                anchor="w"
            ).pack(side=tk.LEFT)
            
            # Opción para usar la mejor calidad
            boton_mejor_calidad = tk.Button(
                frame_calidad_actual, 
                text="Usar mejor calidad", 
                command=lambda: seleccionar_mejor_calidad(mensaje_calidad)
            )
            boton_mejor_calidad.pack(side=tk.RIGHT)
            
            # Funciones para manejar la selección
            def al_seleccionar(event):
                """Maneja el evento cuando se selecciona un formato"""
                seleccionados = tree.selection()
                if seleccionados:
                    item_id = seleccionados[0]
                    format_id = tree.item(item_id, "tags")[0]
                    calidad_text = tree.item(item_id, "values")[0]
                    
                    formato_seleccionado['id'] = format_id
                    formato_seleccionado['calidad'] = calidad_text
                    boton_aceptar.config(state=tk.NORMAL)
            
            def seleccionar_mejor_calidad(mensaje_var):
                """Selecciona la mejor calidad disponible"""
                formato_seleccionado['id'] = ""
                formato_seleccionado['calidad'] = "Mejor calidad (por defecto)"
                mensaje_var.set("Calidad actual: Mejor calidad (por defecto)")
                
                # Desseleccionar todo en el árbol
                for item in tree.selection():
                    tree.selection_remove(item)
                
                boton_aceptar.config(state=tk.NORMAL)
            
            # Vincular evento de selección
            tree.bind("<<TreeviewSelect>>", al_seleccionar)
            
            # Configurar el botón de aceptar
            def aceptar_seleccion():
                """Guarda la selección y cierra la ventana"""
                self.calidad_seleccionada = formato_seleccionado['id']
                guardar_calidad_video(formato_seleccionado['id'])
                
                # Mostrar mensaje de confirmación
                if formato_seleccionado['id']:
                    mensaje = f"Se ha seleccionado la calidad: {formato_seleccionado['calidad']}"
                else:
                    mensaje = "Se ha seleccionado la mejor calidad (por defecto)"
                
                messagebox.showinfo("Calidad seleccionada", mensaje)
                ventana_calidad.destroy()
            
            boton_aceptar.config(command=aceptar_seleccion)
            
            # Si no hay selección inicial y el formato actual no está en la lista
            if not tree.selection() and self.calidad_seleccionada:
                boton_aceptar.config(state=tk.DISABLED)
        
        # Función para obtener formatos en un hilo separado
        def obtener_formatos_en_hilo():
            try:
                print("Iniciando obtención de formatos...")
                formatos = obtener_formatos_disponibles(url)
                # Programar actualización en el hilo principal
                ventana_calidad.after(0, lambda: mostrar_formatos(formatos))
            except Exception:
                print(f"Error al obtener formatos: {str(Exception)}")
                # Manejar error en el hilo principal
                ventana_calidad.after(0, lambda: mostrar_error(str(Exception)))
        
        def mostrar_error(mensaje):
            frame_carga.destroy()
            tk.Label(
                frame_contenido, 
                text=f"Error al obtener formatos: {mensaje}",
                font=("Helvetica", 10), 
                fg="red",
                wraplength=400
            ).pack(pady=20)
            boton_aceptar.config(state=tk.DISABLED)
        
        # Ejecutar la obtención de formatos en un hilo separado
        hilo = threading.Thread(target=obtener_formatos_en_hilo)
        hilo.daemon = True
        hilo.start()
    
    def _seleccionar_carpeta_destino(self):
        """Abre un diálogo para seleccionar la carpeta de destino de las descargas."""
        # Obtener directorio actual
        directorio_actual = obtener_directorio_descargas()
        
        carpeta_seleccionada = filedialog.askdirectory(
            title="Seleccionar carpeta de destino",
            initialdir=directorio_actual
        )
        
        if carpeta_seleccionada:
            self._procesar_seleccion_carpeta(carpeta_seleccionada)
    
    def _procesar_seleccion_carpeta(self, carpeta_seleccionada):
        """
        Procesa la carpeta seleccionada por el usuario.
        
        Args:
            carpeta_seleccionada: Ruta de la carpeta seleccionada
        """
        # Actualizar la configuración
        if guardar_configuracion(carpeta_seleccionada):
            # Mostrar mensaje informativo
            messagebox.showinfo(
                "Carpeta de destino", 
                f"Las descargas se guardarán en:\n{carpeta_seleccionada}"
            )
        else:
            messagebox.showerror(
                "Error", 
                "No se pudo establecer la carpeta de destino.\nVerifique que tiene permisos de escritura."
            )
    
    def _on_download_click(self):
        """Maneja el evento de clic en el botón de descarga."""
        url = self.entrada_url.get()
        if url and self.download_callback:
            # Limpiar el campo de entrada para la siguiente URL
            self.entrada_url.delete(0, tk.END)
            # Llamar al callback con la URL y la calidad seleccionada
            self.download_callback(url, self.calidad_seleccionada)
    
    def set_download_callback(self, callback):
        """
        Establece el callback que se llamará cuando se haga clic en el botón de descarga.
        
        Args:
            callback: Función a llamar con la URL y la calidad como argumento
        """
        self.download_callback = callback
