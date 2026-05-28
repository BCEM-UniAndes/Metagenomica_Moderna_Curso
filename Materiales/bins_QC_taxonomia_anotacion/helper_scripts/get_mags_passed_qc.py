#!/hpcfs/home/cursos/metagenomica_moderna/conda/envs/python-env/bin/python

import pandas as pd
import os
import shutil

# Rutas de los archivos de salida de CheckM2 y GUNC
checkm2_output_path = "/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/bins_qc/checkm2_out/quality_report.tsv"
gunc_output_path = "/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/bins_qc/gunc_out/GUNC.progenomes_2.1.maxCSS_level.tsv"

# Carpeta donde están los bins de todas las muestras
mag_source_dir = "/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/all_bins"

# Carpeta donde se copiarán los MAGs que pasen el filtro de calidad
destination_dir = "/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/bins_qc/MAGs_pass_qc"

# Archivo de salida con la tabla filtrada de CheckM2 y GUNC
filtered_output_path = "gunc_and_checkm2_output_pass.csv"


# Leer la tabla de calidad generada por CheckM2
checkm2_output = pd.read_csv(checkm2_output_path, sep='\t')
# Cambiar el nombre de la columna Name a genome para poder unirla con GUNC
checkm2_output = checkm2_output.rename(columns={'Name': 'genome'})

# Leer la tabla de resultados de GUNC
gunc_output = pd.read_csv(gunc_output_path, sep='\t')

# # Unir la información de CheckM2 con la columna pass.GUNC de GUNC
merged_data = checkm2_output.merge(gunc_output[['genome', 'pass.GUNC']], on='genome', how='left')

# Filtrar MAGs que pasan GUNC, tienen completitud >= 50% y contaminación <= 5%
filtered_mags = merged_data[
    (merged_data['pass.GUNC'] == True) &
    (merged_data['Completeness'] >= 50) &
    (merged_data['Contamination'] <= 5)
]

# Guardar la tabla con los MAGs que pasaron el filtro de calidad
filtered_mags.to_csv(filtered_output_path, index=False)

# Copiar los archivos .fa de los MAGs que pasaron el filtro
for genome_id in filtered_mags["genome"]:

    # Ruta del archivo original en all_bins
    source_path = os.path.join(mag_source_dir, f"{genome_id}.fa")

    # Ruta donde se copiará el MAG filtrado
    destination_path = os.path.join(destination_dir, f"{genome_id}.fa")

    # Copiar el MAG filtrado a la carpeta de salida
    shutil.copy(source_path, destination_path)
    
print("MAGs that passed QC have been copied successfully.")

