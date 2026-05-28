#!/bin/bash

# Directory containing the .fa files
input_dir="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/all_bins"

# Recorrer todos los archivos .fa de la carpeta
for file in "$input_dir"/*.fa; do
    filename=$(basename "$file" .fa)  # Obtener el nombre del archivo sin extensión
    temp_file="${file}.tmp"  # Crear archivo temporal
    contig_number=1  # Initialize contig counter

    # Renombrar los contigs usando el nombre del archivo como prefijo
    awk -v prefix="${filename}_c_" '
    BEGIN { contig_number=1; OFS="\n" }
    /^>/ {
        printf ">%s%010d\n", prefix, contig_number++
        next
    }
    { print }
    ' "$file" > "$temp_file"

    # Reemplazar el archivo original con la versión modificada: >SRR17048902_01_c_000000000001
    mv "$temp_file" "$file"
    
 done

   echo "Contigs renamed successfully in all .fa files."