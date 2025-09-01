import duckdb

# ID des fichiers Google Drive en constance avec convention majuscule
FILE_ID = "10qVBsRX_qX8OyWTqumGHwl9134M4PY-P"

#Constante pour les nom de tables
TEMPERATURE_AIR = "temperature_air"

def creerInsererDonnees(file_id, table_name):
    # Télécharger
    url = f"https://drive.google.com/uc?export=download&id={file_id}"

    con = duckdb.connect("mydb.duckdb")

    # Lecture directe et insertion
    con.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} AS 
        SELECT * FROM read_csv_auto('{url}')
    """)

    print(con.execute(f'SELECT * FROM "{table_name}" LIMIT 5').fetchall())

# application des fonctions pour importer les données en base
creerInsererDonnees(FILE_ID, TEMPERATURE_AIR)