# Reels · Casa Alberto (Tudela)

Tres reels verticales (1080×1920, 30 fps, con música y efectos) para Instagram/TikTok:

| Vídeo | Duración | Idea |
|---|---|---|
| `output/casa-alberto-reel1-ia.mp4` | 23 s | "Le pregunté a la IA dónde comer en Tudela": simulación de un chat de IA que recomienda Casa Alberto |
| `output/casa-alberto-reel2-cachopo.mp4` | 24 s | "Esto no es un filete… es un CACHOPO": anatomía por capas, ¡crunch!, corte con queso fundido, paletilla y costillares |
| `output/casa-alberto-reel3-tudela.mp4` | 29 s | "6 curiosidades de Tudela": 802, Puerta del Juicio, Bajada del Ángel, verdura, Bardenas… y la 6ª: Casa Alberto en el mapa |

Todos terminan con la misma tarjeta final: logo, C/ Muro 27 · Tudela y 📞 948 82 19 12.

## Cómo están hechos

Cada reel es una página HTML/SVG animada (`src/`) que se renderiza fotograma a fotograma
con Playwright y se codifica con ffmpeg. La banda sonora (`soundtrack.py`) se sintetiza por
código, así que no tiene derechos de autor.

- `assets/common.js` – utilidades de animación, logo vectorial y tarjeta final compartida.
- `assets/common.css` – colores de marca, tipografías (Google Fonts, licencia OFL).
- `render.mjs` – exportador a MP4.
- `soundtrack.py` – música (chill / trap / upbeat) y efectos (whoosh, pop, crunch, ding…).

## Volver a generar / editar

Requiere Node + Playwright (Chromium), Python 3 con numpy y ffmpeg.

```bash
cd reels/casa-alberto
node render.mjs src/reel2-cachopo.html output/casa-alberto-reel2-cachopo.mp4
```

Para ver fotogramas sueltos mientras editas:

```bash
node render.mjs src/reel2-cachopo.html stills/ --stills 2,9,14
```

Los textos (dirección, teléfono, platos, curiosidades) están directamente en cada `src/*.html`.
