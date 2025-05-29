# ⏬ Descargador de Videos de YouTube

<div align="center">
   <img src="https://cdn-icons-png.flaticon.com/128/2504/2504965.png" alt="YouTube Downloader Screenshot" width="100">
   <p><em>Interfaz del Descargador de Videos de YouTube</em></p>
</div>

Este proyecto es una herramienta de automatización hecha en Python para descargar videos de YouTube mediante una interfaz gráfica creada con Tkinter. Se utiliza la librería `yt-dlp` para gestionar las descargas, garantizando compatibilidad con diferentes formatos y calidades de video y audio.

## 🎯Objetivo del Proyecto

Ofrecer una interfaz fácil de usar para descargar por medio de una URL de YouTube video o audio.

## 🔍Características

- Descarga videos de YouTube con la mejor calidad disponible.
- Interfaz sencilla y fácil de usar basada en Tkinter.
- Seleccionar ubicación de carpeta de descarga (por defecto `downloads`).
- Ventana centrada en la pantalla al iniciarse.

## 📥Instalación

1. Clona este repositorio:
   ```sh
   git clone https://github.com/NeicerVB/1_DescargarVideosYT.git
   cd 1_DescargarVideosYT
   ```

2. Crea la carpeta donde se almacenarán las descargas:
   ```sh
   mkdir downloads
   ```

3. Instala las dependencias necesarias:
   ```sh
   pip install -r requirements.txt
   ```

4. Ejecuta la aplicación:
   ```shv
   python main.py
   ```

## 🤝 Contribuir

Si deseas contribuir al desarrollo de este proyecto, sigue estos pasos:

1. Realiza un fork del repositorio.
2. Crea una rama nueva con tu nombre y fecha.
   ```sh
   git checkout -b neicer-2025-10-01
   ```
3. Realiza los cambios y confírmalos.
   ```sh
   git commit -m "Agrega nueva funcionalidad"
   ```
4. Envía un pull request con una descripción clara de los cambios.

## 🚀 Futuras Mejoras
- Interrumpir la descarga en curso.
- Reanudar descargas interrumpidas.
- Permitir la descarga de listas de reproducción.
- Poder descargar múltiples videos a la vez.
- Desplegar el proyecto en alguna plataforma gratuita para que esté disponible en cualquier momento.

## Funciones completadas 03.1
1. Correpción del desplazamiento vertical en la lista de videos descargados.
2. Correpción de la fecha de descarga de los videos.
3. Selección de calidad de video antes de la descarga.

## Funciones completadas 03.2
1. Eliminar videos descargados.
2. Interrumpir y cancelar la descarga en curso.
3. Reanudar descargas interrumpidas.

## Arreglos de errores y mejoras de diseño 03.3
1. Cambio en las opciones de eliminar video descargado: Ahora solo hay dos opciones (Si - No).
2. La ventana de "Seleccionar calidad de video" ahora está centrada en la pantalla.