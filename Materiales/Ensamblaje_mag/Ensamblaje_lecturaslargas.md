# Tutorial: Ensamblaje de lecturas largas con nf-core/mag

# nf-core/mag

`nf-core/mag` es un pipeline bioinformático desarrollado dentro de la comunidad **nf-core** para el análisis reproducible de metagenomas. El pipeline está diseñado para realizar ensamblaje, binning y anotación de metagenomas a partir de lecturas cortas, lecturas largas o datos híbridos. En términos generales, permite pasar desde archivos FASTQ hasta ensamblajes, bins metagenómicos, evaluación de calidad, clasificación taxonómica, anotación y reportes integrados.

El flujo completo de `nf-core/mag` versión 5.4.2:

![Flujo de trabajo de nf-core/mag](https://raw.githubusercontent.com/nf-core/mag/5.4.2//docs/images/mag_metromap_light.png)

Fuente: página oficial de `nf-core/mag` versión 5.4.2.

En la imagen se observa que el pipeline completo puede ir desde el preprocesamiento de lecturas cortas y largas hasta ensamblaje, binning, refinamiento, evaluación de calidad, clasificación taxonómica, anotación y reporte final. En nuestro caso, solo seguiremos la ruta inicial de ensamblaje con **FLYE** y evaluación con **QUAST/metaQUAST**.

# Tutorial

## 1. Objetivo del tutorial

En este tutorial se realizará el **ensamblaje de lecturas largas** usando el pipeline **nf-core/mag**.

El objetivo es ejecutar únicamente la etapa de ensamblaje con **FLYE** y evaluar la calidad del ensamblaje con **QUAST/metaQUAST**. En este ejercicio no se realizará binning, refinamiento de bins, clasificación taxonómica de MAGs ni anotación.

---

## 2. Ingreso al cluster

Ingrese al cluster de la Universidad de los Andes usando `ssh`.

```bash
ssh metagenomica_moderna@hypatia.uniandes.edu.co
```

La contraseña será compartida por el instructor durante la sesión.

---

## 3. Ubicación de trabajo

Cada estudiante debe trabajar dentro de su carpeta personal.

La ruta general es:

```bash
/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal
```

Debe reemplazar `Carpeta_personal` por el nombre real de su carpeta asignada.

Ingrese a su carpeta personal:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal
```

---

## 4. Ingresar a la carpeta del taller

En el tutorial anterior se creó la carpeta `Taller_Ensamblaje`. Ingrese a esa carpeta:

```bash
cd Taller_Ensamblaje
```

Ahora cree una carpeta específica para lecturas largas:

```bash
mkdir longReads
```

Ingrese a la carpeta:

```bash
cd longReads
```

Dentro de `longReads`, cree dos carpetas:

```bash
mkdir Secuencias
mkdir Data
```

La estructura esperada será:

```text
Taller_Ensamblaje/
└── longReads/
    ├── Secuencias/
    │   ├── ERR3077601.fastq.gz
    │   └── ERR3077910.fastq.gz
    │
    ├── Data/
    │   ├── samplesheet.csv
    │   └── mag.config
    │
    ├── mag.sh
    ├── work/
    ├── singularity_cache/
    └── output_4/
```

Descripción general:

| Carpeta o archivo | Descripción |
|---|---|
| `Secuencias/` | Carpeta donde se guardan los archivos FASTQ de lecturas largas. |
| `Data/` | Carpeta donde se guardan los archivos de configuración: `samplesheet.csv` y `mag.config`. |
| `mag.sh` | Script principal para enviar el job a SLURM. |
| `work/` | Carpeta temporal de trabajo de Nextflow. |
| `singularity_cache/` | Carpeta donde se almacenan los contenedores descargados por Singularity. |
| `output_4/` | Carpeta de salida con los resultados del pipeline. |

---

## 5. Secuencias que se usarán

En este tutorial todos los estudiantes trabajarán con las siguientes secuencias de Oxford Nanopore:

```text
ERR3077601.fastq.gz
ERR3077910.fastq.gz
```

Estas secuencias corresponden a lecturas largas en formato FASTQ comprimido.

---

## 6. Copiar las secuencias

Ingrese a la carpeta `Secuencias` de su espacio de trabajo:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/longReads/Secuencias
```

Copie la primera secuencia:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/longReads/Secuencias/ERR3077601.fastq.gz .
```

Copie la segunda secuencia:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/longReads/Secuencias/ERR3077910.fastq.gz .
```

Al finalizar, revise que los archivos se copiaron correctamente:

```bash
ls -lh
```

Para contar cuántos archivos FASTQ tiene en la carpeta:

```bash
ls *.fastq.gz | wc -l
```

Como en este tutorial se usarán dos muestras de lecturas largas, deberían aparecer dos archivos `.fastq.gz`.

---

## 7. Crear el archivo `samplesheet.csv`

El archivo `samplesheet.csv` le indica a `nf-core/mag` cuáles muestras se van a analizar y dónde se encuentran los archivos FASTQ.

Ingrese a la carpeta `Data`:

```bash
cd ../Data
```

Copie el archivo base:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/longReads/Data/samplesheet.csv .
```

Abra el archivo con `nano`:

```bash
nano samplesheet.csv
```

El archivo debe tener la siguiente estructura:

```csv
sample,run,group,long_reads,long_reads_platform
ERR3077601,0,1,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/longReads/Secuencias/ERR3077601.fastq.gz,OXFORD_NANOPORE
ERR3077910,0,2,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/longReads/Secuencias/ERR3077910.fastq.gz,OXFORD_NANOPORE
```

Debe reemplazar:

```text
Carpeta_personal
```

por el nombre real de su carpeta.

---

## 8. Explicación de las columnas del `samplesheet.csv`

| Columna | Descripción |
|---|---|
| `sample` | Nombre de la muestra. En este caso corresponde al código de la secuencia, por ejemplo `ERR3077601`. |
| `run` | Número de corrida o réplica técnica. En este tutorial se usa `0`. |
| `group` | Grupo de ensamblaje. Si cada muestra se ensambla por separado, cada muestra debe tener un grupo diferente. |
| `long_reads` | Ruta absoluta al archivo FASTQ de lecturas largas. |
| `long_reads_platform` | Plataforma de secuenciación. En este caso se usa `OXFORD_NANOPORE`. |

Ejemplo general:

```csv
sample,run,group,long_reads,long_reads_platform
Muestra1,0,1,/ruta/Muestra1.fastq.gz,OXFORD_NANOPORE
Muestra2,0,2,/ruta/Muestra2.fastq.gz,OXFORD_NANOPORE
```

Es importante que las rutas de `long_reads` apunten a su propia carpeta de estudiante.

Cambie rutas de este tipo:

```text
/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/longReads/Secuencias/
```

por rutas de este tipo:

```text
/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/longReads/Secuencias/
```

Para guardar y salir de `nano`:

```text
Ctrl + X
Y
Enter
```

---

## 9. Crear el archivo `mag.config`

El archivo `mag.config` permite controlar el uso de recursos computacionales del pipeline. Aquí se definen memoria, número de CPUs, tiempo máximo por proceso, particiones de SLURM y carpetas temporales de trabajo.

Desde la carpeta `Data`, copie el archivo base:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/longReads/Data/mag.config .
```

Abra el archivo:

```bash
nano mag.config
```

El archivo debe tener una estructura similar a esta:

```groovy
workDir = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/longReads/work'

singularity {
  enabled     = true
  autoMounts  = true
  cacheDir    = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/longReads/singularity_cache'
  pullTimeout = '12h'
}

executor {
  queueSize       = 3
  submitRateLimit = '3/1min'
}

params {
  /*
   * Como no haremos binning ni evaluación de MAGs,
   * apagamos explícitamente herramientas de bin QC.
   */
  run_busco   = false
  run_checkm  = false
  run_checkm2 = false
}

process {
  executor = 'slurm'

  errorStrategy = 'retry'
  maxRetries    = 2

  shell = ['/bin/bash', '-euo', 'pipefail']

  /*
   * Recursos base para procesos pequeños
   */
  cpus   = 2
  memory = 8.GB
  time   = 4.h
  queue  = 'short'

  withLabel: process_single {
    cpus   = 1
    memory = 4.GB
    time   = 4.h
    queue  = 'short'
  }

  withLabel: process_low {
    cpus   = 2
    memory = 8.GB
    time   = 6.h
    queue  = 'short'
  }

  withLabel: process_medium {
    cpus   = 8
    memory = 32.GB
    time   = 24.h
    queue  = 'medium'
  }

  withLabel: process_high {
    cpus   = 16
    memory = 120.GB
    time   = 72.h
    queue  = 'long'
  }

  withLabel: process_long {
    cpus   = 16
    memory = 120.GB
    time   = 96.h
    queue  = 'long'
  }

  /*
   * Ensamblaje de lecturas largas con Flye
   * Este será el ensamblador activo.
   */
  withName: '.*FLYE.*' {
    cpus     = 8
    memory   = 80.GB
    time     = 96.h
    queue    = 'long'
    maxForks = 1
  }

  /*
   * Evaluación del ensamblaje con QUAST / metaQUAST
   * No usar --skip_quast en el job.
   */
  withName: '.*QUAST.*' {
    cpus     = 4
    memory   = 24.GB
    time     = 24.h
    queue    = 'medium'
    maxForks = 1
  }

  /*
   * Reporte final MultiQC
   */
  withName: '.*MULTIQC.*' {
    cpus   = 2
    memory = 8.GB
    time   = 4.h
    queue  = 'short'
  }

  /*
   * NanoPlot inicial.
   * No es esencial para el ensamblaje, pero puede generar reportes iniciales.
   * Si se desea que no detenga el flujo en caso de error, se puede usar errorStrategy = 'ignore'.
   */
  withName: '.*NANOPLOT.*' {
    cpus          = 1
    memory        = 16.GB
    time          = 8.h
    queue         = 'short'
    maxRetries    = 0
    errorStrategy = 'ignore'
    maxForks      = 1
  }
}
```

---

## 10. Modificar rutas en `mag.config`

Cada estudiante debe modificar las rutas de `workDir` y `cacheDir`.

Cambie esta línea:

```groovy
workDir = '/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/longReads/work'
```

por:

```groovy
workDir = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/longReads/work'
```

También cambie esta línea:

```groovy
cacheDir = '/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/longReads/singularity_cache'
```

por:

```groovy
cacheDir = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/longReads/singularity_cache'
```

Estas rutas son importantes porque Nextflow necesita escribir archivos temporales, logs, contenedores y archivos intermedios. Por esta razón, `workDir` y `cacheDir` deben estar en una carpeta donde el estudiante tenga permisos de escritura.

Para guardar y salir de `nano`:

```text
Ctrl + X
Y
Enter
```

---

## 11. Copiar el job principal

Una vez configurados los archivos anteriores, regrese desde `Data` hacia `longReads`:

```bash
cd ../
```

Copie el job base:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/longReads/mag.sh .
```

Abra el archivo:

```bash
nano mag.sh
```

El archivo debe tener una estructura similar a esta:

```bash
#!/bin/bash

#SBATCH --job-name=flye_quast
#SBATCH -p long
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=8
#SBATCH --mem=80G
#SBATCH --time=4-00:00:00
#SBATCH --mail-user=jf.meza@uniandes.edu.co
#SBATCH --mail-type=ALL
#SBATCH -o flye_quast.o%j
#SBATCH -e flye_quast.e%j


module load jdk/19.0.2
module load singularity/3.7.1
module load nextflow/25.04.8
hash -r

nextflow run nf-core/mag -r 5.4.1 \
  -resume \
  -profile singularity \
  -c /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/longReads/Data/mag.config \
  --input /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/longReads/Data/samplesheet.csv \
  --outdir /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/longReads/output_4 \
  --skip_longread_qc \
  --skip_spades \
  --skip_spadeshybrid \
  --skip_megahit \
  --skip_metamdbg \
  --skip_ale \
  --skip_binning \
  --skip_binqc \
  --skip_gtdbtk \
  --skip_prodigal \
  --skip_prokka \
  --skip_metaeuk
```

Cada estudiante debe modificar las rutas de:

```bash
-c /ruta/a/mag.config
```

y:

```bash
--input /ruta/a/samplesheet.csv
```

para que apunten a su propia carpeta personal.

También debe revisar la ruta de salida:

```bash
--outdir /ruta/a/output_4
```

En este tutorial se implementa únicamente **Flye** como ensamblador de lecturas largas. Por esta razón, se saltan otros ensambladores como MEGAHIT, SPAdes, SPAdesHybrid y MetaDBG.

Además, se saltan las etapas posteriores de binning, evaluación de bins, clasificación taxonómica de MAGs y anotación.

---

## 12. Ejecutar el job

Desde la carpeta `longReads`, envíe el job a SLURM:

```bash
sbatch mag.sh
```

Para revisar el estado del job:

```bash
squeue -u metagenomica_moderna
```

También puede revisar un job específico:

```bash
squeue -j JOBID
```

Debe reemplazar `JOBID` por el número real de su job.

---

## 13. Revisar archivos de salida y error

Durante la ejecución, SLURM generará archivos de salida y error similares a:

```text
flye_quast.oJOBID
flye_quast.eJOBID
```

Puede revisarlos con:

```bash
less -S flye_quast.oJOBID
```

o:

```bash
less -S flye_quast.eJOBID
```

También puede revisar el log principal de Nextflow:

```bash
less -S .nextflow.log
```

---

## 14. Estructura esperada de resultados

Cuando el pipeline termine, se generará una carpeta de salida llamada:

```text
output_4
```

Para ingresar:

```bash
cd output_4
```

Liste el contenido:

```bash
ls
```

La estructura general esperada es:

```text
output_4/
├── Assembly/
├── QC_longreads/
├── multiqc/
└── pipeline_info/
```

Descripción general:

| Carpeta | Descripción |
|---|---|
| `Assembly/` | Contiene los ensamblajes generados por Flye y los reportes de calidad del ensamblaje. |
| `QC_longreads/` | Contiene reportes iniciales asociados a las lecturas largas. |
| `multiqc/` | Contiene el reporte integrado de MultiQC. |
| `pipeline_info/` | Contiene información técnica de la ejecución del pipeline. |

---

## 15. Resultados de Flye

Ingrese a la carpeta de ensamblaje:

```bash
cd Assembly
```

Revise su contenido:

```bash
ls
```

Debe aparecer una carpeta llamada:

```text
FLYE
```

Ingrese a ella:

```bash
cd FLYE
```

Liste el contenido:

```bash
ls
```

Ejemplo de salida esperada:

```text
FLYE-ERR3077601.assembly.fasta.gz
FLYE-ERR3077601.assembly_graph.gfa.gz
FLYE-ERR3077601.flye.log
FLYE-ERR3077910.assembly.fasta.gz
FLYE-ERR3077910.assembly_graph.gfa.gz
FLYE-ERR3077910.flye.log
QC
```

Los archivos más importantes son:

| Archivo | Descripción |
|---|---|
| `FLYE-<muestra>.assembly.fasta.gz` | Archivo FASTA comprimido con los contigs ensamblados por Flye. |
| `FLYE-<muestra>.assembly_graph.gfa.gz` | Grafo de ensamblaje generado por Flye. |
| `FLYE-<muestra>.flye.log` | Log de ejecución de Flye para cada muestra. |
| `QC/` | Carpeta con resultados de evaluación del ensamblaje. |

---

## 16. Revisar la calidad del ensamblaje

Dentro de la carpeta `FLYE`, ingrese a la carpeta `QC`:

```bash
cd QC
```

Liste el contenido:

```bash
ls
```

Cada carpeta corresponde a una muestra.

Ingrese a una de ellas:

```bash
cd ERR3077601
```

Revise los archivos:

```bash
ls
```

En esta carpeta se encuentran las métricas generadas por QUAST/metaQUAST.

Algunas métricas importantes son:

| Métrica | Descripción |
|---|---|
| `# contigs` | Número total de contigs generados. |
| `Total length` | Longitud total ensamblada. |
| `Largest contig` | Longitud del contig más largo. |
| `N50` | Longitud mínima de contig necesaria para cubrir el 50% del ensamblaje. |
| `L50` | Número de contigs necesarios para alcanzar el 50% del ensamblaje. |
| `GC (%)` | Porcentaje de contenido GC del ensamblaje. |

Para buscar el resumen principal de QUAST:

```bash
find . -name "report.txt"
```

Si aparece un archivo `report.txt`, puede revisarlo con:

```bash
less -S report.txt
```

---






