import os
import yt_dlp

def descargar_video(url):
    carpeta_descargas = "downloads"
    if not os.path.exists(carpeta_descargas):
        os.makedirs(carpeta_descargas)

    opciones = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(carpeta_descargas, '%(title)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=True)
        ruta_guardado = os.path.join(carpeta_descargas, f"{info['title']}.{info['ext']}")
    
    return ruta_guardado
