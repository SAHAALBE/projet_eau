## Projet Eau – Import et préparation des données

Ce projet importe des données de catastrophes liées aux inondations depuis un Google Sheet, les transforme et les stocke dans une base DuckDB locale.

### Données générées
La table `disaster` ne contient que les colonnes suivantes, pour les années > 1992 :
- `country_year` : concaténation de `Country code` et `Year` (ex: `AL1946`).
- `cause` : contenu de `Cause`.
- `duration` : `Start date - End date` (texte).
- `type` : valeur fixe `flood`.
- `nb_extreme_events` : nombre d’événements par `Country code` et `Year`.

### Prérequis
- Python 3.10+
- Pip

### Installation
```bash
pip install -r requirements.txt
```

### Exécution (local)
Le script supprime la base DuckDB si nécessaire (si vous avez laissé cette logique dans le code) et recrée la table `disaster` avec uniquement les colonnes ci-dessus.
```bash
python importDisasterData.py
```

La base est créée à la racine du projet sous le nom `mydb.duckdb`.

### Utilisation avec Docker
Un `Dockerfile` et un `compose.yml` sont fournis.

Build et exécution du conteneur:
```bash
docker build -t projet-eau .
docker run --rm -v "$(pwd)":/app projet-eau python importDisasterData.py
```

Avec Docker Compose:
```bash
docker compose run --rm app python importDisasterData.py
```

### Fichiers importants
- `importDisasterData.py` : import et transformation des données.
- `mydb.duckdb` : base DuckDB générée (ignorée par git).
- `.gitignore` : ignore les fichiers de cache, environnements et la base DuckDB.
- `requirements.txt` : dépendances Python (inclut `duckdb`).

### Notes
- Les identifiants du Google Sheet sont définis en haut de `importDisasterData.py` (`FILE_ID`, `GID`). Adaptez-les si nécessaire.
- La table est recréée à chaque exécution pour garantir la fraîcheur et la conformité du schéma.
documentation sur le projet eau concernant notre veille technique et technologique
