# Anotación funcional de MAGs

La anotación funcional de MAGs es esencial para obtener información sobre su potencial metabólico, sus roles ecológicos y sus posibles aplicaciones biotecnológicas o biomédicas.

## Herramienta utilizada

En este taller se usará **Bakta**, una herramienta rápida y completa para la anotación de genomas bacterianos y arqueales. Bakta predice genes, asigna funciones y genera archivos de salida útiles para describir el contenido funcional de cada MAG.

## Configuración de directorios de salida

Cree una nueva carpeta llamada `MAGs_func_annotation`. Dentro de esta carpeta, cree el subdirectorio `bakta_out`:

```bash
mkdir -p MAGs_func_annotation/bakta_out
```

La estructura esperada será:

```bash
MAGs_func_annotation/
└── bakta_out/
```

## Crear y ejecutar el script para correr Bakta

Para ejecutar Bakta, cree un script llamado `run_bakta.sh`:

```bash
nano run_bakta.sh
```

Copie el siguiente contenido y modifique la variable `batchfile` con la ruta correcta al archivo `batchfile.txt` creado previamente:

```bash
#!/bin/bash

#SBATCH -J bakta
#SBATCH -D .
#SBATCH -e bakta_%j.err
#SBATCH -o bakta_%j.out
#SBATCH --cpus-per-task=8
#SBATCH --time=4:00:00	
#SBATCH --mem=8000

source /hpcfs/home/cursos/metagenomica_moderna/conda/bin/activate
conda activate bakta

batchfile="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/bins_taxonomy/batchfile.txt"

while IFS=$'\t' read -r file MAG_ID; do

    bakta --db /hpcfs/home/cursos/metagenomica_moderna/databases/bakta_db_ligth/db-light --output bakta_out/$MAG_ID --threads 8 --prefix $MAG_ID $file

done < $batchfile
```

Este script lee el `batchfile.txt`, toma la ruta de cada MAG y su identificador, y ejecuta Bakta de forma individual para cada genoma.

Después de crear y guardar el script, dele permisos de ejecución:

```bash
chmod +x run_bakta.sh
```

Luego envíelo al clúster:

```bash
sbatch run_bakta.sh
```

## Descripción de la salida

Después de completar la anotación funcional, la carpeta `MAGs_func_annotation` tendrá una estructura similar a esta:

```bash
MAGs_func_annotation/
└── bakta_out/
    └── MAG_ID/
        ├── MAG_ID.tsv
        ├── MAG_ID.gff3
        ├── MAG_ID.gbff
        ├── MAG_ID.faa
        ├── MAG_ID.ffn
        ├── MAG_ID.png
        ├── MAG_ID.svg
        └── MAG_ID.log
```

- El archivo `.tsv` contiene la tabla principal de anotación funcional de los genes predichos.
- El archivo `.gff3` contiene las coordenadas y características genómicas anotadas.
- El archivo `.faa` contiene las secuencias de proteínas predichas.
- El archivo `.ffn` contiene las secuencias nucleotídicas de los genes predichos.
- Los archivos `.png` y `.svg` corresponden a visualizaciones del genoma anotado.
- El archivo `.log` resume la ejecución de Bakta y permite revisar posibles errores o advertencias.

