"""
Validación del modelo mediante VALIDACIÓN CRUZADA (k-fold cross-validation).

El PDF pide "métodos de validación del modelo (cross-validation)" y "su rendimiento
en la predicción". Aquí evaluamos:

  1. El filtrado colaborativo: ¿qué tan bien predice las calificaciones que ya
     conocemos? Métricas de regresión: MAE y RMSE.
  2. El árbol de decisión: ¿clasifica bien si una película "gusta" o no?
     Métricas de clasificación: precisión (accuracy).

Procedimiento k-fold:
  - Se toman todas las calificaciones conocidas (usuario, película, estrellas).
  - Se reparten en k bloques (folds).
  - En cada ronda: un fold se "oculta" (test) y el resto se usa para predecir.
  - Se promedian las métricas de las k rondas.

Todo implementado a mano, sin librerías de ML.
"""

import math
import random

from .datos import RATINGS
from .catalogo import PELICULAS_POR_ID, CARACTERISTICAS
from . import arbol as arbol_mod

SEMILLA = 7


def _todas_las_calificaciones():
    """Aplana RATINGS a una lista de (usuario_id, pelicula_id, estrellas)."""
    muestras = []
    for uid, vistos in RATINGS.items():
        for pid, estrellas in vistos.items():
            muestras.append((uid, pid, estrellas))
    return muestras


def _dividir_en_folds(muestras, k):
    """Reparte las muestras (barajadas) en k bloques de tamaño similar."""
    rng = random.Random(SEMILLA)
    barajadas = muestras[:]
    rng.shuffle(barajadas)
    folds = [[] for _ in range(k)]
    for i, m in enumerate(barajadas):
        folds[i % k].append(m)
    return folds


def _predecir_rating_con(ratings_entrenamiento, usuario_id, pelicula_id, k=10):
    """
    Versión del filtrado colaborativo que usa SOLO los ratings de entrenamiento
    (para no hacer trampa viendo el dato que estamos evaluando).
    """
    objetivo = ratings_entrenamiento.get(usuario_id, {})
    # Similitudes contra todos los demás usuarios usando los ratings de train.
    similitudes = []
    for otro_id, otros in ratings_entrenamiento.items():
        if otro_id == usuario_id:
            continue
        comunes = set(objetivo) & set(otros)
        if not comunes:
            continue
        va = [objetivo[p] for p in comunes]
        vb = [otros[p] for p in comunes]
        num = sum(x * y for x, y in zip(va, vb))
        na = math.sqrt(sum(x * x for x in va))
        nb = math.sqrt(sum(y * y for y in vb))
        if na and nb:
            similitudes.append((otro_id, num / (na * nb)))
    similitudes.sort(key=lambda x: x[1], reverse=True)

    numerador = denominador = 0.0
    for vid, sim in similitudes[:k]:
        r = ratings_entrenamiento[vid].get(pelicula_id)
        if r is not None:
            numerador += sim * r
            denominador += sim
    if denominador == 0:
        return None
    return numerador / denominador


def evaluar_filtrado_colaborativo(k_folds=5, k_vecinos=10):
    """
    Valida el filtrado colaborativo con k-fold y devuelve MAE y RMSE promedio.
    MAE  = error absoluto medio.
    RMSE = raíz del error cuadrático medio.
    """
    muestras = _todas_las_calificaciones()
    folds = _dividir_en_folds(muestras, k_folds)

    maes, rmses = [], []
    for i in range(k_folds):
        test = folds[i]
        train = [m for j, f in enumerate(folds) if j != i for m in f]

        # Reconstruye la matriz de ratings solo con train.
        ratings_train = {}
        for uid, pid, est in train:
            ratings_train.setdefault(uid, {})[pid] = est

        errores = []
        for uid, pid, real in test:
            pred = _predecir_rating_con(ratings_train, uid, pid, k_vecinos)
            if pred is not None:
                errores.append(abs(pred - real))
        if errores:
            mae = sum(errores) / len(errores)
            rmse = math.sqrt(sum(e * e for e in errores) / len(errores))
            maes.append(mae)
            rmses.append(rmse)

    return {
        "k_folds": k_folds,
        "mae": round(sum(maes) / len(maes), 4) if maes else None,
        "rmse": round(sum(rmses) / len(rmses), 4) if rmses else None,
    }


def evaluar_arbol_decision(k_folds=5):
    """
    Valida el árbol de decisión con k-fold y devuelve la precisión promedio
    (accuracy) de la clasificación GUSTA / NO_GUSTA.
    """
    muestras = _todas_las_calificaciones()
    folds = _dividir_en_folds(muestras, k_folds)

    precisiones = []
    for i in range(k_folds):
        test = folds[i]
        train = [m for j, f in enumerate(folds) if j != i for m in f]

        # Ejemplos de entrenamiento por usuario.
        ejemplos_por_usuario = {}
        for uid, pid, est in train:
            etq = "GUSTA" if est >= arbol_mod.UMBRAL_GUSTA else "NO_GUSTA"
            ejemplos_por_usuario.setdefault(uid, []).append(
                (PELICULAS_POR_ID[pid]["caracteristicas"], etq))

        # Entrena un árbol por usuario.
        arboles = {
            uid: arbol_mod.construir_arbol(ej, list(CARACTERISTICAS))
            for uid, ej in ejemplos_por_usuario.items()
        }

        aciertos = total = 0
        for uid, pid, est in test:
            if uid not in arboles:
                continue
            real = "GUSTA" if est >= arbol_mod.UMBRAL_GUSTA else "NO_GUSTA"
            pred = arbol_mod.predecir(arboles[uid], PELICULAS_POR_ID[pid]["caracteristicas"])
            total += 1
            if pred == real:
                aciertos += 1
        if total:
            precisiones.append(aciertos / total)

    return {
        "k_folds": k_folds,
        "precision": round(sum(precisiones) / len(precisiones), 4) if precisiones else None,
    }


def reporte_completo():
    """Devuelve un resumen de todas las métricas de validación."""
    return {
        "filtrado_colaborativo": evaluar_filtrado_colaborativo(),
        "arbol_decision": evaluar_arbol_decision(),
    }
