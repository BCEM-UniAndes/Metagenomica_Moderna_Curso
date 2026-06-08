#!/home/bioinf-cabana/conda/envs/python_3.13.2/bin/python


import pandas as pd
from pathlib import Path

# File paths
taxonomy = "/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/bins_taxonomy/gtdbtk_out/gtdbtk.bac120.summary.tsv"

# Carpeta donde están los genomas representativos
genome_dir = Path("/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_drep/drep_out/dereplicated_genomes")

output_csv_path = "/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_abundance_estimation/mags_taxonomy.csv"

# Step 1: Get genome names from the representative genomes folder
# file.stem removes the .fa extension, for example: MAG001.fa -> MAG001
genome_names = [file.stem for file in genome_dir.glob("*.fa")]

# Step 2: Read GTDB-Tk taxonomy table
taxonomy_data = pd.read_csv(taxonomy, sep="\t")

# Step 3: Filter only representative genomes
filtered_data = taxonomy_data[taxonomy_data["user_genome"].isin(genome_names)].copy()

# Step 4: Parse GTDB-Tk classification into taxonomic levels
taxonomy_columns = ["Domain", "Phylum", "Class", "Order", "Family", "Genus", "Species"]

for level in taxonomy_columns:
    prefix = level[0].lower() + "__"
    filtered_data[level] = (
        filtered_data["classification"]
        .str.extract(f"({prefix}[^;]*)")[0]
        .str.replace(prefix, "", regex=False)
    )

# Step 5: Keep only relevant columns and replace missing taxonomy with empty strings
filtered_data = filtered_data[["user_genome"] + taxonomy_columns].fillna("")

# Step 6: Save the final taxonomy table
filtered_data.to_csv(output_csv_path, index=False)
