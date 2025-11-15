# Sora2Pro Video Generator

This project provides a minimal local interface to generate videos using the Sora 2 Pro model via CometAPI.

## Overview

The interface allows you to:
- Enter a text prompt.
- Upload an image as the initial frame (must be exactly 1792×1024 px).
- Select video duration (15 or 25 seconds).
- Generate a video using the **sora-2-pro** model with a fixed resolution of **1792×1024**.
- Download or view the resulting MP4 file with no watermark.

All requests are sent through a lightweight Flask backend to CometAPI, which wraps OpenAI’s Sora API. Your API key is stored locally and never exposed to the browser.

## Prerequisites

- Python 3.10 or later.
- A CometAPI key with access to **sora-2-pro**.

## Installation and usage

1. Clone or download this repository.
2. Copy your CometAPI key into a `.env` file or export it as the environment variable `COMET_API_KEY`.
3. Run the startup script to set up the environment and launch the server:

```
scripts\start_server.bat
```

4. Open your web browser and navigate to `http://localhost:5000`.
5. Enter your prompt, choose a 1792×1024 image, select 15 s or 25 s, and click **Generate Video**. Wait while your video is generated and then view or download it.

## Project structure

- `frontend/index.html` – Minimalist web interface.
- `backend/app.py` – Flask server handling CometAPI calls.
- `backend/requirements.txt` – Python dependencies.
- `scripts/start_server.bat` – Windows script to set up and run the server.

---

# Generador de videos con Sora 2 Pro

Este proyecto ofrece una interfaz local mínima para generar videos mediante el modelo **Sora 2 Pro** a través de CometAPI.

## Resumen

La interfaz permite:
- Escribir un prompt de texto.
- Subir una imagen como fotograma inicial (debe medir exactamente **1792×1024 px**).
- Seleccionar la duración del video (**15 o 25 segundos**).
- Generar un video usando el modelo **sora-2-pro** con resolución fija **1792×1024**.
- Descargar o ver el archivo MP4 resultante **sin marca de agua**.

Todas las peticiones se envían a CometAPI mediante un backend ligero en Flask. Tu clave API se guarda localmente y nunca se expone al navegador.

## Requisitos

- Python 3.10 o superior.
- Una clave de CometAPI con acceso al modelo **sora-2-pro**.

## Instalación y uso

1. Clona o descarga este repositorio.
2. Copia tu clave de CometAPI en un archivo `.env` o expórtala como variable de entorno `COMET_API_KEY`.
3. Ejecuta el script de inicio para crear el entorno y lanzar el servidor:

```
scripts\start_server.bat
```

4. Abre tu navegador y visita `http://localhost:5000`.
5. Introduce tu prompt, elige una imagen 1792×1024, selecciona 15 s o 25 s y haz clic en **Generar video**. Espera mientras se genera el video y, a continuación, descárgalo o reprodúcelo.

## Estructura

- `frontend/index.html` – Interfaz web.
- `backend/app.py` – Servidor Flask para CometAPI.
- `backend/requirements.txt` – Dependencias de Python.
- `scripts/start_server.bat` – Script de inicio para Windows.
