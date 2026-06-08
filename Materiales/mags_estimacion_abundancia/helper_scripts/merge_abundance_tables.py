#!/hpcfs/home/cursos/metagenomica_moderna/conda/envs/python-env/bin/python

import pandas as pd
from pathlib import Path

# Carpeta donde están todos los archivos de abundancia generados por msamtools
input_dir = Path("/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_abundance_estimation/msamtools_out")

# Lista donde se guardará la abundancia de cada muestra
abundance_tables = []

# Leer todos los archivos que terminan en .profile.txt
for file in input_dir.glob("*.profile.txt"):

    # Usar el nombre del archivo como identificador de la muestra
    sample_id = file.name.replace(".profile.txt", "")

    # Leer la tabla de abundancia, omitiendo las primeras 11 líneas del encabezado
    df = pd.read_csv(
        file,
        sep="\t",
        skiprows=11,
        header=None,
        names=["genome_id", sample_id]
    )

    # Quitar la extensión .fa del nombre de los genomas, si está presente
    df["genome_id"] = df["genome_id"].str.replace(".fa", "", regex=False)

    # Eliminar genomas repetidos, conservando la primera aparición
    df = df.drop_duplicates(subset="genome_id", keep="first")

    # Usar los genomas como índice para poder unir las tablas por genome_id
    df = df.set_index("genome_id")

    # Guardar la tabla de esta muestra en la lista
    abundance_tables.append(df)

# Unir todas las tablas por genome_id y reemplazar valores faltantes por 0
merged_abundance = pd.concat(abundance_tables, axis=1).fillna(0)

# Transponer la tabla para dejar muestras en filas y genomas en columnas
merged_abundance = merged_abundance.T

# Nombrar el índice como Sample
merged_abundance.index.name = "Sample"

# Guardar la tabla final como archivo CSV
merged_abundance.reset_index().to_csv("merged_abundance.csv", index=False)
