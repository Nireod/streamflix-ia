"""
Filtrado colaborativo basado en usuarios (user-based collaborative filtering).

IMPLEMENTADO DESDE CERO (sin librerías de ML). Es el corazón del sistema:

Idea: "a un usuario le gustarán las películas que les gustaron a OTROS usuarios
parecidos a él". Pasos:

  1. Medir cuánto se parecen dos usuarios comparando las películas que AMBOS
     calificaron, usando la SIMILITUD DEL COSENO.
  2. Para una película que el usuario objetivo no ha visto, predecir su rating
     como el promedio de los ratings de los usuarios similares, ponderado por
     cuánto se parecen.
  3. Recomendar las películas no vistas con mayor rating predicho.

Aquí también se usa RECURSIVIDAD en dos puntos pedidos por el curso:
  - `producto_punto_recursivo` y `suma_recursiva`: cálculos sobre listas.
  - `recomendaciones_en_cadena`: explora recursivamente "vecinos de vecinos"
    para descubrir películas más allá del círculo inmediato del usuario.
"""

import math

from .datos import RATINGS, USUARIOS_POR_ID
from .catalogo import PELICULAS_POR_ID


# ---------------------------------------------------------------------------
# Utilidades recursivas (requisito del curso: funciones recursivas)
# ---------------------------------------------------------------------------

def suma_recursiva(valores):
    """Suma los elementos de una lista de forma recursiva."""
    if not valores:
        return 0.0
    return valores[0] + suma_recursiva(valores[1:])


def producto_punto_recursivo(a, b):
    """Producto punto de dos vectores (listas) de igual longitud, recursivo."""
    if not a or not b:
        return 0.0
    return a[0] * b[0] + producto_punto_recursivo(a[1:], b[1:])


# ---------------------------------------------------------------------------
# Similitud entre usuarios
# ---------------------------------------------------------------------------

def similitud_coseno(ratings_a: dict, ratings_b: dict) -> float:
    """
    Similitud del coseno entre dos usuarios.

    Solo se consideran las películas que AMBOS calificaron (intersección).
    Devuelve un valor entre 0 (nada parecidos) y 1 (idénticos gustos).
    """
    comunes = set(ratings_a) & set(ratings_b)
    if not comunes:
        return 0.0

    # Vectores alineados sobre las películas en común.
    vec_a = [ratings_a[pid] for pid in comunes]
    vec_b = [ratings_b[pid] for pid in comunes]

    numerador = producto_punto_recursivo(vec_a, vec_b)
    norma_a = math.sqrt(producto_punto_recursivo(vec_a, vec_a))
    norma_b = math.sqrt(producto_punto_recursivo(vec_b, vec_b))

    if norma_a == 0 or norma_b == 0:
        return 0.0
    return numerador / (norma_a * norma_b)


def usuarios_similares(usuario_id: int, k: int = 10):
    """
    Devuelve los `k` usuarios más parecidos al usuario dado.

    Lista de tuplas (otro_usuario_id, similitud) ordenada de mayor a menor.
    """
    objetivo = RATINGS.get(usuario_id, {})
    similitudes = []
    for otro_id, otros_ratings in RATINGS.items():
        if otro_id == usuario_id:
            continue
        sim = similitud_coseno(objetivo, otros_ratings)
        if sim > 0:
            similitudes.append((otro_id, sim))
    similitudes.sort(key=lambda x: x[1], reverse=True)
    return similitudes[:k]


# ---------------------------------------------------------------------------
# Predicción y recomendación
# ---------------------------------------------------------------------------

def predecir_rating(usuario_id: int, pelicula_id: int, k: int = 10) -> float:
    """
    Predice qué calificación le daría el usuario a una película no vista,
    como promedio ponderado por similitud de los vecinos que sí la vieron.
    """
    vecinos = usuarios_similares(usuario_id, k)
    numerador = 0.0
    denominador = 0.0
    for vecino_id, sim in vecinos:
        rating_vecino = RATINGS[vecino_id].get(pelicula_id)
        if rating_vecino is not None:
            numerador += sim * rating_vecino
            denominador += sim
    if denominador == 0:
        return 0.0
    return numerador / denominador


def recomendar(usuario_id: int, n: int = 10, k: int = 10):
    """
    Genera las `n` mejores recomendaciones para un usuario (filtrado colaborativo).

    Devuelve lista de dicts: {pelicula, rating_predicho, motivo}.
    Solo recomienda películas que el usuario NO ha visto todavía.
    """
    vistos = set(RATINGS.get(usuario_id, {}))
    vecinos = usuarios_similares(usuario_id, k)

    candidatas = []
    for pid in PELICULAS_POR_ID:
        if pid in vistos:
            continue
        prediccion = predecir_rating(usuario_id, pid, k)
        if prediccion > 0:
            candidatas.append((pid, prediccion))

    candidatas.sort(key=lambda x: x[1], reverse=True)

    resultado = []
    for pid, pred in candidatas[:n]:
        resultado.append({
            "pelicula": PELICULAS_POR_ID[pid],
            "rating_predicho": round(pred, 2),
            "motivo": _explicar(usuario_id, pid, vecinos),
        })
    return resultado


def _explicar(usuario_id: int, pelicula_id: int, vecinos) -> str:
    """Genera una explicación legible de por qué se recomienda la película."""
    cuantos = sum(1 for vid, _ in vecinos if pelicula_id in RATINGS[vid])
    if cuantos == 0:
        return "Sugerida por tu perfil de gustos."
    return f"Porque a {cuantos} usuarios con gustos parecidos también les gustó."


# ---------------------------------------------------------------------------
# Recorrido recursivo de la "red" de usuarios (vecinos de vecinos)
# ---------------------------------------------------------------------------

def recomendaciones_en_cadena(usuario_id: int, profundidad: int = 2,
                              k: int = 5, _visitados=None, _acumulado=None):
    """
    Explora RECURSIVAMENTE la red de usuarios similares hasta cierta
    `profundidad`: vecinos del usuario, luego vecinos de esos vecinos, etc.,
    acumulando las películas bien calificadas que el usuario no ha visto.

    Esto demuestra el uso de recursividad para recorrer una estructura de datos
    (un grafo de similitud) y enriquecer las recomendaciones con descubrimientos
    "lejanos" que el filtrado directo no alcanzaría.

    Devuelve un dict {pelicula_id: puntaje_acumulado}.
    """
    if _visitados is None:
        _visitados = set()
    if _acumulado is None:
        _acumulado = {}

    # Caso base: sin profundidad restante o usuario ya visitado.
    if profundidad <= 0 or usuario_id in _visitados:
        return _acumulado

    _visitados.add(usuario_id)
    vistos_objetivo = set(RATINGS.get(usuario_id, {}))

    for vecino_id, sim in usuarios_similares(usuario_id, k):
        # Acumula las pelis que le gustaron al vecino y el objetivo no ha visto.
        for pid, estrellas in RATINGS[vecino_id].items():
            if pid not in vistos_objetivo and estrellas >= 4:
                # El aporte decae con la profundidad y pondera por similitud.
                aporte = sim * estrellas * (1.0 / profundidad)
                _acumulado[pid] = _acumulado.get(pid, 0.0) + aporte
        # Paso recursivo: explora los vecinos de este vecino.
        recomendaciones_en_cadena(vecino_id, profundidad - 1, k,
                                   _visitados, _acumulado)

    return _acumulado
