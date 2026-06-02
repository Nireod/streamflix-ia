# Respuestas a las preguntas guía

> Las preguntas guía orientan la propuesta de solución del caso práctico de StreamFlix.

---

## 1) ¿Cómo puede el uso de IA mejorar la personalización de las recomendaciones para cada usuario?

El sistema actual de StreamFlix muestra **lo mismo a todos** (popularidad global). La IA cambia
el enfoque de "qué es popular" a "qué le gusta a *este* usuario":

- El **filtrado colaborativo** aprende de forma automática qué usuarios se parecen entre sí
  (similitud del coseno) y propaga gustos entre ellos: si a personas con tu mismo historial les
  gustó una película, probablemente a ti también.
- El **árbol de decisión** identifica, por usuario, qué *características* del contenido predicen su
  gusto, permitiendo recomendaciones explicables.
- A medida que el usuario consume más contenido, ambos modelos se reentrenan y la
  personalización mejora continuamente (aprendizaje incremental).

Resultado: cada usuario ve una página distinta, alineada con su comportamiento real, lo que
aumenta la satisfacción y el tiempo de visualización.

---

## 2) ¿Qué diferencias existen entre el filtrado colaborativo y el análisis de contenido?

| Aspecto | Filtrado colaborativo | Análisis de contenido (árbol/características) |
|---------|-----------------------|----------------------------------------------|
| En qué se basa | En el comportamiento de **otros usuarios similares** | En los **atributos del propio contenido** |
| Necesita | Muchas calificaciones de muchos usuarios | Buenos metadatos de las películas |
| Problema del "arranque en frío" | Sufre con usuarios o películas nuevas (sin historial) | Funciona aunque la película sea nueva (tiene características) |
| Capacidad de sorpresa | Alta: descubre contenido inesperado pero apreciado | Baja: tiende a recomendar "más de lo mismo" |
| Explicabilidad | "A usuarios como tú les gustó" | "Te gusta el terror, y esta es de terror" |

**Conclusión:** para una plataforma como StreamFlix lo más **efectivo es combinarlos**
(enfoque híbrido): el contenido cubre el arranque en frío y el colaborativo aporta
descubrimiento y precisión cuando ya hay historial. Por eso la propuesta usa ambos.

---

## 3) ¿Cómo puede implementarse un árbol de decisión para identificar qué características son más relevantes?

Se implementa el algoritmo **ID3**:

1. Cada película se representa por un vector de características binarias (terror, comedia,
   mudo, ciencia ficción, etc.).
2. Para cada usuario, sus películas calificadas son los **ejemplos de entrenamiento**, con
   etiqueta `GUSTA` (≥ 4★) o `NO_GUSTA`.
3. En cada nodo se calcula la **entropía** y la **ganancia de información** de cada
   característica; se elige la de **mayor ganancia** (la que mejor separa GUSTA de NO_GUSTA).
4. Se divide el conjunto por esa característica y se repite **recursivamente** en cada rama
   hasta obtener nodos puros o agotar las características.

La característica situada en la **raíz** del árbol es la más relevante para ese usuario. Así el
modelo no solo recomienda, sino que **explica** qué atributos importan.

---

## 4) ¿Cómo se puede utilizar la recursividad para mejorar el sistema y optimizar el rendimiento?

La recursividad aparece de forma natural en tres puntos:

1. **Estructura del árbol de decisión:** construir y recorrer un árbol es inherentemente
   recursivo (cada nodo contiene subárboles). El recorrido para predecir baja recursivamente
   hasta una hoja en O(profundidad), muy eficiente.
2. **Cálculos sobre vectores:** producto punto y sumas se expresan de forma recursiva sobre
   listas (didáctico y acorde al curso).
3. **Exploración de la red de usuarios ("vecinos de vecinos"):** una función recursiva recorre
   el grafo de similitud a una profundidad limitada, descubriendo recomendaciones lejanas. El
   parámetro de **profundidad** controla el costo, evitando explosión combinatoria.

Optimización: el uso de **profundidad máxima** en el árbol y de **caché** (memoización) de
similitudes evita recálculos y mantiene el rendimiento acotado.

---

## 5) ¿Qué métricas se deben considerar para evaluar el éxito y cómo compararlas con los resultados actuales?

**Métricas offline (calidad del modelo):**
- **RMSE** y **MAE** del filtrado colaborativo (error en la predicción de calificaciones).
- **Precisión / Recall / F1** del árbol de decisión (clasificación GUSTA/NO_GUSTA).
- Todas obtenidas con **validación cruzada k-fold** para evitar sobreajuste.

**Métricas online (impacto de negocio):**
- **CTR** sobre las recomendaciones (clics / impresiones).
- **Tiempo de visualización** y **tasa de finalización**.
- **Retención** a 30 días y **reducción de cancelaciones**.
- **NPS / encuestas** de satisfacción.

**Cómo comparar con lo actual:** mediante un **test A/B** — un grupo de usuarios mantiene el
sistema de popularidad y otro recibe el sistema de IA; se comparan las métricas anteriores
entre ambos grupos durante un periodo definido. La mejora estadísticamente significativa en
tiempo de visualización y retención valida el éxito del nuevo sistema.
