"""
Funciones auxiliares para la interfaz gráfica.
"""

def centrar_ventana(ventana, ancho, alto):
    """
    Centra una ventana en la pantalla.
    
    Args:
        ventana: Ventana a centrar
        ancho: Ancho de la ventana
        alto: Alto de la ventana
    """
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
