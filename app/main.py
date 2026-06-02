"""
API de StreamFlix (FastAPI).

Expone el motor de recomendación como una API REST y sirve el frontend estático
(la web estilo Netflix). Pensado para desplegarse en Render.

Endpoints principales:
    GET /api/usuarios                  -> lista de perfiles (usuarios ficticios)
    GET /api/catalogo                  -> todas las películas
    GET /api/pelicula/{id}             -> detalle + URL de reproducción (embed)
    GET /api/recomendaciones/{uid}     -> recomendaciones personalizadas
    GET /api/populares                 -> ranking del sistema ACTUAL (popularidad)
    GET /api/comparacion/{uid}         -> personalizado vs popular (para el informe)
    GET /api/metricas                  -> validación cruzada del modelo
    GET /api/arbol/{uid}               -> árbol de decisión del usuario (texto)
"""

import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .recommender import catalogo, datos, colaborativo, arbol, validacion

app = FastAPI(title="StreamFlix — Sistema de recomendación", version="1.0")

ESTATICOS = os.path.join(os.path.dirname(__file__), "static")

# Caché del reporte de métricas (la validación cruzada es algo costosa).
_metricas_cache = None


def _pelicula_publica(peli: dict) -> dict:
    """Versión de la película para enviar al frontend (sin el vector interno)."""
    return {
        "id": peli["id"],
        "titulo": peli["titulo"],
        "anio": peli["anio"],
        "director": peli["director"],
        "genero": peli["genero"],
        "sinopsis": peli["sinopsis"],
        "poster": peli["poster"],
        "embed": catalogo.url_embed(peli["id"]),
    }


@app.get("/api/usuarios")
def listar_usuarios():
    """Perfiles disponibles para elegir (como los perfiles de Netflix)."""
    return [
        {"id": u["id"], "nombre": u["nombre"], "arquetipo": u["arquetipo"]}
        for u in datos.USUARIOS
    ]


@app.get("/api/catalogo")
def obtener_catalogo():
    """Catálogo completo, agrupado por género para los carruseles."""
    pelis = [_pelicula_publica(p) for p in catalogo.PELICULAS]
    por_genero = {}
    for p in pelis:
        por_genero.setdefault(p["genero"], []).append(p)
    return {"peliculas": pelis, "por_genero": por_genero}


@app.get("/api/pelicula/{pelicula_id}")
def detalle_pelicula(pelicula_id: int):
    peli = catalogo.obtener_pelicula(pelicula_id)
    if not peli:
        raise HTTPException(status_code=404, detail="Película no encontrada")
    return _pelicula_publica(peli)


@app.get("/api/recomendaciones/{usuario_id}")
def recomendaciones(usuario_id: int, n: int = 10):
    """
    Recomendaciones personalizadas combinando filtrado colaborativo y árbol.
    Devuelve la lista colaborativa (con rating predicho y motivo) y, aparte,
    las que el árbol de decisión marca como afines.
    """
    if usuario_id not in datos.USUARIOS_POR_ID:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    colab = colaborativo.recomendar(usuario_id, n)
    arbol_recs, _ = arbol.recomendar_con_arbol(usuario_id, n)

    return {
        "usuario": datos.USUARIOS_POR_ID[usuario_id]["nombre"],
        "colaborativo": [
            {
                "pelicula": _pelicula_publica(r["pelicula"]),
                "rating_predicho": r["rating_predicho"],
                "motivo": r["motivo"],
            }
            for r in colab
        ],
        "arbol": [_pelicula_publica(p) for p in arbol_recs],
    }


@app.get("/api/populares")
def populares(n: int = 10):
    """Sistema ACTUAL de StreamFlix: ranking por popularidad (sin personalizar)."""
    ranking = datos.popularidad()[:n]
    return [
        {
            "pelicula": _pelicula_publica(catalogo.obtener_pelicula(pid)),
            "rating_promedio": round(prom, 2),
            "votos": n_votos,
        }
        for pid, prom, n_votos in ranking
    ]


@app.get("/api/comparacion/{usuario_id}")
def comparacion(usuario_id: int, n: int = 5):
    """
    Compara el sistema NUEVO (personalizado) contra el ACTUAL (popularidad)
    para un usuario. Sirve de evidencia para el informe.
    """
    if usuario_id not in datos.USUARIOS_POR_ID:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    personalizado = colaborativo.recomendar(usuario_id, n)
    popular = datos.popularidad()[:n]

    return {
        "usuario": datos.USUARIOS_POR_ID[usuario_id]["nombre"],
        "sistema_actual_popularidad": [
            {"titulo": catalogo.obtener_pelicula(pid)["titulo"],
             "rating_promedio": round(prom, 2)}
            for pid, prom, _ in popular
        ],
        "sistema_nuevo_personalizado": [
            {"titulo": r["pelicula"]["titulo"],
             "rating_predicho": r["rating_predicho"],
             "motivo": r["motivo"]}
            for r in personalizado
        ],
    }


@app.get("/api/metricas")
def metricas():
    """Resultados de la validación cruzada del modelo (se cachean)."""
    global _metricas_cache
    if _metricas_cache is None:
        _metricas_cache = validacion.reporte_completo()
    return _metricas_cache


@app.get("/api/arbol/{usuario_id}")
def arbol_usuario(usuario_id: int):
    """Devuelve el árbol de decisión aprendido para el usuario, como texto."""
    if usuario_id not in datos.USUARIOS_POR_ID:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    nodo = arbol.entrenar_para_usuario(usuario_id)
    return {
        "usuario": datos.USUARIOS_POR_ID[usuario_id]["nombre"],
        "arbol_texto": arbol.explicar_arbol(nodo),
    }


# --- Frontend estático (web estilo Netflix) ---
# Se monta al final para que las rutas /api/* tengan prioridad.

@app.get("/")
def raiz():
    return FileResponse(os.path.join(ESTATICOS, "index.html"))


app.mount("/", StaticFiles(directory=ESTATICOS, html=True), name="static")
