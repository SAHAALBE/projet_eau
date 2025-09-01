FROM python:3.11-slim

# Copier le fichier requirements.txt et installer les dépendances
COPY requirements.txt .

# Installer DuckDB via pip
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY . /app

CMD ["python", "scriptBaseDonnees.py"]