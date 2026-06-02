# Propuesta de solución — Sistema de recomendación personalizado para StreamFlix

**Curso:** Artificial Intelligence with Machine Learning
**Caso práctico:** Implementación de un sistema de recomendación de películas
**Plataforma:** StreamFlix (streaming, +15 millones de suscriptores)

---

## 1. Resumen ejecutivo

StreamFlix utiliza hoy un sistema de recomendación **basado en popularidad** (géneros
populares y rankings generales), que es idéntico para todos los usuarios y no aprovecha el
comportamiento individual. Esto reduce la satisfacción y el tiempo de visualización.

Se propone un **sistema de recomendación personalizado** que combina dos técnicas de
Inteligencia Artificial implementadas desde cero:

1. **Filtrado colaborativo basado en usuarios** — recomienda según lo que vieron usuarios con
   gustos similares.
2. **Árbol de decisión (ID3)** — aprende qué *características* de las películas predicen que a
   un usuario le gustarán.

El sistema se entregó **funcional y desplegable** (web estilo Netflix sobre FastAPI), usando
películas de **dominio público** que se reproducen realmente vía Internet Archive.

---

## 2. Tipos de datos disponibles

Para esta propuesta se trabaja con **datos ficticios** generados de forma controlada y
reproducible (semilla fija), simulando lo que StreamFlix tendría en producción:

| Dato | Descripción | Origen real en producción |
|------|-------------|---------------------------|
| **Catálogo** | 17 películas con id, título, año, director, género y un **vector de características** binarias (terror, comedia, mudo, etc.). | Base de datos de contenido / metadatos. |
| **Usuarios** | 60 perfiles con un *arquetipo* de gustos (p. ej. "Fan del terror clásico"). | Cuentas / perfiles de la plataforma. |
| **Calificaciones (ratings)** | Matriz usuario × película con valores de 1 a 5 estrellas; con huecos (no visto). | Historial de visualización, likes, calificaciones. |
| **Popularidad** | Promedio de calificaciones por película (sistema actual). | Métricas agregadas. |

> En producción, las "estrellas" se derivarían de señales implícitas (porcentaje de la película
> visto, repeticiones, "me gusta", abandonos) además de calificaciones explícitas.

---

## 3. Identificación de patrones y análisis de preferencias mediante IA

El sistema descubre patrones sin reglas manuales:

- **Similitud entre usuarios:** mediante **similitud del coseno** sobre las calificaciones
  comunes, agrupa a los usuarios por afinidad de gustos. Dos "fans del terror" obtienen
  similitud ≈ 1.0 aunque nunca se definió explícitamente esa categoría.
- **Importancia de características:** el árbol de decisión calcula la **ganancia de información**
  de cada característica y revela cuáles predicen mejor el gusto de cada usuario (p. ej., para un
  usuario, "¿es de terror?" separa mejor que "¿es romance?").

---

## 4. Algoritmos implementados

### 4.1 Filtrado colaborativo (usuarios similares)

Para predecir la calificación de un usuario *u* a una película *i* no vista:

```
            Σ ( sim(u, v) · rating(v, i) )
pred(u,i) = ───────────────────────────────     para los vecinos v que vieron i
                  Σ | sim(u, v) |
```

donde `sim(u, v)` es la similitud del coseno entre los vectores de calificaciones de *u* y *v*.
Se recomiendan las películas no vistas con mayor `pred`.

### 4.2 Filtrado basado en contenido + árbol de decisión

Cada película tiene un vector de características binarias. Para cada usuario se entrena un
**árbol de decisión ID3**:

- **Ejemplos:** las películas que el usuario ya calificó.
- **Etiqueta:** `GUSTA` si rating ≥ 4, `NO_GUSTA` en caso contrario.
- **Criterio de división:** la característica con mayor **ganancia de información**
  (reducción de entropía de Shannon).
- El árbol se construye **recursivamente** hasta que los nodos son puros o se agotan las
  características.

Luego, para una película no vista, se recorre el árbol (también de forma recursiva) y se
recomienda si la hoja predice `GUSTA`.

---

## 5. Uso de la recursividad

La recursividad se aplica en tres lugares concretos del código:

1. **Cálculos vectoriales** (`producto_punto_recursivo`, `suma_recursiva`) usados por la
   similitud del coseno.
2. **Construcción y recorrido del árbol de decisión** — un árbol es una estructura
   intrínsecamente recursiva (un nodo contiene subárboles).
3. **Recomendaciones en cadena** (`recomendaciones_en_cadena`) — explora la red de
   "vecinos de vecinos" a una profundidad dada, descubriendo películas más allá del círculo
   inmediato del usuario. Es un recorrido recursivo de un grafo de similitud.

---

## 6. Validación del modelo (cross-validation)

Se implementó **validación cruzada k-fold (k = 5)** desde cero:

- Se reparten todas las calificaciones conocidas en 5 bloques.
- En cada ronda, 4 bloques entrenan y 1 se usa para evaluar (sin "ver" el dato de prueba).
- Se promedian las métricas.

| Modelo | Métrica | Resultado (k=5) | Interpretación |
|--------|---------|-----------------|----------------|
| Filtrado colaborativo | **RMSE** | ≈ 1.40 (escala 1–5) | Error de predicción de estrellas. |
| Filtrado colaborativo | **MAE** | ≈ 1.12 | Error absoluto medio. |
| Árbol de decisión | **Precisión** | ≈ 82.7 % | Aciertos al clasificar GUSTA/NO_GUSTA. |

> Los valores exactos se calculan en vivo en el endpoint `/api/metricas` y se muestran en el
> panel inferior de la web.

---

## 7. Comparación con el sistema actual

| Criterio | Sistema actual (popularidad) | Sistema propuesto (IA) |
|----------|------------------------------|------------------------|
| Personalización | Nula (igual para todos) | Por usuario |
| Datos que usa | Promedio global | Historial individual + similares |
| Descubrimiento | Solo lo popular | Contenido de nicho relevante |
| Explicabilidad | "Es popular" | "Porque a usuarios como tú les gustó" / reglas del árbol |
| Métrica esperada | — | Mayor satisfacción y tiempo de visualización |

**Ejemplo real del sistema** (usuario "Fan del terror clásico"):
el sistema actual le muestra *El fantasma de la ópera* y *La quimera del oro* (lo más popular en
general), mientras que el sistema personalizado le recomienda *Nosferatu*, *Carnival of Souls* y
*House on Haunted Hill* — claramente alineadas con su gusto por el terror.

---

## 8. Casos de éxito en la industria

- **Netflix:** su sistema de recomendación influye en más del **80 % del contenido visto**; la
  compañía ha estimado su valor en más de **1.000 millones de dólares anuales** por la
  reducción de cancelaciones.
- **Amazon Prime Video / Amazon:** el filtrado colaborativo ("los clientes que vieron esto
  también vieron…") es pionero y atribuye una porción significativa de las reproducciones.
- **YouTube:** las recomendaciones generan la mayoría del tiempo de visualización de la
  plataforma.
- **Spotify:** aunque es de audio, su "Discover Weekly" demuestra el mismo principio de
  filtrado colaborativo + contenido aplicado a millones de usuarios.

Estos casos confirman que la personalización mediante IA es el estándar de la industria del
streaming y un factor directo de retención.

---

## 9. Infraestructura tecnológica para el despliegue

| Componente | Tecnología propuesta (prototipo) | Equivalente en producción real |
|------------|----------------------------------|--------------------------------|
| Backend / API | Python + FastAPI + Uvicorn | FastAPI/Java en contenedores escalables |
| Servidor | Render (plan free) | Kubernetes / AWS ECS con autoescalado |
| Base de datos | Datos en memoria (ficticios) | PostgreSQL (perfiles) + Redis (caché de recomendaciones) |
| Almacenamiento de vídeo | Internet Archive (embed) | CDN + almacenamiento de objetos (S3/GCS) |
| Cálculo de modelos | En proceso | Pipeline batch + *feature store* |
| Frontend | HTML/CSS/JS | SPA (React) servida por CDN |

---

## 10. Costos estimados

**Prototipo académico (este proyecto): USD 0** — Render free + Internet Archive + GitHub.

**Estimación para producción (orden de magnitud, mensual):**

| Concepto | Estimado (USD/mes) |
|----------|--------------------|
| Cómputo API (autoescalado) | 300 – 1.500 |
| Base de datos gestionada (PostgreSQL + Redis) | 200 – 800 |
| CDN + almacenamiento de vídeo | Variable según tráfico (puede ser el mayor costo) |
| Pipeline de entrenamiento de modelos | 150 – 600 |
| Monitoreo y logs | 50 – 200 |
| **Mantenimiento** (1–2 ingenieros) | Costo de personal |

> El costo dominante en una plataforma real es la **entrega de vídeo (CDN)**, no el motor de
> recomendación. El motor en sí es relativamente económico de operar.

---

## 11. Formato para medir la satisfacción del usuario

Se proponen dos mecanismos:

1. **Encuesta breve in-app** (escala 1–5):
   - "¿Qué tan relevantes te parecieron las recomendaciones de hoy?"
   - "¿Encontraste algo nuevo que te gustó?"
   - "¿Recomendarías StreamFlix a un amigo?" (NPS).
2. **Métricas implícitas (A/B testing):** CTR sobre las recomendaciones, tiempo de
   visualización, tasa de finalización de películas y retención a 30 días, comparando el grupo
   con el sistema nuevo contra el grupo con el sistema actual.

---

## 12. Conclusiones

La propuesta cumple todos los requisitos del caso práctico: integra **IA, filtrado colaborativo,
árboles de decisión, recursividad y validación cruzada**, supera al sistema basado en
popularidad en personalización y explicabilidad, y se entrega como un producto **funcional y
desplegable** con contenido reproducible legalmente. Los resultados de la validación
(precisión ≈ 83 % en el árbol; RMSE ≈ 1.4 en el filtrado colaborativo) demuestran su
factibilidad técnica.
