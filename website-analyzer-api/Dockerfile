# Dockerfile

# 1. Start mit einem offiziellen Python-Image
FROM python:3.11-slim

# 2. Setzt das Arbeitsverzeichnis im Container
WORKDIR /app

# NEU: Fügt das Hauptverzeichnis zum Python-Suchpfad hinzu
# Das löst das "ModuleNotFoundError: No module named 'app'"-Problem
ENV PYTHONPATH=/

# 3. Anforderungen kopieren und installieren
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# 4. Den gesamten App-Code in den Container kopieren
COPY ./app /app