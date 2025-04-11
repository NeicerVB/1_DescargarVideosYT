"""
Implementación de tooltips para la interfaz gráfica.
"""

import tkinter as tk

def crear_tooltip(widget, texto):
    """
    Crea un tooltip para un widget.
    
    Args:
        widget: Widget al que se añadirá el tooltip
        texto: Texto que se mostrará en el tooltip
    """
    # Variable para almacenar la instancia del tooltip
    tooltip_window = None
    
    def mostrar_tooltip(event):
        nonlocal tooltip_window
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 25
        
        # Crear ventana emergente
        tooltip_window = tk.Toplevel(widget)
        tooltip_window.wm_overrideredirect(True)
        tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tooltip_window, text=texto, bg="#FFFFDD", 
                       relief=tk.SOLID, borderwidth=1, padx=5, pady=2)
        label.pack()
        
    def ocultar_tooltip(event):
        nonlocal tooltip_window
        if tooltip_window:
            tooltip_window.destroy()
            tooltip_window = None
            
    widget.bind("<Enter>", mostrar_tooltip)
    widget.bind("<Leave>", ocultar_tooltip)
