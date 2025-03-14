import tkinter as tk
from tkinter import messagebox
from downloader import descargar_video

def iniciar_descarga(ventana, entrada_url, mensaje):
    url = entrada_url.get()
    if url:
        mensaje.set("Descargando...")
        ventana.update_idletasks()
        try:
            ruta_guardado = descargar_video(url)
            mensaje.set("¡Descarga completada!")
            messagebox.showinfo("Éxito", f"Video guardado en:\n{ruta_guardado}")
        except Exception as e:
            mensaje.set("Error en la descarga")
            messagebox.showerror("Error", f"No se pudo descargar el video.\n{str(e)}")
    else:
        messagebox.showwarning("Advertencia", "Por favor, ingresa una URL válida.")


def iniciar_gui():

    # Función para centrar la ventana
    def centrar_ventana(ancho, alto):
        pantalla_ancho = ventana.winfo_screenwidth()
        pantalla_alto = ventana.winfo_screenheight()
        x = (pantalla_ancho // 2) - (ancho // 2)
        y = (pantalla_alto // 2) - (alto // 2)
        ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    # Crear ventana
    ventana = tk.Tk()
    ventana.title("Descargador de YouTube")

    # Agregar icono
    ventana.iconbitmap('assets/ico-youtube.ico')

    # Definir tamaño de la ventana
    ANCHO_VENTANA = 500
    ALTO_VENTANA = 300
    centrar_ventana(ANCHO_VENTANA, ALTO_VENTANA)

    # Campo de entrada
    tk.Label(ventana, text="URL del video:").pack(pady=5)
    entrada_url = tk.Entry(ventana, width=50)
    entrada_url.pack(pady=5)

    # Botón de descarga
    boton_descargar = tk.Button(
        ventana, text="Descargar", 
        command=lambda: iniciar_descarga(ventana, entrada_url, mensaje)
    )
    boton_descargar.pack(pady=10)

    # Mensaje de estado
    mensaje = tk.StringVar()
    tk.Label(ventana, textvariable=mensaje).pack()

    ventana.mainloop()