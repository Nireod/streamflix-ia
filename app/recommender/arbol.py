"""
Árbol de decisión IMPLEMENTADO DESDE CERO (algoritmo tipo ID3).

Objetivo (lo que pide el PDF): "aplicar algoritmos de árboles de decisión para
determinar qué películas recomendar a un usuario según sus características".

Cómo lo planteamos:
  - Para CADA usuario construimos un árbol personal.
  - Ejemplos de entrenamiento = las películas que el usuario YA calificó.
  - Atributos (features) = las características binarias de cada película
    (terror, comedia, mudo, etc.).
  - Etiqueta a predecir = ¿le gustó? (rating >= 4  ->  "GUSTA", si no "NO_GUSTA").
  - El árbol aprende qué características predicen que al usuario le guste una peli.
  - Luego, para una película no vista, recorremos el árbol y predecimos si la
    recomendamos.

El árbol se construye RECURSIVAMENTE eligiendo en cada nodo la característica con
mayor GANANCIA DE INFORMACIÓN (reducción de entropía), que es el criterio de ID3.
"""

import math

from .catalogo import CARACTERISTICAS, PELICULAS_POR_ID
from .datos import RATINGS

UMBRAL_GUSTA = 4  # rating >= 4 estrellas se considera "le gustó"


# ---------------------------------------------------------------------------
# Métricas de impureza
# ---------------------------------------------------------------------------

def entropia(etiquetas):
    """
    Entropía de Shannon de una lista de etiquetas ("GUSTA"/"NO_GUSTA").
    0 = grupo puro (todas iguales); 1 = máxima incertidumbre (mitad y mitad).
    """
    total = len(etiquetas)
    if total == 0:
        return 0.0
    h = 0.0
    for clase in set(etiquetas):
        p = etiquetas.count(clase) / total
        if p > 0:
            h -= p * math.log2(p)
    return h


def ganancia_informacion(ejemplos, caracteristica):
    """
    Ganancia de información al dividir `ejemplos` por una característica binaria.
    ejemplos = lista de tuplas (vector_caracteristicas, etiqueta).
    """
    etiquetas = [etq for _, etq in ejemplos]
    h_inicial = entropia(etiquetas)

    total = len(ejemplos)
    h_despues = 0.0
    for valor in (0, 1):
        subset = [etq for vec, etq in ejemplos if vec[caracteristica] == valor]
        if subset:
            h_despues += (len(subset) / total) * entropia(subset)

    return h_inicial - h_despues


# ---------------------------------------------------------------------------
# Construcción recursiva del árbol
# ---------------------------------------------------------------------------

class Nodo:
    """Nodo del árbol. Si es hoja tiene `prediccion`; si no, divide por `caracteristica`."""

    def __init__(self, caracteristica=None, hijos=None, prediccion=None, soporte=0):
        self.caracteristica = caracteristica   # característica por la que divide
        self.hijos = hijos or {}               # {0: Nodo, 1: Nodo}
        self.prediccion = prediccion           # "GUSTA"/"NO_GUSTA" si es hoja
        self.soporte = soporte                 # nº de ejemplos que llegaron aquí

    @property
    def es_hoja(self):
        return self.prediccion is not None


def _clase_mayoritaria(etiquetas):
    """Devuelve la etiqueta más frecuente (con desempate hacia NO_GUSTA)."""
    if not etiquetas:
        return "NO_GUSTA"
    return max(set(etiquetas), key=etiquetas.count)


def construir_arbol(ejemplos, caracteristicas_disponibles, profundidad=0, max_prof=6):
    """
    Construye el árbol de decisión de forma RECURSIVA (ID3).

    Casos base (hoja):
      - Todos los ejemplos tienen la misma etiqueta -> hoja con esa etiqueta.
      - No quedan características o se alcanzó la profundidad máxima -> hoja con
        la clase mayoritaria.
    Paso recursivo:
      - Elegir la característica de mayor ganancia de información, dividir los
        ejemplos por ella y construir un subárbol para cada valor (0 y 1).
    """
    etiquetas = [etq for _, etq in ejemplos]

    # --- Casos base ---
    if not etiquetas:
        return Nodo(prediccion="NO_GUSTA", soporte=0)
    if len(set(etiquetas)) == 1:
        return Nodo(prediccion=etiquetas[0], soporte=len(etiquetas))
    if not caracteristicas_disponibles or profundidad >= max_prof:
        return Nodo(prediccion=_clase_mayoritaria(etiquetas), soporte=len(etiquetas))

    # --- Elegir mejor característica ---
    mejor = max(caracteristicas_disponibles,
                key=lambda c: ganancia_informacion(ejemplos, c))

    # Si la mejor ganancia es nula, no vale la pena seguir dividiendo.
    if ganancia_informacion(ejemplos, mejor) <= 0:
        return Nodo(prediccion=_clase_mayoritaria(etiquetas), soporte=len(etiquetas))

    restantes = [c for c in caracteristicas_disponibles if c != mejor]
    hijos = {}
    for valor in (0, 1):
        subset = [(vec, etq) for vec, etq in ejemplos if vec[mejor] == valor]
        if subset:
            # Paso recursivo.
            hijos[valor] = construir_arbol(subset, restantes, profundidad + 1, max_prof)
        else:
            # Sin ejemplos para esta rama: hoja con la clase mayoritaria del padre.
            hijos[valor] = Nodo(prediccion=_clase_mayoritaria(etiquetas), soporte=0)

    return Nodo(caracteristica=mejor, hijos=hijos, soporte=len(etiquetas))


# ---------------------------------------------------------------------------
# Predicción (recorrido recursivo del árbol)
# ---------------------------------------------------------------------------

def predecir(nodo: Nodo, caracteristicas: dict) -> str:
    """Recorre el árbol RECURSIVAMENTE hasta una hoja y devuelve la predicción."""
    if nodo.es_hoja:
        return nodo.prediccion
    valor = caracteristicas[nodo.caracteristica]
    hijo = nodo.hijos.get(valor)
    if hijo is None:
        return "NO_GUSTA"
    return predecir(hijo, caracteristicas)


# ---------------------------------------------------------------------------
# Integración con el usuario
# ---------------------------------------------------------------------------

def _ejemplos_de_usuario(usuario_id: int):
    """Convierte las calificaciones de un usuario en ejemplos de entrenamiento."""
    ejemplos = []
    for pid, estrellas in RATINGS.get(usuario_id, {}).items():
        peli = PELICULAS_POR_ID[pid]
        etiqueta = "GUSTA" if estrellas >= UMBRAL_GUSTA else "NO_GUSTA"
        ejemplos.append((peli["caracteristicas"], etiqueta))
    return ejemplos


def entrenar_para_usuario(usuario_id: int) -> Nodo:
    """Entrena un árbol de decisión personalizado para el usuario."""
    ejemplos = _ejemplos_de_usuario(usuario_id)
    return construir_arbol(ejemplos, list(CARACTERISTICAS))


def recomendar_con_arbol(usuario_id: int, n: int = 10):
    """
    Usa el árbol de decisión del usuario para decidir qué películas NO vistas
    recomendar (aquellas que el árbol clasifica como "GUSTA").
    """
    arbol = entrenar_para_usuario(usuario_id)
    vistos = set(RATINGS.get(usuario_id, {}))

    recomendadas = []
    for pid, peli in PELICULAS_POR_ID.items():
        if pid in vistos:
            continue
        if predecir(arbol, peli["caracteristicas"]) == "GUSTA":
            recomendadas.append(peli)

    return recomendadas[:n], arbol


def explicar_arbol(nodo: Nodo, profundidad: int = 0):
    """
    Representa el árbol como texto indentado (útil para el informe y para
    depurar). Recorrido RECURSIVO en preorden.
    """
    sangria = "  " * profundidad
    if nodo.es_hoja:
        return f"{sangria}-> {nodo.prediccion} (n={nodo.soporte})\n"
    texto = f"{sangria}[{nodo.caracteristica}?]\n"
    for valor, hijo in sorted(nodo.hijos.items()):
        etiqueta = "sí" if valor == 1 else "no"
        texto += f"{sangria}  {etiqueta}:\n"
        texto += explicar_arbol(hijo, profundidad + 2)
    return texto
