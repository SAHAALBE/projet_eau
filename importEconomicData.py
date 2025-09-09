import duckdb

# ID des fichiers Google Drive en constance avec convention majuscule
POPULATION_FILE_ID = "1tCn1OEI9zY_MngiRo7jZRxdpEYFRYsfWLqOYg1A0DPk"
POPULATION_GID = "852815993"

GDP_FILE_ID = "1ng7mdgNcFEbqFSluO1Dnjx0i4Dx4hRQG"

SANITATION_FILE_ID = "19eD6tj57ge1FCsZwZL7HsPGoZ3nFJueoq_LctE0YkuQ"
SANITATION_GID = "1513564853"

CLEAN_WATER_ACCESS_FILE_ID = "1wmWYnrEXKwfEKVOy7bcwMVkKny2K4YKoWRHBs-clbYg"
CLEAN_WATER_ACCESS_GID = "1512777463"

#Constante pour les nom de tables
ECONOMIC = "economic"
def creerInsererDonnees(file_id, table_name, gid,):
    # Télécharger
    url = f"https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&gid={gid}"

    con = duckdb.connect("mydb.duckdb")
    
    # vider la table si elle existe
    con.execute(f"DROP TABLE IF EXISTS {table_name}")

    # Créer une vue source Population et détecter dynamiquement les colonnes d'années au format "1992 [YR1992]"
    con.execute(f"CREATE OR REPLACE VIEW tmp_src_pop AS SELECT * FROM read_csv_auto('{url}')")

    # Récupérer les colonnes candidates Population (ex: 1992 [YR1992]) et construire la liste pour UNPIVOT
    cols_info_pop = con.execute("PRAGMA table_info('tmp_src_pop')").fetchall()
    year_cols_pop = []
    for _, col_name, *_ in cols_info_pop:
        # Colonne commençant par 4 chiffres suivis d'un espace et [YRxxxx]
        if (
            len(col_name) >= 12
            and col_name[:4].isdigit()
            and ' [YR' in col_name
            and col_name.endswith(']')
        ):
            year_cols_pop.append(col_name)

    if not year_cols_pop:
        raise RuntimeError("Aucune colonne année trouvée (format 'YYYY [YRYYYY]') dans la source.")

    # Construire la clause IN et les CAST homogènes pour Population
    unpivot_in_pop = ", ".join([f'"{c}"' for c in year_cols_pop])
    cast_cols_pop = ", ".join([f"TRY_CAST(REPLACE(CAST(\"{c}\" AS VARCHAR), ',', '') AS DOUBLE) AS \"{c}\"" for c in year_cols_pop])

    # Charger le fichier GDP via le lien uc?export=download&id=...
    gdp_url = f"https://drive.google.com/uc?export=download&id={GDP_FILE_ID}"
    con.execute(f"CREATE OR REPLACE VIEW tmp_src_gdp AS SELECT * FROM read_csv_auto('{gdp_url}')")

    # Récupérer les colonnes candidates GDP
    cols_info_gdp = con.execute("PRAGMA table_info('tmp_src_gdp')").fetchall()
    year_cols_gdp = []
    for _, col_name, *_ in cols_info_gdp:
        if (
            len(col_name) >= 12
            and col_name[:4].isdigit()
            and ' [YR' in col_name
            and col_name.endswith(']')
        ):
            year_cols_gdp.append(col_name)

    if not year_cols_gdp:
        raise RuntimeError("Aucune colonne année trouvée pour le GDP (format 'YYYY [YRYYYY]').")

    unpivot_in_gdp = ", ".join([f'"{c}"' for c in year_cols_gdp])
    cast_cols_gdp = ", ".join([f"TRY_CAST(REPLACE(CAST(\"{c}\" AS VARCHAR), ',', '') AS DOUBLE) AS \"{c}\"" for c in year_cols_gdp])

    # Charger le fichier Sanitation (même méthode que Population via export CSV avec gid)
    sanitation_url = f"https://docs.google.com/spreadsheets/d/{SANITATION_FILE_ID}/export?format=csv&gid={SANITATION_GID}"
    con.execute(f"CREATE OR REPLACE VIEW tmp_src_san AS SELECT * FROM read_csv_auto('{sanitation_url}')")

    # Récupérer les colonnes candidates Sanitation
    cols_info_san = con.execute("PRAGMA table_info('tmp_src_san')").fetchall()
    year_cols_san = []
    for _, col_name, *_ in cols_info_san:
        if (
            len(col_name) >= 12
            and col_name[:4].isdigit()
            and ' [YR' in col_name
            and col_name.endswith(']')
        ):
            year_cols_san.append(col_name)

    if not year_cols_san:
        raise RuntimeError("Aucune colonne année trouvée pour Sanitation (format 'YYYY [YRYYYY]').")

    unpivot_in_san = ", ".join([f'"{c}"' for c in year_cols_san])
    cast_cols_san = ", ".join([f"TRY_CAST(REPLACE(CAST(\"{c}\" AS VARCHAR), ',', '') AS DOUBLE) AS \"{c}\"" for c in year_cols_san])

    # Charger le fichier Clean Water Access (même méthode que Sanitation via export CSV avec gid)
    cwa_url = f"https://docs.google.com/spreadsheets/d/{CLEAN_WATER_ACCESS_FILE_ID}/export?format=csv&gid={CLEAN_WATER_ACCESS_GID}"
    con.execute(f"CREATE OR REPLACE VIEW tmp_src_cwa AS SELECT * FROM read_csv_auto('{cwa_url}')")

    # Récupérer les colonnes candidates Clean Water Access
    cols_info_cwa = con.execute("PRAGMA table_info('tmp_src_cwa')").fetchall()
    year_cols_cwa = []
    for _, col_name, *_ in cols_info_cwa:
        if (
            len(col_name) >= 12
            and col_name[:4].isdigit()
            and ' [YR' in col_name
            and col_name.endswith(']')
        ):
            year_cols_cwa.append(col_name)

    if not year_cols_cwa:
        raise RuntimeError("Aucune colonne année trouvée pour Clean Water Access (format 'YYYY [YRYYYY]').")

    unpivot_in_cwa = ", ".join([f'"{c}"' for c in year_cols_cwa])
    cast_cols_cwa = ", ".join([f"TRY_CAST(REPLACE(CAST(\"{c}\" AS VARCHAR), ',', '') AS DOUBLE) AS \"{c}\"" for c in year_cols_cwa])

    # Transformation: dé-pivoter Population et GDP, puis joindre par pays/année au format DE1992
    con.execute(f"""
        CREATE TABLE {table_name} AS
        WITH pop AS (
            SELECT
                (SUBSTR("Country Code", 1, 2) || split_part(year_col, ' ', 1)) AS country_year,
                CAST(value AS BIGINT) AS population_total
            FROM (
                SELECT "Country Code", {cast_cols_pop}
                FROM tmp_src_pop
                WHERE "Series Code" = 'SP.POP.TOTL'
            )
            UNPIVOT (value FOR year_col IN ({unpivot_in_pop})) u
            WHERE CAST(split_part(year_col, ' ', 1) AS INTEGER) >= 1992
        ),
        gdp AS (
            SELECT
                (SUBSTR("Country Code", 1, 2) || split_part(year_col, ' ', 1)) AS country_year,
                CAST(value AS DOUBLE) AS gdp
            FROM (
                SELECT "Country Code", {cast_cols_gdp}
                FROM tmp_src_gdp
            )
            UNPIVOT (value FOR year_col IN ({unpivot_in_gdp})) u
            WHERE CAST(split_part(year_col, ' ', 1) AS INTEGER) >= 1992
        ),
        san AS (
            SELECT
                (SUBSTR("Country Code", 1, 2) || split_part(year_col, ' ', 1)) AS country_year,
                CAST(value AS DOUBLE) AS sanitation
            FROM (
                SELECT "Country Code", {cast_cols_san}
                FROM tmp_src_san
            )
            UNPIVOT (value FOR year_col IN ({unpivot_in_san})) u
            WHERE CAST(split_part(year_col, ' ', 1) AS INTEGER) >= 1992
        ),
        cwa AS (
            SELECT
                (SUBSTR("Country Code", 1, 2) || split_part(year_col, ' ', 1)) AS country_year,
                CAST(value AS DOUBLE) AS clean_water_access
            FROM (
                SELECT "Country Code", {cast_cols_cwa}
                FROM tmp_src_cwa
            )
            UNPIVOT (value FOR year_col IN ({unpivot_in_cwa})) u
            WHERE CAST(split_part(year_col, ' ', 1) AS INTEGER) >= 1992
        )
        SELECT
            p.country_year,
            p.population_total,
            ROUND(g.gdp, 2) AS gdp,
            ROUND(s.sanitation, 2) AS sanitation,
            ROUND(w.clean_water_access, 2) AS clean_water_access
        FROM pop p
        LEFT JOIN gdp g ON g.country_year = p.country_year
        LEFT JOIN san s ON s.country_year = p.country_year
        LEFT JOIN cwa w ON w.country_year = p.country_year
    """)

    print(con.execute(f'SELECT * FROM "{table_name}" LIMIT 5').fetchall())

# application des fonctions pour importer les données en base
creerInsererDonnees(POPULATION_FILE_ID, ECONOMIC, POPULATION_GID)