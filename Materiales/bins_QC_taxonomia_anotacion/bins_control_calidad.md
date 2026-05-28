# Evaluación de calidad de MAGs

## Descripción general

Evaluar la calidad de los genomas ensamblados a partir de metagenomas, conocidos como MAGs o bins, es un paso fundamental antes de usarlos en análisis posteriores. Esta evaluación permite identificar bins con baja completitud, alta contaminación o posibles señales de quimerismo.

En este taller se utilizarán dos herramientas principales: **CheckM2** y **GUNC**.

**CheckM2** estima la completitud y la contaminación de los MAGs. A diferencia de CheckM, no depende únicamente de conjuntos fijos de genes marcadores, sino que usa modelos de aprendizaje automático. Esto puede mejorar la evaluación de genomas pertenecientes a grupos taxonómicos poco representados o con características inusuales.

**GUNC** permite detectar posibles MAGs quiméricos o con contaminación taxonómica. Para esto, evalúa inconsistencias filogenéticas dentro del genoma. Un MAG de buena calidad debería representar un genoma coherente, no una mezcla de secuencias provenientes de distintos organismos.

## Crear las carpetas de salida

Primero, creee una carpeta llamada `MAGs_qc`. Dentro de esta carpeta se guardarán los resultados de CheckM2, GUNC y los MAGs que pasen los filtros de calidad.

La estructura recomendada es:

```bash
MAGs_qc/
├── checkm2_out/   (almacenar los resultados generados por CheckM2)
├── gunc_out/      (almacenar los resultados generados por GUNC)
└── MAGs_pass_qc/  (contendrá los MAGs finales que pasen los filtros de calidad y que podrán usarse en análisis posteriores)
```

Puede crear esta estructura con:

```bash
mkdir -p MAGs_qc
mkdir -p MAGs_qc/checkm2_out
mkdir -p MAGs_qc/gunc_out
mkdir -p MAGs_qc/MAGs_pass_qc
```

## Copiar los bins reconstruidos al directorio de control de calidad

Después de crear la estructura de carpetas, se deben copiar los bins reconstruidos y refinados a partir de todas las muestras dentro del directorio `MAGs_qc`. Estos bins se encuentran en la siguiente ruta:

```bash
/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/all_bins
```

Para copiarlos a su directorio de control de calidad, use el siguiente comando:

```bash
cp -r /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/all_bins MAGs_qc
```

Después de ejecutar este comando, dentro de `MAGs_qc` quedará una copia de la carpeta `all_bins`, que contiene los bins reconstruidos a partir de todas las muestras. Esta carpeta será usada como entrada para los análisis de calidad con CheckM2 y GUNC.

La estructura del directorio quedaría así:

```bash
MAGs_qc/
├── all_bins/
├── checkm2_out/
├── gunc_out/
└── MAGs_pass_qc/
```

## Ejecutar GUNC y CheckM2

Para evaluar la calidad de los MAGs se utilizarán dos herramientas: **GUNC** y **CheckM2**. Cada una se ejecutará mediante un script de bash independiente.

Antes de ejecutar los scripts, modifique la variable `MAGs_folder` con la ruta completa a la carpeta `all_bins` dentro de su carpeta personal. Esta carpeta contiene los bins reconstruidos a partir de todas las muestras y será usada como entrada para el control de calidad.

## Script para ejecutar GUNC

Cree un archivo llamado `run_gunc.sh`:

```bash
nano run_gunc.sh
```

Copie el siguiente contenido:

```bash
#!/bin/bash

#SBATCH -J gunc
#SBATCH -D .
#SBATCH -e gunc_%j.err
#SBATCH -o gunc_%j.out
#SBATCH --cpus-per-task=8
#SBATCH --time=6:00:00	
#SBATCH --mem=18000	

source /hpcfs/home/cursos/metagenomica_moderna/conda/bin/activate
conda activate gunc

MAGs_folder="/hpcfs/home/cursos/metagenomica_moderna/estudiantes/carpeta_peronal/MAGs_qc/all_bins"

gunc run -d $MAGs_folder -o gunc_out -e .fa -t 8 --db_file /hpcfs/shared/bcem/databases/gunc/gunc_db_progenomes2.1.dmnd
```

Este script evalúa los MAGs con GUNC y guarda los resultados en la carpeta `gunc_out`.

## Script para ejecutar CheckM2

Cree un archivo llamado `run_checkm2.sh`:

```bash
nano run_checkm2.sh
```

Copie el siguiente contenido:

```bash
#!/bin/bash

#SBATCH -J checkm2
#SBATCH -D .
#SBATCH -e checkm2_%j.err
#SBATCH -o checkm2_%j.out
#SBATCH --cpus-per-task=8
#SBATCH --time=6:00:00	
#SBATCH --mem=22000	

source /hpcfs/home/cursos/metagenomica_moderna/conda/bin/activate
conda activate checkm2

MAGs_folder=""/hpcfs/home/cursos/metagenomica_moderna/estudiantes/carpeta_peronal/MAGs_qc/all_bins""

checkm2 predict --threads 8 --input $MAGs_folder -x .fa --output-directory checkm2_out --remove_intermediates
```

Este script estima la completitud y contaminación de cada MAG usando CheckM2. Los resultados se guardarán en la carpeta `checkm2_out`.

## Dar permisos y enviar los trabajos al clúster

Después de crear los scripts, se necesita dar permisos de ejecución:

```bash
chmod +x run_gunc.sh
chmod +x run_checkm2.sh
```

Luego envie los jobs al clúster con `sbatch`:

```bash
sbatch run_gunc.sh
sbatch run_checkm2.sh
```

Puede revisar el estado de los trabajos con:

```bash
squeue -u $USER
```

## Archivos de salida esperados

Cuando ambos procesos terminen, la carpeta `MAGs_qc` debería tener una estructura similar a esta:

```bash
MAGs_qc/
├── checkm2_out/
│   ├── checkm2.log
│   └── quality_report.tsv
│
├── gunc_out/
│   ├── diamond_output/
│   ├── gene_calls/
|   └── GUNC.progenomes_2.1.maxCSS_level.tsv
|
├── all_bins/
└── MAGs_pass/
```

- El archivo `checkm2.log` contiene información sobre la ejecución de CheckM2, incluyendo parámetros, progreso del análisis y posibles errores.
- El archivo `quality_report.tsv` resume la calidad de cada MAG. Las columnas más importantes son `Name`, `Completeness` y `Contamination`.
- La carpeta `diamond_output/` contiene resultados intermedios generados por DIAMOND, que GUNC utiliza para la clasificación taxonómica y la detección de inconsistencias.
- La carpeta `gene_calls/` contiene las secuencias génicas predichas a partir de los MAGs, las cuales son usadas por GUNC para evaluar la consistencia filogenética.
- El archivo `GUNC.progenomes_2.1.maxCSS_level.tsv` resume los resultados principales de GUNC. Una de las columnas más importantes es `pass.GUNC`, que indica si el MAG pasó o no los filtros de GUNC.

## Obtener los MAGs que pasan los filtros de calidad

El conjunto final de MAGs curados incluirá únicamente aquellos que cumplan estos criterios:

```text
pass.GUNC == True
Completeness >= 50
Contamination <= 5
```

Estos filtros permiten conservar MAGs con calidad media a alta para análisis posteriores, reduciendo el riesgo de incluir genomas incompletos, contaminados o potencialmente quiméricos.

Para combinar los resultados de CheckM2 y GUNC, puede usar el script `get_mags_passed_qc.py`, ubicado en:

```bash
/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/helper_scripts/
```

Copie este script dentro de la carpeta `MAGs_qc/`:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/helper_scripts/get_mags_passed_qc.py MAGs_qc
```

Abra el script:

```bash
nano concat_and_filter.py
```

Modifique las siguientes variables con las rutas correctas:

```python
checkm2_output_path = "/ruta/a/checkm2_out/quality_report.tsv"
gunc_output_path = "/ruta/a/gunc_out/GUNC.progenomes_2.1.maxCSS_level.tsv"
mag_source_dir = "/ruta/a/la/carpeta/all_bins/"
destination_dir = "/ruta/a/MAGs_pass/"
```

Después, active el ambiente de Python correspondiente y ejecuta el script:

```bash
conda activate python-env
python get_mags_passed_qc.py
```

Este script genera un archivo llamado `gunc_and_checkm2_output_pass.csv`. Este archivo contiene la información de CheckM2 y GUNC solo para los MAGs que pasaron los filtros de calidad. Además, el script busca los archivos `.fa` correspondientes a esos MAGs en las carpeta `all_bins` y los copia en la carpeta `MAGs_pass`.

