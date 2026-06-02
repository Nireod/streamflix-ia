# Imagen base ligera de Python.
FROM python:3.12-slim

WORKDIR /app

# Instala dependencias primero (mejor cacheo de capas).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código de la aplicación.
COPY app ./app

# Render inyecta el puerto en $PORT; por defecto usamos 8000 en local.
ENV PORT=8000
EXPOSE 8000

# Arranca el servidor. La forma "shell" permite expandir $PORT.
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
