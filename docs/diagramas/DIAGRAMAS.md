# Diagramas del sistema StreamFlix

Diagramas en formato **Mermaid** (se renderizan automáticamente en GitHub y en
editores compatibles). Cada uno acompaña una parte de la propuesta.

---

## 1. Arquitectura general

```mermaid
flowchart TB
    subgraph Cliente["🖥️ Cliente (navegador)"]
        UI["Frontend estilo Netflix<br/>HTML · CSS · JS"]
    end

    subgraph Render["☁️ Render (servidor)"]
        API["API FastAPI<br/>app/main.py"]
        subgraph Motor["🧠 Motor de recomendación"]
            COL["Filtrado colaborativo<br/>(similitud coseno)"]
            ARB["Árbol de decisión<br/>(ID3)"]
            VAL["Validación cruzada<br/>(k-fold)"]
        end
        DATOS["Datos ficticios<br/>usuarios + ratings"]
        CAT["Catálogo de películas"]
    end

    subgraph Externo["🌐 Internet Archive"]
        IA["Reproductor embed<br/>archive.org/embed/&lt;id&gt;"]
    end

    UI -->|"GET /api/recomendaciones"| API
    API --> COL
    API --> ARB
    API --> VAL
    COL --> DATOS
    ARB --> CAT
    COL --> CAT
    UI -->|"reproduce película"| IA
```

---

## 2. Flujo del proceso de recomendación

```mermaid
flowchart LR
    A["Usuario elige<br/>su perfil"] --> B["Cargar su historial<br/>de calificaciones"]
    B --> C{"¿Tiene<br/>historial?"}
    C -->|Sí| D["Buscar usuarios<br/>similares<br/>(coseno)"]
    C -->|Poco| E["Usar árbol de<br/>decisión por<br/>características"]
    D --> F["Predecir rating de<br/>películas no vistas"]
    E --> F
    F --> G["Ordenar por<br/>rating predicho"]
    G --> H["Mostrar carruseles<br/>personalizados"]
    H --> I["Usuario reproduce<br/>(embed Archive.org)"]
```

---

## 3. Algoritmo de filtrado colaborativo

```mermaid
flowchart TB
    inicio(["recomendar(usuario)"]) --> v["Obtener vecinos:<br/>similitud coseno con<br/>todos los demás usuarios"]
    v --> orden["Ordenar vecinos<br/>por similitud (top-k)"]
    orden --> loop["Para cada película<br/>NO vista por el usuario"]
    loop --> pred["pred = Σ(sim·rating) / Σ(sim)<br/>sobre vecinos que la vieron"]
    pred --> rank["Ranking por rating<br/>predicho"]
    rank --> fin(["Top-N recomendaciones"])
```

---

## 4. Construcción recursiva del árbol de decisión (ID3)

```mermaid
flowchart TB
    start(["construir_arbol(ejemplos, features)"]) --> base1{"¿Todos los ejemplos<br/>tienen la misma etiqueta?"}
    base1 -->|Sí| hoja1["Hoja: esa etiqueta"]
    base1 -->|No| base2{"¿Sin features o<br/>profundidad máxima?"}
    base2 -->|Sí| hoja2["Hoja: clase mayoritaria"]
    base2 -->|No| mejor["Elegir feature con<br/>mayor ganancia de información"]
    mejor --> split["Dividir ejemplos por<br/>el valor de esa feature (0 / 1)"]
    split --> rec0["construir_arbol(subconjunto=0) 🔁"]
    split --> rec1["construir_arbol(subconjunto=1) 🔁"]
    rec0 --> nodo["Nodo de decisión<br/>con dos subárboles"]
    rec1 --> nodo
```

---

## 5. Ejemplo de árbol aprendido (usuario "Fan del terror clásico")

```mermaid
flowchart TB
    raiz{"¿drama?"}
    raiz -->|no| n1{"¿mudo?"}
    raiz -->|sí| h3["NO_GUSTA"]
    n1 -->|no| h1["NO_GUSTA"]
    n1 -->|sí| h2["GUSTA"]
```

> Este árbol se genera dinámicamente desde el endpoint `/api/arbol/{usuario_id}`.
> La estructura concreta cambia según el historial de cada usuario.
