"""
Detección y normalización de fuentes de video (embeds).

StreamFlix reproduce dos tipos de contenido:
  - El catálogo base: películas de dominio público en Internet Archive.
  - Películas añadidas por el usuario desde el formulario, que pueden venir de
    YouTube, Vimeo, un .mp4 directo, Google Drive o un embed genérico (Doodstream).

Cada fuente se reproduce distinto:
  - .mp4 / Drive  -> etiqueta <video> nativa del navegador (sin anuncios).
  - YouTube/Vimeo/Doodstream/Archive -> <iframe> con la URL de embed.

Este módulo recibe una URL cualquiera y devuelve cómo reproducirla.
"""

import re


def detectar(url: str) -> dict:
    """
    Analiza una URL y devuelve un dict:
        { "tipo": "video"|"iframe", "src": "<url lista para reproducir>" }

    - tipo "video"  -> usar <video src=...> (archivo directo).
    - tipo "iframe" -> usar <iframe src=...> (plataforma embebida).
    """
    if not url:
        return {"tipo": "iframe", "src": ""}

    u = url.strip()

    # --- YouTube ---
    yt = _id_youtube(u)
    if yt:
        return {"tipo": "iframe", "src": f"https://www.youtube.com/embed/{yt}"}

    # --- Vimeo ---
    vimeo = re.search(r"vimeo\.com/(?:video/)?(\d+)", u)
    if vimeo:
        return {"tipo": "iframe", "src": f"https://player.vimeo.com/video/{vimeo.group(1)}"}

    # --- Google Drive ---  (lo servimos como iframe /preview, que es lo estable)
    drive = re.search(r"drive\.google\.com/file/d/([^/]+)", u)
    if drive:
        return {"tipo": "iframe", "src": f"https://drive.google.com/file/d/{drive.group(1)}/preview"}

    # --- Internet Archive ---
    if "archive.org" in u:
        # Si ya es /embed/ lo dejamos; si es /details/ lo convertimos.
        if "/details/" in u:
            ident = u.split("/details/")[-1].split("/")[0]
            return {"tipo": "iframe", "src": f"https://archive.org/embed/{ident}"}
        return {"tipo": "iframe", "src": u}

    # --- Archivo de video directo (.mp4, .webm, .ogg/.ogv, .m4v) ---
    if re.search(r"\.(mp4|webm|ogv|ogg|m4v)(\?.*)?$", u, re.IGNORECASE):
        return {"tipo": "video", "src": u}

    # --- Doodstream y cualquier otro: iframe genérico ---
    #     (dood.* suele usar /e/ para el embed; si dan /d/ lo adaptamos)
    dood = re.search(r"(dood\.[a-z]+|dooood\.[a-z]+|do[a-z]*stream\.[a-z]+)/[de]/([a-z0-9]+)", u, re.IGNORECASE)
    if dood:
        dominio = dood.group(1)
        code = dood.group(2)
        return {"tipo": "iframe", "src": f"https://{dominio}/e/{code}"}

    # Fallback: tratar la URL tal cual como iframe.
    return {"tipo": "iframe", "src": u}


def _id_youtube(url: str):
    """Extrae el ID de video de las distintas formas de URL de YouTube."""
    patrones = [
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"youtube\.com/watch\?v=([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
        r"youtube\.com/shorts/([A-Za-z0-9_-]{11})",
    ]
    for p in patrones:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None
