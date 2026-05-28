#!/bin/bash

# Carpeta donde están los MAGs que pasaron el control de calidad
MAGs_pass="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/bins_qc/MAGs_pass_qc"

# Archivo de salida requerido por GTDB-Tk con la ruta completa de cada MAG y su ID
MAGs_path_and_name="batchfile.txt"

# Crear el archivo batchfile.txt o limpiarlo si ya existe
> "$MAGs_path_and_name"

# Recorrer todos los archivos .fa dentro de la carpeta MAGs_pass_qc
for file in "$MAGs_pass"/*.fa; do
    filename=$(basename "$file")  
    mag_id="${filename%.fa}"      

    # Escribir en el batchfile:
    # columna 1 = ruta completa del archivo .fa
    # columna 2 = ID del MAG
    echo -e "$file\t$mag_id" >> "$MAGs_path_and_name"
done

echo "Batchfile generated successfully."