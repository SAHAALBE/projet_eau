import duckdb

# ID des fichiers Google Drive en constance avec convention majuscule
FILE_ID = "11SodLYgjwXChgP6y7X8eJW2xnST8fcMSArYQj5-pMrc"
GID = "676334042"

#Constante pour les nom de tables
DISASTER = "disaster"
def creerInsererDonnees(file_id, table_name, gid):
    # Télécharger
    url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={gid}"

    con = duckdb.connect("mydb.duckdb")
    
    # vider la table si elle existe
    con.execute(f"DROP TABLE IF EXISTS {table_name}")

    # Lecture directe et insertion (ne garder que les colonnes demandées)
    con.execute(f"""
        CREATE TABLE {table_name} AS
        SELECT
            CONCAT("Country code", CAST("Year" AS VARCHAR)) AS country_year,
            "Cause" AS cause,
            ("Start date" || ' - ' || "End date") AS duration,
            'flood' AS type,
            COUNT(*) OVER (PARTITION BY "Country code", "Year") AS nb_extreme_events
        FROM read_csv_auto('{url}')
        WHERE CAST("Year" AS INTEGER) > 1992
    """)

    print(con.execute(f'SELECT * FROM "{table_name}" LIMIT 5').fetchall())

# application des fonctions pour importer les données en base
creerInsererDonnees(FILE_ID, DISASTER, GID)