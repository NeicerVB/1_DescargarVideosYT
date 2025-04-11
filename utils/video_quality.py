"""
Utilidades para obtener y manejar la calidad de video.
"""

import yt_dlp

def obtener_formatos_disponibles(url):
    """
    Obtiene los formatos disponibles para un video.
    
    Args:
        url: URL del video
    
    Returns:
        Lista de diccionarios con información de cada formato disponible
    """
    print(f"Obteniendo formatos disponibles para: {url}")
    
    # Opciones para YoutubeDL
    opciones = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        # Obtener la información del video
        with yt_dlp.YoutubeDL(opciones) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if not info:
                print("No se pudo obtener información del video")
                return []
            
            print(f"Título del video: {info.get('title', 'Desconocido')}")
            
            # Formatos disponibles
            formatos_disponibles = []
            
            # Opciones predefinidas comunes
            formatos_predefinidos = [
                {'format_id': 'best', 'calidad': 'Mejor calidad disponible', 'extension': 'auto', 'tamaño_aprox': 'Variable'},
                {'format_id': 'bestvideo+bestaudio', 'calidad': 'Mejor video + mejor audio', 'extension': 'auto', 'tamaño_aprox': 'Variable'},
            ]
            
            # Añadir formatos predefinidos siempre
            formatos_disponibles.extend(formatos_predefinidos)
            
            # Formatos específicos del video
            if 'formats' in info and info['formats']:
                # Filtro para formatos con audio y video
                for formato in info['formats']:
                    vcodec = formato.get('vcodec', '')
                    acodec = formato.get('acodec', '')
                    
                    # Ignorar formatos sin video o solo audio
                    if vcodec == 'none' or vcodec == '':
                        continue
                    
                    # Crear un ID de formato que combine video+audio si es necesario
                    format_id = formato.get('format_id', '')
                    if acodec == 'none':
                        format_id = f"{format_id}+bestaudio"
                    
                    # Obtener información de calidad
                    height = formato.get('height', 0)
                    width = formato.get('width', 0)
                    fps = formato.get('fps', 0)
                    extension = formato.get('ext', 'desconocida')
                    
                    # Construir descripción de la calidad
                    if height and width:
                        calidad = f"{width}x{height}"
                        if fps:
                            calidad += f" @{int(fps)}fps"
                    else:
                        calidad = formato.get('format_note', 'Calidad desconocida')
                    
                    # Añadir info de codec
                    if vcodec and vcodec != 'none':
                        codec_info = f" [{vcodec.split('.')[0]}"
                        if acodec and acodec != 'none':
                            codec_info += f"/{acodec.split('.')[0]}"
                        elif format_id.endswith('+bestaudio'):
                            codec_info += "/mejor audio"
                        codec_info += "]"
                        calidad += codec_info
                    
                    # Estimar tamaño
                    filesize = formato.get('filesize') or formato.get('filesize_approx')
                    if filesize:
                        if filesize > 1024 * 1024 * 1024:
                            tamaño = f"{filesize / (1024 * 1024 * 1024):.2f} GB"
                        else:
                            tamaño = f"{filesize / (1024 * 1024):.2f} MB"
                    else:
                        tamaño = "Tamaño desconocido"
                    
                    # Guardar información del formato
                    formatos_disponibles.append({
                        'format_id': format_id,
                        'calidad': calidad,
                        'extension': extension,
                        'tamaño_aprox': tamaño,
                        'height': height or 0  # Para ordenar
                    })
            
            # Eliminar duplicados y ordenar
            formatos_filtrados = []
            formatos_ids_vistos = set()
            
            # Primero incluir las opciones predefinidas
            for formato in formatos_disponibles:
                if formato['format_id'] in ['best', 'bestvideo+bestaudio']:
                    formatos_filtrados.append(formato)
                    formatos_ids_vistos.add(formato['format_id'])
            
            # Luego ordenar el resto por altura (calidad) descendente
            otros_formatos = [f for f in formatos_disponibles 
                             if f['format_id'] not in formatos_ids_vistos]
            otros_formatos.sort(key=lambda x: x.get('height', 0), reverse=True)
            
            # Agregar los formatos ordenados, evitando duplicados de resoluciones
            resoluciones_vistas = set()
            for formato in otros_formatos:
                height = formato.get('height', 0)
                # Si es una resolución que ya tenemos, ignorar
                if height in resoluciones_vistas and height != 0:
                    continue
                
                formatos_filtrados.append(formato)
                resoluciones_vistas.add(height)
            
            print(f"Se encontraron {len(formatos_filtrados)} formatos únicos")
            return formatos_filtrados
            
    except Exception as e:
        print(f"Error al obtener formatos: {str(e)}")
        raise
