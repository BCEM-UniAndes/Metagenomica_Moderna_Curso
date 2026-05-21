# Tutorial: Ensamblaje de lecturas cortas con nf-core/mag

# nf-core/mag

`nf-core/mag` es un pipeline bioinformático desarrollado dentro de la comunidad **nf-core** para el análisis reproducible de metagenomas. El pipeline está diseñado para realizar ensamblaje, binning y anotación de metagenomas a partir de lecturas cortas, lecturas largas o datos híbridos. En términos generales, permite pasar desde archivos FASTQ hasta ensamblajes, bins metagenómicos, evaluación de calidad, clasificación taxonómica, anotación y reportes integrados.

El flujo completo de `nf-core/mag` versión 5.4.2:

![Flujo de trabajo de nf-core/mag](https://raw.githubusercontent.com/nf-core/mag/5.4.2//docs/images/mag_metromap_light.png)

Fuente: página oficial de `nf-core/mag` versión 5.4.2.

En la imagen se observa que el pipeline completo puede ir desde el preprocesamiento de lecturas cortas y largas hasta ensamblaje, binning, refinamiento, evaluación de calidad, clasificación taxonómica, anotación y reporte final. En nuestro caso, solo seguiremos la ruta inicial de ensamblaje con **MEGAHIT** y evaluación con **QUAST/metaQUAST**.

# Tutorial

## 1. Objetivo del tutorial

En este tutorial se realizará el **ensamblaje de lecturas cortas paired-end** usando el pipeline **nf-core/mag**.

El objetivo es ejecutar únicamente la etapa de ensamblaje con **MEGAHIT** y evaluar la calidad del ensamblaje con **QUAST/metaQUAST**. En este ejercicio no se realizará binning, refinamiento de bins, clasificación taxonómica de MAGs ni anotación. Además, se trabajará con lecturas cortas que ya pasaron por remoción de hospedero. Por esta razón, se saltarán los pasos de control de calidad y preprocesamiento de lecturas cortas dentro del pipeline.

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

## 4. Crear estructura de carpetas

Dentro de su carpeta personal, cree una carpeta para el taller:

```bash
mkdir Taller_Ensamblaje
```

Ingrese a la carpeta:

```bash
cd Taller_Ensamblaje
```

Cree una carpeta específica para lecturas cortas:

```bash
mkdir shortReads
```

Ingrese a la carpeta:

```bash
cd shortReads
```

Dentro de `shortReads`, cree dos carpetas:

```bash
mkdir Secuencias
mkdir Data
```

La estructura esperada será:

```text
Taller_Ensamblaje/
└── shortReads/
    ├── Secuencias/
    │   ├── muestra_1_forward.fastq.gz
    │   ├── muestra_1_reverse.fastq.gz
    │   ├── muestra_2_forward.fastq.gz
    │   └── muestra_2_reverse.fastq.gz
    │
    ├── Data/
    │   ├── samplesheet.csv
    │   └── mag.config
    │
    ├── mag.sh
    ├── work/
    ├── singularity_cache/
    └── output_3/
```

Descripción general:

| Carpeta o archivo | Descripción |
|---|---|
| `Secuencias/` | Carpeta donde se guardan los archivos FASTQ asignados a cada estudiante. |
| `Data/` | Carpeta donde se guardan los archivos de configuración: `samplesheet.csv` y `mag.config`. |
| `mag.sh` | Script principal para enviar el job a SLURM. |
| `work/` | Carpeta temporal de trabajo de Nextflow. |
| `singularity_cache/` | Carpeta donde se almacenan los contenedores descargados por Singularity. |
| `output_3/` | Carpeta de salida con los resultados del pipeline. |

---

## 5. Secuencias asignadas

Cada estudiante trabajará con dos muestras paired-end.

| Estudiante | Muestra 1 | Muestra 2 |
|---|---|---|
| Rodriguez Alvarado, Lina Daniela | SRR17048924 | SRR17048974 |
| Agudelo, Sergio | SRR17049011 | SRR17049018 |
| Bernal Zarate, María Paula | SRR17048933 | SRR17048978 |
| Bonilla Torres, Rafaela | SRR17048983 | SRR17048902 |
| Diaz Ramirez, Maria Ximena | SRR17048994 | SRR17049021 |
| Duarte Romero, Yeimi Valentina | SRR17048995 | SRR17048980 |
| Floréz Gamba, Diana Carolina | SRR17048895 | SRR17048957 |
| García Catiblanco, Sebastián | SRR17048990 | SRR17049013 |
| Huerfano Santos, Lina Paola | SRR17048922 | SRR17048973 |
| León Jiménez, Ingri Vanesa | SRR17048892 | SRR17048904 |
| Lopez Ramirez, Gina Pilar | SRR17048899 | SRR17048898 |
| Pedraza Herrera, Luz Adriana | SRR17048969 | SRR17048982 |
| Perez Mejia, Julian Andres | SRR17048929 | SRR17048958 |
| Pérez Rubiano, Claudia Constanza | SRR17048893 | SRR17048896 |
| Redondo Gonzalez, Marilin Yohandra | SRR17048984 | SRR17048921 |

Cada muestra tiene dos archivos paired-end:

```text
CodigoID_run0_host_removed.unmapped_1.fastq.gz
CodigoID_run0_host_removed.unmapped_2.fastq.gz
```

El archivo terminado en `_1.fastq.gz` corresponde a la lectura **forward**.

El archivo terminado en `_2.fastq.gz` corresponde a la lectura **reverse**.

---

## 6. Copiar las secuencias asignadas

Ingrese a la carpeta `Secuencias` de su espacio de trabajo:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/Secuencias
```

Para copiar una muestra, use la siguiente estructura general:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/shortReads/Secuencias/CodigoID_run0_host_removed.unmapped_1.fastq.gz .
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/shortReads/Secuencias/CodigoID_run0_host_removed.unmapped_2.fastq.gz .
```

Debe reemplazar `CodigoID` por el código real de su muestra.

Por ejemplo, si su muestra es `SRR17048892`, debe ejecutar:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/shortReads/Secuencias/SRR17048892_run0_host_removed.unmapped_1.fastq.gz .
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/shortReads/Secuencias/SRR17048892_run0_host_removed.unmapped_2.fastq.gz .
```

Si tiene dos muestras, debe repetir el mismo procedimiento para la segunda muestra.

Al finalizar, revise que los archivos se copiaron correctamente:

```bash
ls -lh
```

Para contar cuántos archivos FASTQ tiene en la carpeta:

```bash
ls *.fastq.gz | wc -l
```

Como cada estudiante tiene dos muestras paired-end, deberían aparecer cuatro archivos `.fastq.gz`.

---

## 7. Crear el archivo `samplesheet.csv`

El archivo `samplesheet.csv` le indica a `nf-core/mag` cuáles muestras se van a analizar y dónde se encuentran los archivos FASTQ.

Ingrese a la carpeta `Data`:

```bash
cd ../Data
```

Copie el archivo base:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/shortReads/Data/samplesheet.csv .
```

Abra el archivo con `nano`:

```bash
nano samplesheet.csv
```

El archivo debe tener la siguiente estructura:

```csv
sample,group,short_reads_1,short_reads_2,long_reads,short_reads_platform
SRR17048924,1,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/Secuencias/SRR17048924_run0_host_removed.unmapped_1.fastq.gz,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/Secuencias/SRR17048924_run0_host_removed.unmapped_2.fastq.gz,,ILLUMINA
SRR17048974,2,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/Secuencias/SRR17048974_run0_host_removed.unmapped_1.fastq.gz,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/Secuencias/SRR17048974_run0_host_removed.unmapped_2.fastq.gz,,ILLUMINA
```

Debe reemplazar `Carpeta_personal` por el nombre real de su carpeta.

También debe reemplazar los códigos de muestra por los códigos asignados.

---

## 8. Explicación de las columnas del `samplesheet.csv`

| Columna | Descripción |
|---|---|
| `sample` | Nombre de la muestra. Debe coincidir con el código de la secuencia, por ejemplo `SRR17048924`. |
| `group` | Grupo de ensamblaje. Si cada muestra se ensambla por separado, cada muestra debe tener un grupo diferente. |
| `short_reads_1` | Ruta absoluta al archivo forward `_1.fastq.gz`. |
| `short_reads_2` | Ruta absoluta al archivo reverse `_2.fastq.gz`. |
| `long_reads` | Se deja vacío porque en este tutorial solo se usan lecturas cortas. |
| `short_reads_platform` | Plataforma de secuenciación. En este caso se usa `ILLUMINA`. |

Ejemplo para dos muestras ensambladas por separado:

```csv
sample,group,short_reads_1,short_reads_2,long_reads,short_reads_platform
Muestra1,1,/ruta/Muestra1_1.fastq.gz,/ruta/Muestra1_2.fastq.gz,,ILLUMINA
Muestra2,2,/ruta/Muestra2_1.fastq.gz,/ruta/Muestra2_2.fastq.gz,,ILLUMINA
```

Es importante que las rutas de `short_reads_1` y `short_reads_2` apunten a su propia carpeta de estudiante.

Por ejemplo, debe cambiar rutas de este tipo:

```text
/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/shortReads/Secuencias/
```

por rutas de este tipo:

```text
/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/Secuencias/
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
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/shortReads/Data/mag.config .
```

Abra el archivo:

```bash
nano mag.config
```

El archivo debe tener una estructura similar a esta:

```groovy
workDir = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/work'

singularity {
  enabled     = true
  autoMounts  = true
  cacheDir    = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/singularity_cache'
  pullTimeout = '12h'
}

executor {
  queueSize       = 3
  submitRateLimit = '3/1min'
}

params {
  run_busco  = false
  run_checkm = false
  run_checkm2 = false
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
   * Ensamblaje con MEGAHIT
   */
  withName: '.*MEGAHIT.*' {
    cpus     = 16
    memory   = 120.GB
    time     = 96.h
    queue    = 'long'
    maxForks = 1
  }

  /*
   * Evaluación del ensamblaje con QUAST / metaQUAST
   */
  withName: '.*QUAST.*' {
    cpus     = 8
    memory   = 32.GB
    time     = 24.h
    queue    = 'medium'
    maxForks = 4
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
   * FastQC inicial.
   * Se limita el uso de Java para evitar errores de memoria.
   */
  withName: '.*FASTQC.*' {
    cpus     = 1
    memory   = 16.GB
    time     = 8.h
    queue    = 'short'
    maxForks = 1

    beforeScript = '''
      export _JAVA_OPTIONS="-XX:CompressedClassSpaceSize=128m -XX:ReservedCodeCacheSize=64m"
    '''
  }
}
```

---

## 10. Modificar rutas en `mag.config`

Cada estudiante debe modificar las rutas de `workDir` y `cacheDir`.

Cambie esta línea:

```groovy
workDir = '/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/shortReads/work'
```

por:

```groovy
workDir = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/work'
```

También cambie esta línea:

```groovy
cacheDir = '/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/shortReads/singularity_cache'
```

por:

```groovy
cacheDir = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/singularity_cache'
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

Una vez configurados los archivos anteriores, regrese desde `Data` hacia `shortReads`:

```bash
cd ../
```

Copie el job base:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Ensamblaje/shortReads/mag.sh .
```

Abra el archivo:

```bash
nano mag.sh
```

El archivo debe tener una estructura similar a esta:

```bash
#!/bin/bash

#SBATCH --job-name=megahit_quast
#SBATCH -p medium
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=32
#SBATCH --mem=120G
#SBATCH --time=2-00:00:00
#SBATCH --mail-user=jf.meza@uniandes.edu.co
#SBATCH --mail-type=ALL
#SBATCH -o megahit_quast.o%j
#SBATCH -e megahit_quast.e%j


module load jdk/19.0.2
module load singularity/3.7.1
module load nextflow/25.04.8
hash -r

nextflow run nf-core/mag -r 5.4.1 \
  -resume \
  -profile singularity \
  -c /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/Data/mag.config \
  --input /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Ensamblaje/shortReads/Data/samplesheet.csv \
  --outdir output_3 \
  --skip_shortread_qc \
  --skip_spades \
  --skip_spadeshybrid \
  --skip_metamdbg \
  --skip_flye \
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

En este tutorial se implementa únicamente **MEGAHIT** como ensamblador. Por eso se saltan otros ensambladores como SPAdes, SPAdesHybrid, MetaDBG y Flye.

Además, se saltan las etapas posteriores de binning, evaluación de bins, clasificación taxonómica de MAGs y anotación.

---

## 12. Ejecutar el job

Desde la carpeta `shortReads`, envíe el job a SLURM:

```bash
sbatch mag.sh
```

Para revisar el estado del job:

```bash
squeue -u metagenomica_moderna
```

También puede revisar únicamente sus procesos usando el identificador del job:

```bash
squeue -j JOBID
```

Debe reemplazar `JOBID` por el número real de su job.

---

## 13. Revisar archivos de salida y error

Durante la ejecución, SLURM generará archivos de salida y error similares a:

```text
megahit_quast.oJOBID
megahit_quast.eJOBID
```

Puede revisarlos con:

```bash
less -S megahit_quast.oJOBID
```

o:

```bash
less -S megahit_quast.eJOBID
```

También puede revisar el log principal de Nextflow:

```bash
less -S .nextflow.log
```

---

## 14. Estructura esperada de resultados

Cuando el pipeline termine, se generará una carpeta de salida llamada:

```text
output_3
```

Para ingresar:

```bash
cd output_3
```

Liste el contenido:

```bash
ls
```

La estructura general esperada es:

```text
output_3/
├── Assembly/
├── QC_shortreads/
├── multiqc/
└── pipeline_info/
```

Descripción general:

| Carpeta | Descripción |
|---|---|
| `Assembly/` | Contiene los ensamblajes generados por MEGAHIT y los reportes de calidad del ensamblaje. |
| `QC_shortreads/` | Contiene reportes iniciales de calidad asociados a las lecturas cortas. |
| `multiqc/` | Contiene el reporte integrado de MultiQC. |
| `pipeline_info/` | Contiene información técnica de la ejecución del pipeline. |

---

## 15. Resultados de MEGAHIT

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
MEGAHIT
```

Ingrese a ella:

```bash
cd MEGAHIT
```

Liste el contenido:

```bash
ls
```

Ejemplo de salida esperada:

```text
MEGAHIT-SRR17048924.contigs.fa.gz
MEGAHIT-SRR17048924.log
MEGAHIT-SRR17048974.contigs.fa.gz
MEGAHIT-SRR17048974.log
QC
```

Los archivos más importantes son:

| Archivo | Descripción |
|---|---|
| `MEGAHIT-<muestra>.contigs.fa.gz` | Archivo FASTA comprimido con los contigs ensamblados. |
| `MEGAHIT-<muestra>.log` | Log de ejecución de MEGAHIT para cada muestra. |
| `QC/` | Carpeta con resultados de evaluación del ensamblaje. |

---

## 16. Revisar la calidad del ensamblaje

Dentro de la carpeta `MEGAHIT`, ingrese a la carpeta `QC`:

```bash
cd QC
```

Liste el contenido:

```bash
ls
```

Ejemplo:

```text
SRR17048924
SRR17048974
```

Cada carpeta corresponde a una muestra.

Ingrese a una de ellas:

```bash
cd SRR17048924
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

## 17. Interpretación básica de resultados

Al finalizar el análisis, cada estudiante debe identificar:

1. El número de contigs ensamblados por muestra.
2. La longitud total ensamblada.
3. El N50.
4. El contig más largo.
5. Si una muestra tuvo mejor ensamblaje que la otra.

Una forma sencilla de interpretar los resultados es:

```text
Un ensamblaje con mayor N50, mayor longitud total ensamblada y menor número de contigs puede indicar una mejor continuidad del ensamblaje.
```

Sin embargo, en metagenómica, un mayor número de contigs no siempre significa que el ensamblaje sea malo, ya que la muestra puede contener múltiples organismos con diferentes abundancias y coberturas.

---
