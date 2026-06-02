"""
Generación de datos FICTICIOS de usuarios y calificaciones (ratings).

El PDF pide explícitamente trabajar con "datos ficticios". Aquí simulamos una base
de usuarios con gustos coherentes: cada usuario tiene un perfil de afinidad por
ciertas características (terror, comedia, etc.) y calificamos las películas que "vio"
en función de cuánto encajan con su perfil, más algo de ruido aleatorio para que
los datos no sean perfectos (como en la realidad).

La calificación va de 1 a 5 estrellas. Un valor 0 significa "no visto".
"""

import random

from .catalogo import PELICULAS, CARACTERISTICAS

# Semilla fija: así los datos son reproducibles entre ejecuciones y el profesor
# obtiene siempre los mismos resultados al revisar.
SEMILLA = 42

# Arquetipos de usuario: cada uno tiene pesos de afinidad por característica.
# Esto hace que las recomendaciones sean explicables ("le gusta el terror").
ARQUETIPOS = {
    "Fan del terror clásico":   {"terror": 3.0, "suspenso": 2.0, "mudo": 1.5, "clasico_pre1940": 1.0},
    "Amante de la comedia":     {"comedia": 3.0, "romance": 1.5, "drama": 0.5},
    "Cinéfilo de cine negro":   {"cine_negro": 3.0, "suspenso": 2.0, "drama": 1.5},
    "Aficionado al cine mudo":  {"mudo": 3.0, "clasico_pre1940": 2.5, "drama": 1.0, "comedia": 1.0},
    "Fan de ciencia ficción":   {"ciencia_ficcion": 3.0, "accion": 1.5, "terror": 1.0},
    "Espectador generalista":   {"drama": 1.5, "comedia": 1.5, "romance": 1.5, "accion": 1.0},
}


def _afinidad(perfil: dict, pelicula: dict) -> float:
    """Producto punto entre el perfil del usuario y las características de la peli."""
    return sum(peso * pelicula["caracteristicas"][carac]
               for carac, peso in perfil.items()
               if carac in CARACTERISTICAS)


def _afinidad_a_estrellas(valor: float, valor_max: float) -> int:
    """Normaliza la afinidad a una escala de 1 a 5 estrellas."""
    if valor_max <= 0:
        return 3
    normal = valor / valor_max  # 0..1
    estrellas = 1 + round(normal * 4)
    return max(1, min(5, estrellas))


def generar_usuarios(n_usuarios: int = 60, prob_visto: float = 0.55):
    """
    Genera una base de `n_usuarios` usuarios ficticios.

    Devuelve:
        usuarios: lista de dicts con id, nombre, arquetipo y perfil de afinidad.
        ratings:  dict {usuario_id: {pelicula_id: estrellas}}.

    `prob_visto` controla qué proporción del catálogo ha visto cada usuario
    (deja huecos a propósito: eso es lo que el recomendador debe predecir).
    """
    rng = random.Random(SEMILLA)
    nombres_arquetipos = list(ARQUETIPOS.keys())

    usuarios = []
    ratings = {}

    for uid in range(1, n_usuarios + 1):
        arquetipo = nombres_arquetipos[(uid - 1) % len(nombres_arquetipos)]
        perfil = ARQUETIPOS[arquetipo]

        # Afinidad máxima teórica para normalizar las estrellas de este usuario.
        afinidades = [_afinidad(perfil, p) for p in PELICULAS]
        max_af = max(afinidades) if afinidades else 1.0

        usuarios.append({
            "id": uid,
            "nombre": f"{arquetipo} #{(uid - 1) // len(nombres_arquetipos) + 1}",
            "arquetipo": arquetipo,
            "perfil": perfil,
        })

        vistos = {}
        for peli in PELICULAS:
            if rng.random() < prob_visto:
                base = _afinidad(perfil, peli)
                # Ruido: +/- 1 estrella para que no sea determinista.
                ruido = rng.choice([-1, 0, 0, 1])
                estrellas = _afinidad_a_estrellas(base, max_af) + ruido
                vistos[peli["id"]] = max(1, min(5, estrellas))
        # Garantiza que cada usuario tenga al menos 4 películas calificadas.
        if len(vistos) < 4:
            for peli in rng.sample(PELICULAS, 4):
                base = _afinidad(perfil, peli)
                vistos[peli["id"]] = _afinidad_a_estrellas(base, max_af)
        ratings[uid] = vistos

    return usuarios, ratings


# Base de datos en memoria, generada una sola vez al importar el módulo.
USUARIOS, RATINGS = generar_usuarios()
USUARIOS_POR_ID = {u["id"]: u for u in USUARIOS}


def popularidad():
    """
    Calcula el ranking de popularidad (sistema ACTUAL de StreamFlix).

    Devuelve lista de (pelicula_id, rating_promedio, num_votos) ordenada por
    promedio. Sirve de línea base para comparar contra el sistema personalizado.
    """
    acumulado = {}
    for vistos in RATINGS.values():
        for pid, estrellas in vistos.items():
            suma, n = acumulado.get(pid, (0, 0))
            acumulado[pid] = (suma + estrellas, n + 1)
    ranking = [(pid, suma / n, n) for pid, (suma, n) in acumulado.items()]
    ranking.sort(key=lambda x: x[1], reverse=True)
    return ranking
