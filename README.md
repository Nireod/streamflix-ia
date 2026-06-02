# 🎬 StreamFlix — Sistema de recomendación de películas con IA

Proyecto final del curso **Artificial Intelligence with Machine Learning** (adaptado a Python).
Implementa un sistema de recomendación personalizado para una plataforma de streaming
ficticia, **StreamFlix**, con una interfaz web estilo Netflix y películas de **dominio público**
reproducibles desde [Internet Archive](https://archive.org).

## ✨ Características

- **Filtrado colaborativo** basado en usuarios (similitud del coseno) — implementado desde cero.
- **Árbol de decisión** (algoritmo ID3 con entropía y ganancia de información) — desde cero.
- **Recursividad** aplicada al recorrido del árbol y a la red de "usuarios similares".
- **Validación cruzada** (k-fold) con métricas MAE, RMSE y precisión.
- **Interfaz web estilo Netflix**: carruseles, carátulas, perfiles y reproductor real.
- **Comparación** entre el sistema actual (popularidad) y el nuevo (IA personalizada).
- **17 películas de dominio público** que se reproducen de verdad (Nosferatu, Metropolis, etc.).

## 🗂️ Estructura

```
.
├── app/
│   ├── main.py                  # API FastAPI + servir frontend
│   ├── recommender/
│   │   ├── catalogo.py          # catálogo de películas (Archive.org)
│   │   ├── datos.py             # usuarios y ratings ficticios
│   │   ├── colaborativo.py      # filtrado colaborativo + recursividad
│   │   ├── arbol.py             # árbol de decisión (ID3) desde cero
│   │   └── validacion.py        # cross-validation y métricas
│   └── static/                  # frontend (HTML/CSS/JS estilo Netflix)
├── docs/
│   ├── PROPUESTA.md             # documento de propuesta (preguntas guía, costos…)
│   └── diagramas/               # diagramas de arquitectura y algoritmos
├── requirements.txt
├── render.yaml                  # despliegue en Render
├── Dockerfile                   # despliegue alternativo por Docker
└── README.md
```

## 🚀 Ejecución local

```bash
# 1. Crear y activar el entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Arrancar el servidor
uvicorn app.main:app --reload
```

Abre <http://localhost:8000> en el navegador.

## ☁️ Despliegue en Render

1. Sube este repositorio a GitHub.
2. En [Render](https://dashboard.render.com), crea un **New > Blueprint** y conecta el repo
   (Render detectará `render.yaml` automáticamente). También puedes crear un **Web Service**
   manual con:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Deja el plan **Free** y despliega. En unos minutos tendrás la URL pública.

> **Nota:** en el plan gratuito de Render el servicio "se duerme" tras unos minutos de
> inactividad; la primera visita tras el reposo puede tardar ~30 s en responder.

## 🔌 Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/usuarios` | Lista de perfiles ficticios |
| GET | `/api/catalogo` | Catálogo completo, agrupado por género |
| GET | `/api/pelicula/{id}` | Detalle + URL de reproducción |
| GET | `/api/recomendaciones/{uid}` | Recomendaciones personalizadas |
| GET | `/api/populares` | Ranking del sistema actual (popularidad) |
| GET | `/api/comparacion/{uid}` | Personalizado vs popular |
| GET | `/api/metricas` | Resultados de la validación cruzada |
| GET | `/api/arbol/{uid}` | Árbol de decisión del usuario (texto) |

## 📚 Películas

Todas las películas son de **dominio público** y se reproducen embebiendo el reproductor
oficial de Internet Archive (`https://archive.org/embed/<id>`). No se aloja ningún archivo
de vídeo en este repositorio ni en el servidor.

## 📄 Licencia

Código del proyecto: uso académico. Las películas pertenecen al dominio público.
