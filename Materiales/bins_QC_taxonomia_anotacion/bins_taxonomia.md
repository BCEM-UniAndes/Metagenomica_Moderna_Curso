# Clasificación taxonómica de MAGs

## Descripción general

Después de evaluar la calidad de los MAGs y conservar únicamente aquellos que pasaron los filtros de calidad establecidos, el siguiente paso es asignarles una clasificación taxonómica.

Para esto se usará **GTDB-Tk**, una herramienta diseñada para clasificar genomas bacterianos y arqueales usando la base de datos **Genome Taxonomy Database**, conocida como **GTDB**. 

GTDB-Tk clasifica los genomas usando una combinación de información filogenética, divergencia evolutiva relativa y similitud nucleotídica promedio. En términos prácticos, esto permite asignar cada MAG a diferentes niveles taxonómicos, como dominio, filo, clase, orden, familia, género y especie, cuando la información disponible lo permite.

En este taller se utilizará el flujo de trabajo `classify_wf` de GTDB-Tk y la base de datos GTDB r226.

## Configuración del directorio de trabajo

Cree una nueva carpeta llamada `MAGs_taxonomy`.

Dentro de esta carpeta, cree el subdirectorio `gtdbtk_out`:

```bash
MAGs_taxonomy/
├── gtdbtk_out/
```

## Crear el batchfile para GTDB-Tk

Antes de ejecutar GTDB-Tk, es necesario crear un archivo llamado `batchfile.txt`. Este archivo le indica a GTDB-Tk cuáles genomas debe analizar y qué nombre debe usar para identificar cada MAG en los resultados.

El `batchfile.txt` es un archivo de texto con dos columnas separadas por tabulación. La primera columna contiene la ruta completa al archivo `.fa` de cada MAG, y la segunda columna contiene el identificador del MAG.

Por ejemplo:

```bash
/ruta/a/MAGs_pass_qc/SRR17048902_01.fa	SRR17048902_01
/ruta/a/MAGs_pass_qc/SRR17048902_02.fa	SRR17048902_02
/ruta/a/MAGs_pass_qc/SRR17048902_03.fa	SRR17048902_03
```

En este caso, GTDB-Tk usará los archivos `.fa` de la primera columna como entrada, y los nombres de la segunda columna como identificadores de los MAGs en los archivos de salida.

Para generar este archivo, copie el script `generate_batchfile.sh` desde la carpeta `helper_scripts` a su carpeta `MAGs_taxonomy`:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/helper_scripts/generate_batchfile.sh MAGs_taxonomy/
```

Antes de ejecutarlo, abra el script y revise que la variable `MAGs_pass` corresponda a la ruta donde están los MAGs que pasaron el control de calidad:

```bash
nano generate_batchfile.sh
```

Modifique esta línea con la ruta correcta a su carpeta personal:

```bash
MAGs_pass="/hpcfs/home/cursos/metagenomica_moderna/estudiantes/carpeta_personal/MAGs_qc/MAGs_pass_qc"
```

Recuerde reemplazar `carpeta_personal` por el nombre de su carpeta dentro del directorio de estudiantes.

Luego ejecute el script:

```bash
bash generate_batchfile.sh
```

Después de ejecutarlo, revise que se haya generado correctamente el archivo `batchfile.txt`:

```bash
ls -lh
head batchfile.txt
```

El archivo debe tener una estructura similar a esta:

```bash
/hpcfs/home/cursos/metagenomica_moderna/estudiantes/carpeta_personal/MAGs_qc/MAGs_pass_qc/SRR17048902_01.fa	SRR17048902_01
/hpcfs/home/cursos/metagenomica_moderna/estudiantes/carpeta_personal/MAGs_qc/MAGs_pass_qc/SRR17048902_02.fa	SRR17048902_02
/hpcfs/home/cursos/metagenomica_moderna/estudiantes/carpeta_personal/MAGs_qc/MAGs_pass_qc/SRR17048902_03.fa	SRR17048902_03
```

Este archivo será la entrada principal para ejecutar GTDB-Tk con la opción `--batchfile`.

## Ejecutar GTDB-Tk

Para ejecutar GTDB-Tk, cree un script llamado `run_gtdbtk.sh`:

```bash
nano run_gtdbtk.sh
```

Copie el siguiente contenido:

```bash
#!/bin/bash

#SBATCH -J gtdbtk_classify
#SBATCH -D .
#SBATCH -e gtdbtk_classify_%j.err
#SBATCH -o gtdbtk_classify_%j.out
#SBATCH --cpus-per-task=8
#SBATCH --time=6:00:00	
#SBATCH --mem=100000

source /hpcfs/home/cursos/metagenomica_moderna/conda/bin/activate
conda activate gtdbtk-2.6.1

batchfile="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/bins_taxonomy/batchfile.txt"

gtdbtk classify_wf --batchfile ${batchfile} -x fa --skip_ani_screen --cpus 8 --out_dir gtdbtk_out

```

Este script ejecuta el flujo de trabajo `classify_wf` de GTDB-Tk usando como entrada el archivo `batchfile.txt`. Los resultados se guardarán en la carpeta `gtdbtk_out`.

La opción `-x fa` indica que los archivos de entrada tienen extensión `.fa`. La opción `--cpus 8` indica que se usarán 8 CPUs, de acuerdo con lo solicitado en el encabezado de SLURM. La opción `--skip_ani_screen` omite la etapa inicial de comparación por ANI. En el contexto del taller, esta opción se usa para reducir el uso de recursos computacionales. Si se usa una versión más reciente de GTDB-Tk, esta opción puede cambiar o estar desactualizada, por lo que conviene revisar la versión instalada en el ambiente del curso.

## Enviar el trabajo al clúster

Después de crear y guardar el script, dele permisos de ejecución:

```bash
chmod +x run_gtdbtk.sh
```

Luego envíelo al clúster con:

```bash
sbatch run_gtdbtk.sh
```

Puede revisar el estado del trabajo con:

```bash
squeue -u $USER
```

## Archivos de salida esperados

Cuando GTDB-Tk termine, la carpeta `gtdbtk_out` tendrá una estructura similar a esta:

```bash
gtdbtk_out/
├── align/
├── classify/
├── identify/
├── gtdbtk.ar53.summary.tsv
├── gtdbtk.bac120.summary.tsv
├── gtdbtk.log
└── gtdbtk.warnings.log
```

- La carpeta `identify` contiene los archivos generados durante la etapa de identificación. En esta etapa, GTDB-Tk detecta genes marcadores en los MAGs y evalúa si contienen suficiente información para ser clasificados.
- La carpeta `align` contiene los alineamientos de genes marcadores usados para ubicar los MAGs dentro del marco filogenético de GTDB.
- La carpeta `classify` contiene archivos relacionados con la asignación taxonómica y la ubicación de los genomas en el árbol de referencia de GTDB.
- El archivo `gtdbtk.bac120.summary.tsv` contiene la clasificación taxonómica de los MAGs bacterianos. Este suele ser el archivo principal a analizar.
- El archivo `gtdbtk.ar53.summary.tsv` contiene la clasificación taxonómica de MAGs arqueanos, si hay arqueas entre los genomas analizados.
- El archivo `gtdbtk.log` registra información general de la ejecución, incluyendo comandos, rutas usadas, progreso del análisis y tiempo de ejecución.
- El archivo `gtdbtk.warnings.log` contiene advertencias generadas durante el análisis. Es importante revisarlo, especialmente si algunos MAGs no fueron clasificados o si hubo problemas con genes marcadores, contaminación o información insuficiente.

