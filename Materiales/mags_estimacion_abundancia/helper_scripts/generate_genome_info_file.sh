#!/bin/bash

# Archivo de entrada con los MAGs que pasaron CheckM2 y GUNC
input_file="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/bins_qc/gunc_and_checkm2_output_pass.csv"

# Archivo final con la información simplificada de calidad para drep
genome_info_file="genome_info_file.csv"

# Escribir el encabezado del archivo de salida
echo "genome,completeness,contamination" > "$genome_info_file"

# Leer el archivo de entrada, saltar el encabezado y extraer:
# columna 1 = nombre del genoma
# columna 2 = completitud
# columna 3 = contaminación
# También se agrega ".fa" al nombre del genoma
awk -F',' 'NR > 1 {print $1".fa,"$2","$3}' "$input_file" >> "$genome_info_file"

echo "Archivo generado: $genome_info_file"