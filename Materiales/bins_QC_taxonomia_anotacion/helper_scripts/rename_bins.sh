#!/bin/bash

DIR="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/all_bins"
LOG="rename_bin_files.log"

echo -e "old_name\tnew_name" > "$LOG"

declare -A count

for f in "$DIR"/*.fa; do
    old=$(basename "$f")

    # Quitar todo lo que está antes del primer guion
    new="${old#*-}"

    # Quitar todo lo que está antes del segundo guion
    new="${new#*-}"

    # Extraer el código de la muestra
    # Ejemplo: SRR17048902.033_sub.fa -> SRR17048902
    sample="${new%%.*}"

    # Aumentar el contador para esa muestra
    count[$sample]=$(( ${count[$sample]:-0} + 1 ))

    # Crear número secuencial con dos dígitos
    num=$(printf "%02d" "${count[$sample]}")

    # Crear nuevo nombre
    new="${sample}_${num}.fa"

    mv "$f" "$DIR/$new"
    echo -e "$old\t$new" >> "$LOG"
done