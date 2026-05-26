# Tutorial: Binning metagenómico de lecturas largas con nf-core/mag

## 1. nf-core/mag: binning metagenómico

`nf-core/mag` es un pipeline bioinformático desarrollado por la comunidad de nf-core para el análisis reproducible de datos metagenómicos. Este pipeline permite realizar control de calidad, remoción de contaminación, ensamblaje metagenómico, binning, refinamiento de bins, evaluación de calidad, clasificación taxonómica y anotación funcional.

En este tutorial nos enfocaremos en la etapa de **binning metagenómico** a partir de ensamblajes previamente generados con lecturas largas.

El flujo completo de `nf-core/mag` versión 5.4.2 se muestra a continuación:

![Flujo de trabajo de nf-core/mag](https://raw.githubusercontent.com/nf-core/mag/5.4.2//docs/images/mag_metromap_light.png)

Fuente: página oficial de `nf-core/mag` versión 5.4.2.

---

## 2. ¿Qué es el binning metagenómico?

El **binning metagenómico** es el proceso mediante el cual los contigs obtenidos a partir de un ensamblaje metagenómico se agrupan en conjuntos que representan genomas reconstruidos a partir de metagenomas, conocidos como **MAGs** (*Metagenome-Assembled Genomes*).

En un ensamblaje metagenómico, los contigs pueden provenir de diferentes microorganismos presentes en una muestra. El objetivo del binning es separar esos contigs y agruparlos según características como:

- Cobertura de secuenciación.
- Composición de nucleótidos.
- Frecuencia de tetranucleótidos.
- Patrones de abundancia.
- Similitud entre contigs.
- Modelos estadísticos o de aprendizaje automático.

En este tutorial se usarán ensamblajes ya generados con **Flye** a partir de lecturas largas de **Oxford Nanopore**.

Las herramientas principales usadas para el binning serán:

| Herramienta | Descripción general |
|---|---|
| `MetaBAT2` | Agrupa contigs usando cobertura diferencial y composición de tetranucleótidos. |
| `MaxBin2` | Usa modelos probabilísticos basados en composición de secuencia y cobertura para agrupar contigs. |
| `SemiBin2` | Usa aprendizaje semi-supervisado para mejorar la agrupación de contigs en metagenomas. |

Además, se usarán:

| Herramienta | Función |
|---|---|
| `DAS Tool` | Refina y combina los bins generados por diferentes herramientas. |
| `CheckM2` | Evalúa la calidad de los MAGs estimando completitud y contaminación. |

---

## 3. Objetivo del tutorial

Realizar el **binning metagenómico de lecturas largas** usando `nf-core/mag` a partir de ensamblajes precomputados.

En este tutorial se utilizarán:

- Lecturas largas de Oxford Nanopore.
- Ensamblajes metagenómicos generados con `Flye`.
- `nf-core/mag` versión 5.4.2.
- `MetaBAT2`, `MaxBin2` y `SemiBin2` como herramientas de binning.
- `DAS Tool` para refinamiento de bins.
- `CheckM2` para evaluación de calidad de MAGs.

El flujo general del análisis será:

```text
Lecturas largas Oxford Nanopore + ensamblajes Flye
                         ↓
                    nf-core/mag
                         ↓
            Uso de ensamblajes precomputados
                         ↓
          Binning con MetaBAT2, MaxBin2 y SemiBin2
                         ↓
              Refinamiento con DAS Tool
                         ↓
                Evaluación con CheckM2
                         ↓
                    MAGs finales
```

> **Nota importante:** en este tutorial se usarán ensamblajes precomputados mediante `--assembly_input`. Esto permite saltar las etapas de preprocesamiento y ensamblaje, e iniciar el flujo desde la etapa de binning.

---

## 4. Ingreso al cluster

Ingrese al cluster de la Universidad de los Andes usando `ssh`:

```bash
ssh metagenomica_moderna@hypatia.uniandes.edu.co
```

La contraseña será compartida por el instructor durante la sesión.

---

## 5. Ubicación de trabajo

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

## 6. Creación de la estructura de carpetas

Dentro de su carpeta personal, cree una carpeta para el taller, si aún no la ha creado:

```bash
mkdir Taller_Binning
```

Ingrese a la carpeta:

```bash
cd Taller_Binning
```

Cree una carpeta específica para lecturas largas:

```bash
mkdir longReads
```

Ingrese a la carpeta:

```bash
cd longReads
```

Dentro de `longReads`, cree tres carpetas:

```bash
mkdir Ensamblajes
mkdir Data
mkdir Secuencias
```

La estructura esperada será:

```text
Taller_Binning/
└── longReads/
    ├── Ensamblajes/
    │   ├── FLYE-ERR3077601.assembly.fasta.gz
    │   └── FLYE-ERR3077910.assembly.fasta.gz
    │
    ├── Data/
    │   ├── samplesheet_reads.csv
    │   ├── samplesheet_ensamblaje.csv
    │   └── mag.config
    │
    ├── Secuencias/
    │   ├── ERR3077601.fastq.gz
    │   └── ERR3077910.fastq.gz
    │
    └── mag.sh
```

---

## 7. Secuencias asignadas

En este tutorial todos los estudiantes trabajarán con las siguientes secuencias de Oxford Nanopore:

```text
ERR3077601.fastq.gz
ERR3077910.fastq.gz
```

Estas secuencias corresponden a lecturas largas en formato FASTQ comprimido.

---

## 8. Copiar las secuencias asignadas

Ingrese a la carpeta `Secuencias` de su espacio de trabajo:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Secuencias
```

Copie las lecturas largas:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/longReads/Secuencias/ERR3077601.fastq.gz .

cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/longReads/Secuencias/ERR3077910.fastq.gz .
```

Al finalizar, revise que los archivos se copiaron correctamente:

```bash
ls -lh
```

Para contar cuántos archivos FASTQ tiene en la carpeta:

```bash
ls *.fastq.gz | wc -l
```

Deberían aparecer dos archivos `.fastq.gz`.

---

## 9. Copiar los ensamblajes

Ingrese a la carpeta `Ensamblajes` de su espacio de trabajo:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Ensamblajes
```

Copie los ensamblajes generados con `Flye`:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/longReads/Ensamblajes/FLYE-ERR3077601.assembly.fasta.gz .

cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/longReads/Ensamblajes/FLYE-ERR3077910.assembly.fasta.gz .
```

Al finalizar, revise que los archivos se copiaron correctamente:

```bash
ls -lh
```

Para contar los ensamblajes:

```bash
ls *.fasta.gz | wc -l
```

Deberían aparecer dos archivos `.assembly.fasta.gz`.

---

## 10. Crear el archivo `samplesheet_reads.csv`

El archivo `samplesheet_reads.csv` le indica a `nf-core/mag` cuáles muestras se van a analizar y dónde se encuentran los archivos de lecturas largas.

Ingrese a la carpeta `Data`:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Data
```

Copie el archivo base:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/longReads/Data/samplesheet_reads.csv .
```

Abra el archivo con `nano`:

```bash
nano samplesheet_reads.csv
```

El archivo debe tener la siguiente estructura:

```csv
sample,group,short_reads_1,short_reads_2,long_reads,short_reads_platform,long_reads_platform
ERR3077601,0,,,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Secuencias/ERR3077601.fastq.gz,,OXFORD_NANOPORE
ERR3077910,1,,,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Secuencias/ERR3077910.fastq.gz,,OXFORD_NANOPORE
```

Debe modificar:

- `Carpeta_personal` por el nombre real de su carpeta asignada.
- Las rutas si su estructura de carpetas es diferente.

### Descripción de las columnas

| Columna | Descripción |
|---|---|
| `sample` | Nombre o identificador de la muestra. Debe coincidir con el `id` del archivo `samplesheet_ensamblaje.csv`. |
| `group` | Grupo de ensamblaje/binning. En este tutorial cada muestra tendrá un grupo diferente. |
| `short_reads_1` | Vacío, porque en este tutorial no se usan lecturas cortas. |
| `short_reads_2` | Vacío, porque en este tutorial no se usan lecturas cortas paired-end. |
| `long_reads` | Ruta absoluta al archivo FASTQ de lectura larga. |
| `short_reads_platform` | Vacío, porque no se están usando lecturas cortas. |
| `long_reads_platform` | Plataforma de lecturas largas. En este caso se usa `OXFORD_NANOPORE`. |

Para guardar y salir de `nano`:

```text
Ctrl + X
Y
Enter
```

---

## 11. Crear el archivo `samplesheet_ensamblaje.csv`

El archivo `samplesheet_ensamblaje.csv` le indica a `nf-core/mag` cuáles ensamblajes precomputados se usarán para el binning.

Copie el archivo base dentro de la carpeta `Data`:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/longReads/Data/samplesheet_ensamblaje.csv .
```

Abra el archivo con `nano`:

```bash
nano samplesheet_ensamblaje.csv
```

El archivo debe tener la siguiente estructura:

```csv
id,group,assembler,fasta
ERR3077601,0,Flye,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Ensamblajes/FLYE-ERR3077601.assembly.fasta.gz
ERR3077910,1,Flye,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Ensamblajes/FLYE-ERR3077910.assembly.fasta.gz
```

Debe modificar:

- `Carpeta_personal` por el nombre real de su carpeta asignada.
- Las rutas si su estructura de carpetas es diferente.

### Descripción de las columnas

| Columna | Descripción |
|---|---|
| `id` | Identificador del ensamblaje. Debe coincidir con la columna `sample` del archivo `samplesheet_reads.csv`. |
| `group` | Grupo de ensamblaje/binning. Debe coincidir con la columna `group` del archivo `samplesheet_reads.csv`. |
| `assembler` | Ensamblador usado para generar los contigs. En este tutorial se usará `Flye`. |
| `fasta` | Ruta absoluta al archivo FASTA del ensamblaje. Puede estar comprimido en formato `.gz`. |

### Punto importante

El archivo de lecturas y el archivo de ensamblajes deben coincidir en `sample/id` y en `group`.

Ejemplo:

```text
samplesheet_reads.csv              samplesheet_ensamblaje.csv

sample = ERR3077601        →       id = ERR3077601
group  = 0                 →       group = 0

sample = ERR3077910        →       id = ERR3077910
group  = 1                 →       group = 1
```

Para guardar y salir de `nano`:

```text
Ctrl + X
Y
Enter
```

---

## 12. Crear el archivo `mag.config`

El archivo `mag.config` permite controlar el uso de recursos computacionales del pipeline. Aquí se definen memoria, número de CPUs, tiempo máximo por proceso, particiones de SLURM y carpetas temporales de trabajo.

Desde la carpeta `Data`, copie el archivo base:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/longReads/Data/mag.config .
```

Abra el archivo:

```bash
nano mag.config
```

El archivo `mag.config` debe tener una estructura similar a esta:

```groovy
/*
 * mag.config
 * Configuración para nf-core/mag 5.4.2
 * Flujo: ensamblajes precomputados de lecturas largas + binning metagenómico
 * Ensamblador: Flye
 * Binners activos: MetaBAT2, MaxBin2 y SemiBin2
 */

workDir = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/work'

singularity {
  enabled     = true
  autoMounts  = true
  cacheDir    = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/singularity_cache'
  pullTimeout = '12h'
}

executor {
  queueSize       = 3
  submitRateLimit = '3/1min'
}

params {
  run_busco   = false
  run_checkm  = false
  run_checkm2 = true

  skip_spades       = true
  skip_spadeshybrid = true
  skip_megahit      = true

  skip_prokka = true
  skip_metaeuk = true
  skip_gtdbtk  = true

  skip_concoct    = true
  skip_comebin    = true
  skip_metabinner = true

  refine_bins_dastool = true
  postbinning_input   = 'refined_bins_only'

  checkm2_db = '/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/Databases/CheckM2_database/uniref100.KO.1.dmnd'

  save_assembly_mapped_reads = true
}

process {
  executor = 'slurm'

  errorStrategy = 'retry'
  maxRetries    = 2

  shell = ['/bin/bash', '-euo', 'pipefail']

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
    time   = 8.h
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

  withName: '.*BOWTIE2.*' {
    cpus     = 12
    memory   = 64.GB
    time     = 48.h
    queue    = 'medium'
    maxForks = 2
  }

  withName: '.*MINIMAP2.*' {
    cpus     = 12
    memory   = 64.GB
    time     = 48.h
    queue    = 'medium'
    maxForks = 2
  }

  withName: '.*SAMTOOLS.*' {
    cpus     = 8
    memory   = 32.GB
    time     = 24.h
    queue    = 'medium'
    maxForks = 3
  }

  withName: '.*COVERAGE.*|.*JGI.*|.*DEPTH.*' {
    cpus     = 8
    memory   = 32.GB
    time     = 24.h
    queue    = 'medium'
    maxForks = 3
  }

  withName: '.*METABAT.*' {
    cpus     = 12
    memory   = 64.GB
    time     = 48.h
    queue    = 'medium'
    maxForks = 2
  }

  withName: '.*MAXBIN.*' {
    cpus     = 12
    memory   = 80.GB
    time     = 72.h
    queue    = 'long'
    maxForks = 2
  }

  withName: '.*SEMIBIN.*' {
    cpus     = 16
    memory   = 120.GB
    time     = 96.h
    queue    = 'long'
    maxForks = 1
  }

  withName: '.*DASTOOL.*|.*DAS_TOOL.*' {
    cpus     = 12
    memory   = 80.GB
    time     = 72.h
    queue    = 'long'
    maxForks = 2
  }

  withName: '.*CHECKM2.*' {
    cpus     = 16
    memory   = 120.GB
    time     = 96.h
    queue    = 'long'
    maxForks = 1
  }

  withName: '.*QUAST.*' {
    cpus     = 8
    memory   = 32.GB
    time     = 24.h
    queue    = 'medium'
    maxForks = 3
  }

  withName: '.*MULTIQC.*' {
    cpus   = 2
    memory = 8.GB
    time   = 4.h
    queue  = 'short'
  }

  withName: '.*FASTQC.*' {
    cpus     = 1
    memory   = 8.GB
    time     = 4.h
    queue    = 'short'
    maxForks = 2

    beforeScript = '''
      export _JAVA_OPTIONS="-XX:CompressedClassSpaceSize=128m -XX:ReservedCodeCacheSize=64m"
    '''
  }
}
```

Cada estudiante debe modificar las rutas de `workDir` y `cacheDir`.

Cambie esta línea:

```groovy
workDir = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/work'
```

reemplazando `Carpeta_personal` por su carpeta real.

También cambie esta línea:

```groovy
cacheDir = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/singularity_cache'
```

reemplazando `Carpeta_personal` por su carpeta real.

Estas rutas son importantes porque Nextflow necesita escribir archivos temporales, logs, contenedores y archivos intermedios. Por esta razón, `workDir` y `cacheDir` deben estar en una carpeta donde el estudiante tenga permisos de escritura.

Para guardar y salir de `nano`:

```text
Ctrl + X
Y
Enter
```

---

## 13. Copiar el job principal

Una vez configurados los archivos anteriores, regrese desde `Data` hacia `longReads`:

```bash
cd ../
```

Copie el job base:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/longReads/mag.sh .
```

Abra el archivo:

```bash
nano mag.sh
```

El archivo debe tener una estructura similar a esta:

```bash
#!/bin/bash

#SBATCH --job-name=nfcore_longBinning
#SBATCH -p medium
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=18
#SBATCH --mem=120G
#SBATCH --time=8-00:00:00
#SBATCH --mail-user=jf.meza@uniandes.edu.co
#SBATCH --mail-type=ALL
#SBATCH -o nfcore_longBinning_job.o%j
#SBATCH -e nfcore_longBinning_job.e%j

module load jdk/19.0.2
module load singularity/3.7.1
module load nextflow/25.04.8
hash -r

nextflow run nf-core/mag -r 5.4.2 \
  -resume \
  -profile singularity \
  -c /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Data/mag.config \
  --input /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Data/samplesheet_reads.csv \
  --assembly_input /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Data/samplesheet_ensamblaje.csv \
  --outdir output \
  --skip_concoct \
  --skip_comebin \
  --skip_metabinner \
  --skip_metaeuk \
  --skip_gtdbtk \
  --skip_prokka \
  --save_assembly_mapped_reads \
  --run_checkm2 \
  --checkm2_db /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/Databases/CheckM2_database/uniref100.KO.1.dmnd \
  --refine_bins_dastool \
  --postbinning_input refined_bins_only
```

Cada estudiante debe modificar las rutas de:

```bash
-c /ruta/a/mag.config
```

```bash
--input /ruta/a/samplesheet_reads.csv
```

```bash
--assembly_input /ruta/a/samplesheet_ensamblaje.csv
```

para que apunten a su propia carpeta personal.

También debe reemplazar `Carpeta_personal` por el nombre real de su carpeta asignada.

Para guardar y salir de `nano`:

```text
Ctrl + X
Y
Enter
```

---

## 14. Ejecutar el job

Desde la carpeta `longReads`, envíe el job a SLURM:

```bash
sbatch mag.sh
```

Para revisar el estado del job:

```bash
squeue -u metagenomica_moderna
```

También puede revisar únicamente su job usando el identificador del job:

```bash
squeue -j JOBID
```

Debe reemplazar `JOBID` por el número real de su job.

Para revisar los archivos de salida y error del job:

```bash
ls -lh *.o* *.e*
```

Puede visualizar el archivo de salida con:

```bash
less nfcore_longBinning_job.oJOBID
```

Y el archivo de error con:

```bash
less nfcore_longBinning_job.eJOBID
```

Debe reemplazar `JOBID` por el número real de su job.

---

## 15. Revisar el progreso de Nextflow

Durante la ejecución, Nextflow mostrará el progreso de los procesos del pipeline.

También puede revisar el log principal:

```bash
less .nextflow.log
```

Para buscar errores dentro del log:

```bash
grep -i "error" .nextflow.log
```

Para buscar procesos fallidos:

```bash
grep -i "failed" .nextflow.log
```

Si el job se detiene y necesita reanudarlo, el comando del script ya incluye:

```bash
-resume
```

Esto permite que Nextflow continúe desde los procesos completados previamente.

---

## 16. Archivos de salida

Los resultados se guardarán en la carpeta definida con `--outdir`. En este tutorial será:

```bash
output
```

Para ingresar a la carpeta de resultados:

```bash
cd output
```

Para revisar la estructura general:

```bash
ls -lh
```

La estructura puede variar ligeramente según los procesos activados, pero de forma general se esperan carpetas asociadas a:

```text
output/
├── Assembly/
├── GenomeBinning/
├── Pipeline_info/
└── MultiQC/
```

---

## 17. Descripción general de los resultados

### 17.1 `Assembly/`

Esta carpeta contiene información relacionada con los ensamblajes usados por el pipeline.

Como en este tutorial se están usando ensamblajes precomputados mediante `--assembly_input`, el pipeline no vuelve a ensamblar las lecturas. Sin embargo, puede organizar, validar o usar los ensamblajes como entrada para los pasos posteriores.

Aquí se pueden encontrar archivos relacionados con:

- Contigs de entrada.
- Enlaces o copias de ensamblajes.
- Resultados de evaluación de ensamblaje si se ejecutan procesos como QUAST.

---

### 17.2 `GenomeBinning/`

Esta carpeta contiene los resultados principales del binning metagenómico.

En este tutorial se esperan salidas de:

- `MetaBAT2`
- `MaxBin2`
- `SemiBin2`

Cada herramienta genera conjuntos de bins a partir de los contigs ensamblados.

Los archivos más importantes suelen ser los bins en formato FASTA:

```text
*.fa
*.fna
*.fasta
```

Estos archivos representan genomas reconstruidos preliminares a partir de los datos metagenómicos.

Ejemplo conceptual:

```text
GenomeBinning/
├── MetaBAT2/
│   ├── sample1_bin.1.fa
│   ├── sample1_bin.2.fa
│   └── sample1_bin.3.fa
│
├── MaxBin2/
│   ├── sample1.001.fasta
│   ├── sample1.002.fasta
│   └── sample1.003.fasta
│
└── SemiBin2/
    ├── sample1_bin_1.fa
    ├── sample1_bin_2.fa
    └── sample1_bin_3.fa
```

---

### 17.3 Refinamiento con `DAS Tool`

Dentro de la salida de binning también se pueden encontrar resultados asociados a `DAS Tool`.

`DAS Tool` compara los bins generados por diferentes herramientas y selecciona la mejor combinación de contigs para producir un conjunto refinado de MAGs.

En este tutorial, como se usa:

```bash
--refine_bins_dastool
--postbinning_input refined_bins_only
```

los bins refinados serán los más importantes para análisis posteriores.

Los archivos principales serán bins refinados en formato FASTA.

Ejemplo conceptual:

```text
DAS_Tool/
├── sample1_DASTool_bins/
│   ├── sample1_DASTool_bin.1.fa
│   ├── sample1_DASTool_bin.2.fa
│   └── sample1_DASTool_bin.3.fa
│
└── sample1_DASTool_summary.tsv
```

El archivo resumen de `DAS Tool` permite revisar qué bins fueron seleccionados y de qué herramienta provenían inicialmente.

---

### 17.4 Evaluación de calidad con `CheckM2`

Los resultados de evaluación de calidad de los bins o MAGs se generan con `CheckM2`.

En este tutorial se usa:

```bash
--run_checkm2
```

Por lo tanto, se esperan resultados de `CheckM2`.

`CheckM2` estima principalmente:

- Completitud del MAG.
- Contaminación del MAG.
- Calidad general del bin.

Los resultados más importantes suelen estar en archivos `.tsv`.

Ejemplo conceptual:

```text
QC/
└── CheckM2/
    ├── quality_report.tsv
    └── diamond_output/
```

El archivo más importante es generalmente:

```text
quality_report.tsv
```

Este archivo puede contener columnas como:

| Columna | Descripción |
|---|---|
| `Name` | Nombre del bin o MAG evaluado. |
| `Completeness` | Porcentaje estimado de completitud del genoma. |
| `Contamination` | Porcentaje estimado de contaminación. |
| `Quality` | Clasificación o estimación general de calidad. |

Un MAG de buena calidad suele tener alta completitud y baja contaminación.

---

### 17.5 `MultiQC/`

Esta carpeta contiene el reporte integrado generado por `MultiQC`.

El archivo principal suele ser:

```text
multiqc_report.html
```

Este reporte puede abrirse en un navegador web y resume diferentes métricas del pipeline.

Para ubicar el reporte:

```bash
find output -name "multiqc_report.html"
```

---

### 17.6 `Pipeline_info/`

Esta carpeta contiene información sobre la ejecución del pipeline.

Puede incluir:

- Versión del pipeline.
- Comando ejecutado.
- Parámetros usados.
- Reportes de ejecución.
- Archivos de trazabilidad de Nextflow.

Archivos comunes:

```text
execution_report.html
execution_timeline.html
execution_trace.txt
pipeline_dag.html
```

Estos archivos son útiles para revisar:

- Cuánto tiempo tardó cada proceso.
- Cuánta memoria usó cada tarea.
- Qué procesos fueron ejecutados.
- Qué parámetros se usaron en la corrida.

---

## 18. Comandos útiles para explorar resultados

Listar carpetas principales:

```bash
ls -lh output
```

Buscar todos los bins generados:

```bash
find output -name "*.fa"
```

Buscar también archivos FASTA con otras extensiones:

```bash
find output \( -name "*.fa" -o -name "*.fna" -o -name "*.fasta" \)
```

Buscar archivos de CheckM2:

```bash
find output -iname "*checkm2*" -o -iname "*quality_report*"
```

Buscar reportes HTML:

```bash
find output -name "*.html"
```

Buscar archivos `.tsv`:

```bash
find output -name "*.tsv"
```

Contar cuántos bins FASTA se generaron:

```bash
find output \( -name "*.fa" -o -name "*.fna" -o -name "*.fasta" \) | wc -l
```

---

## 19. Interpretación básica de los MAGs

Después de obtener los resultados de `CheckM2`, se pueden clasificar los MAGs según completitud y contaminación.

Una clasificación común es:

| Categoría | Criterio aproximado |
|---|---|
| Alta calidad | Completitud ≥ 90% y contaminación ≤ 5% |
| Calidad media | Completitud ≥ 50% y contaminación ≤ 10% |
| Baja calidad | Completitud < 50% o contaminación alta |

Ejemplo de interpretación:

```text
Un bin con 92% de completitud y 3% de contaminación puede considerarse un MAG de alta calidad.
Un bin con 65% de completitud y 7% de contaminación puede considerarse de calidad media.
Un bin con 35% de completitud no se considera un MAG robusto para análisis genómicos posteriores.
```

---

## 20. Recomendaciones finales

Antes de ejecutar el job, revise cuidadosamente:

1. Que las rutas en `samplesheet_reads.csv` existan.
2. Que las rutas en `samplesheet_ensamblaje.csv` existan.
3. Que `sample` e `id` coincidan entre ambos archivos.
4. Que `group` coincida entre ambos archivos.
5. Que el archivo `mag.config` tenga rutas de `workDir` y `cacheDir` dentro de su carpeta personal.
6. Que el archivo `mag.sh` apunte a su propio `mag.config`, `samplesheet_reads.csv` y `samplesheet_ensamblaje.csv`.
7. Que los archivos FASTQ estén comprimidos como `.fastq.gz`.
8. Que los ensamblajes de Flye estén en formato `.fasta.gz`.

Para validar rutas de lecturas largas:

```bash
ls -lh /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Secuencias/
```

Para validar rutas de ensamblajes:

```bash
ls -lh /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/longReads/Ensamblajes/
```

Para validar los archivos de configuración:

```bash
ls -lh Data/
```

Una vez todo esté correcto, ejecute:

```bash
sbatch mag.sh
```

---

## 21. Resumen del tutorial

En este tutorial se realizó un flujo de binning metagenómico de lecturas largas usando `nf-core/mag`.

Se trabajó con:

- Lecturas largas Oxford Nanopore.
- Ensamblajes generados con `Flye`.
- Archivo `samplesheet_reads.csv`.
- Archivo `samplesheet_ensamblaje.csv`.
- Archivo de configuración `mag.config`.
- Job de SLURM `mag.sh`.

El análisis ejecutó:

- Uso de ensamblajes precomputados.
- Binning con `MetaBAT2`, `MaxBin2` y `SemiBin2`.
- Refinamiento de bins con `DAS Tool`.
- Evaluación de MAGs con `CheckM2`.

Los resultados principales se encuentran en:

```text
output/
```

y los archivos más importantes corresponden a:

- Bins generados por cada herramienta.
- Bins refinados por `DAS Tool`.
- Reportes de calidad de `CheckM2`.
- Reporte integrado de `MultiQC`.
- Archivos de trazabilidad de `Nextflow`.
