# Selección de MAGs representativos usando dRep

Durante el ensamblaje independiente de cada muestra, es común reconstruir MAGs muy similares en diferentes muestras. Esta redundancia debe resolverse antes de estimar la abundancia de los MAGs en las muestras metagenómicas. Si no se elimina, los reads pueden mapear contra varios MAGs similares, lo que reduce la precisión del mapeo y puede generar estimaciones de abundancia artificialmente bajas, ya que los reads se distribuyen entre genomas redundantes en lugar de asignarse a un único genoma representativo.

## Descripción general de dRep

Para eliminar la redundancia en el conjunto de MAGs que pasaron los filtros de calidad, se usará **dRep**, una herramienta que agrupa genomas altamente similares y selecciona el mejor representante de cada grupo. En este contexto, se busca conservar un MAG representativo por especie, considerando como especie operacional a los MAGs que comparten al menos 95% de ANI. El MAG representativo será aquel con mejor calidad dentro de cada grupo, es decir, con mayor completitud y menor contaminación, para ser usado en los análisis posteriores.

## Configuración de directorios de salida

Cree una nueva carpeta llamada `mags_drep` y, dentro de ella, una subcarpeta llamada `drep_out`. En este directorio se guardarán los archivos de entrada necesarios para ejecutar dRep, así como los resultados generados durante el proceso de dereplicación.

```bash
mkdir -p mags_drep/drep_out
```

La estructura inicial será:

```bash
mags_drep/
└── drep_out/
```

## Generar los archivos de entrada requeridos

Para ejecutar el flujo de dereplicación con dRep se necesitan dos archivos principales. El primero es un archivo de texto con las rutas de los MAGs que serán procesados. El segundo es un archivo `.csv` con la información de completitud y contaminación de cada MAG que se estimó anteriormente utilizado `checkM2`.

### Archivo con las rutas de los MAGs

dRep puede recibir directamente una lista de genomas usando comodines, por ejemplo `MAGs_folder/*.fa`. Sin embargo, en este taller se usará un archivo de texto con la ruta completa de cada MAG. Esta opción es más robusta y evita problemas cuando se trabaja con muchos archivos.

Los MAGs que se usarán son aquellos que pasaron los filtros de calidad en los pasos anteriores. Para generar el archivo con las rutas de los MAGs, ejecute el siguiente comando dentro del directorio `mags_drep`:

```bash
ls -1 -d /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/bins_qc/MAGs_pass_qc/*.fa > mags_path_file.txt
```

Revise el archivo generado con:

```bash
head mags_path_file.txt
```

El archivo debe contener una ruta por línea, por ejemplo:

```bash
/ruta/a/MAGs_pass_qc/SRR17048902_01.fa
/ruta/a/MAGs_pass_qc/SRR17048902_02.fa
/ruta/a/MAGs_pass_qc/SRR17048902_03.fa
```

### Archivo con información de calidad de los MAGs

dRep utiliza las métricas de completitud y contaminación para seleccionar el genoma de mejor calidad dentro de cada grupo de MAGs similares. Aunque dRep puede calcular estas métricas directamente con `CheckM`, en este taller se usarán los valores obtenidos previamente con `CheckM2`, ya que estos fueron generados durante el control de calidad de los MAGs.

Para esto, se debe preparar un archivo separado por comas (`.csv`) con tres columnas: `genome`, `completeness` y `contamination`. La columna `genome` debe contener el nombre del archivo del MAG, incluyendo la extensión .fa, y las columnas `completeness` y `contamination` deben contener los valores reportados por CheckM2.

El archivo debe tener una estructura como esta:

```csv
genome,completeness,contamination
SRR17048902_01.fa,95.4,1.2
SRR17048902_02.fa,87.6,3.5
SRR17048902_03.fa,62.1,4.8
```

Para generar el archivo `genome_info_file.csv`, se utilizará el script `generate_genome_info_file.sh`, disponible en la carpeta `helper_scripts`. Copie este script dentro de su carpeta `mags_drep`:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/helper_scripts/generate_genome_info_file.sh mags_drep/
```
Antes de ejecutarlo, abra el script y verifique que la variable `input_file` apunte al archivo `gunc_and_checkm2_output_pass.csv` generado en el paso anterior de control de calidad:

Luego ejecute el script:

```bash
bash generate_genome_info_file.csv
```

Revise que el archivo se haya generado correctamente:

```bash
head generate_genome_info_file.csv
```

El archivo `genome_info_file.csv` será usado por dRep mediante la opción `--genomeInfo`.


## Crear y ejecutar el script para correr dRep

Para ejecutar dRep, cree un script llamado `run_drep.sh`:

```bash
nano run_drep.sh
```

Copie el siguiente contenido y modifique las rutas de `MAGs_path_file` y `genome_info_file` según corresponda:

```bash
#!/bin/bash

#SBATCH -J drep
#SBATCH -D .
#SBATCH -e drep_%j.err
#SBATCH -o drep_%j.out
#SBATCH --cpus-per-task=6
#SBATCH --time=1:00:00	
#SBATCH --mem=10000

source /hpcfs/home/cursos/metagenomica_moderna/conda/bin/activate
conda activate drep

MAGs_path_file="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_drep/MAGs_path_file.txt"
genome_info_file="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_drep/genome_info_file.csv"

dRep dereplicate ./drep_out -g $MAGs_path_file -p 6 -comp 50 -con 5 --S_ani 0.95 --cov_thresh 0.30 --S_algorithm fastANI --genomeInfo $genome_info_file

```

Este script ejecuta dRep usando 6 CPUs. Primero filtra los MAGs con una completitud mínima de 50% y una contaminación máxima de 5%. Luego agrupa los genomas similares usando `fastANI`, con un umbral de ANI de 95%. Además, requiere una cobertura mínima de alineamiento de 30% para considerar válida la comparación entre genomas.

Después de crear y guardar el script, dele permisos de ejecución:

```bash
chmod +x run_drep.sh
```

Luego envíelo al clúster:

```bash
sbatch run_drep.sh
```

## Descripción de la salida

Cuando termine el proceso de dereplicación, la carpeta `drep_out` tendrá una estructura similar a esta:

```bash
drep_out/
├── data_tables/
├── dereplicated_genomes/
├── figures/
└── log/
```

- La carpeta `data_tables` contiene tablas resumen relacionadas con la calidad de los genomas, los grupos formados y las comparaciones entre pares de MAGs.
- La carpeta `dereplicated_genomes` contiene los genomas representativos seleccionados por dRep. Estos son los MAGs no redundantes que se usarán en los análisis posteriores.
- La carpeta `figures` contiene figuras generadas por dRep para visualizar el agrupamiento y la similitud entre genomas.
- La carpeta `log` contiene los archivos de registro del análisis, incluyendo los pasos ejecutados, advertencias y posibles errores.

