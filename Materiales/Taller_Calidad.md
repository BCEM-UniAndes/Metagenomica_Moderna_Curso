# Introducción

En cualquier análisis de metagenómica shotgun, el primer paso antes de interpretar resultados biológicos es evaluar la calidad de las secuencias. Las lecturas crudas que salen del secuenciador no deben asumirse como listas para análisis: pueden contener bases de baja calidad, adaptadores, lecturas demasiado cortas, secuencias artificiales, duplicación técnica, contaminación cruzada o lecturas provenientes del hospedero. Si estos problemas no se detectan y corrigen, pueden afectar la clasificación taxonómica, inflar falsos positivos, reducir la sensibilidad para detectar microorganismos reales o generar comparaciones sesgadas entre muestras.

En este taller trabajaremos con datos de metagenómica shotgun, es decir, lecturas generadas a partir del ADN total presente en una muestra. A diferencia de los análisis basados en amplicones como 16S, ITS o 18S, la metagenómica shotgun puede capturar bacterias, arqueas, virus, hongos, protistas y ADN del hospedero en una misma corrida. Por esta razón, la etapa de calidad es especialmente importante: antes de clasificar las lecturas contra bases de datos taxonómicas, necesitamos saber qué tan confiables son, si requieren recorte, si contienen adaptadores y qué proporción corresponde potencialmente al hospedero.

# ¿Por qué la calidad es el primer filtro crítico?

El control de calidad permite responder preguntas básicas antes de cualquier análisis posterior:

- ¿Cuántas lecturas tiene cada muestra?
- ¿Qué tan confiables son las bases?
- ¿Existen adaptadores o secuencias técnicas?
- ¿Las lecturas tienen una longitud adecuada?
- ¿Hay ADN del hospedero?
- ¿Todas las muestras son comparables?

Una muestra con muy pocas lecturas puede no tener profundidad suficiente para análisis taxonómico o comparativo. Una baja calidad de base aumenta la probabilidad de errores de secuenciación y puede afectar alineamientos o clasificaciones. Los adaptadores pueden alinearse erróneamente contra bases contaminadas o generar asignaciones taxonómicas artificiales. Las lecturas demasiado cortas suelen ser menos informativas y pueden clasificarse de forma ambigua. En muestras humanas, una fracción de las lecturas puede corresponder al genoma humano y debe removerse antes de análisis taxonómicos. Finalmente, diferencias extremas en profundidad, calidad o contaminación pueden afectar las conclusiones del estudio.

# Conceptos clave

**Lectura cruda:** secuencia generada directamente por el secuenciador, antes de cualquier filtrado, recorte o remoción de contaminantes.

**Calidad de base:** medida de confianza asociada a cada nucleótido. Usualmente se expresa como un puntaje Phred/Q. A mayor valor de Q, menor probabilidad de error.

**Puntaje Phred/Q:** escala logarítmica que representa la probabilidad de error de una base. Por ejemplo, Q20 equivale aproximadamente a 1 error cada 100 bases, mientras que Q30 equivale aproximadamente a 1 error cada 1000 bases.

**Adaptadores:** secuencias sintéticas usadas durante la preparación de librerías o la secuenciación. Si permanecen en los FASTQ, deben removerse porque no representan ADN biológico de la muestra.

**Recorte o trimming:** eliminación de bases de baja calidad, adaptadores o extremos problemáticos de las lecturas.

**Filtrado:** eliminación completa de lecturas que no cumplen criterios mínimos, por ejemplo longitud mínima, calidad media mínima o complejidad suficiente.

**Lecturas pareadas:** lecturas cortas generadas desde ambos extremos de un fragmento de ADN. Se representan usualmente como archivos R1 y R2.

**Lecturas largas:** lecturas de mayor longitud generadas por tecnologías como Oxford Nanopore o PacBio. Suelen tener longitudes variables y se evalúan con criterios diferentes a los de lecturas cortas.

**Remoción de hospedero:** alineamiento de las lecturas contra un genoma de referencia del hospedero, por ejemplo humano, para retirar las secuencias que no pertenecen al microbioma.

# ¿Qué es nf-core/taxprofiler?

`nf-core/taxprofiler` es un pipeline reproducible desarrollado dentro de la comunidad nf-core y ejecutado con Nextflow. Está diseñado para el análisis de metagenómica shotgun de lecturas cortas y largas, permitiendo integrar múltiples herramientas de preprocesamiento, remoción de hospedero, clasificación taxonómica, perfilamiento de abundancias y generación de reportes estandarizados.

En un flujo completo, `taxprofiler` puede realizar varias etapas:

```text
FASTQ / FASTA de entrada
   |
   |-- Validación del samplesheet
   |-- Control de calidad inicial
   |-- Recorte de adaptadores y filtrado
   |-- Remoción de hospedero
   |-- Unión de corridas por muestra, si aplica
   |-- Clasificación o perfilamiento taxonómico
   |-- Reportes finales y visualización
```

Sin embargo, en este taller no ejecutaremos la clasificación taxonómica. No usaremos herramientas como Kraken2, Bracken, Centrifuge, Kaiju, MALT, MetaPhlAn o DIAMOND. Usaremos `taxprofiler` únicamente como una plataforma reproducible para trabajar la primera parte del flujo:

```text
Lecturas crudas
   |
   |-- Evaluación inicial de calidad
   |-- Recorte / filtrado
   |-- Remoción de hospedero
   |-- Reportes MultiQC
   |-- Lecturas limpias para análisis posterior
```

# ¿Por qué usar taxprofiler si solo haremos calidad?

Aunque podríamos ejecutar herramientas individuales como FastQC, fastp, Filtlong, Nanoq, Bowtie2 o Minimap2 por separado, usar `taxprofiler` tiene varias ventajas para nuestro curso:

- **Reproducibilidad:** todos los pasos quedan registrados en una sola ejecución de Nextflow.
- **Estandarización:** todos los estudiantes usan la misma estructura de entrada y salida.
- **Escalabilidad:** el mismo flujo puede correr en computador local, servidor o cluster HPC.
- **Trazabilidad:** los reportes, logs y archivos intermedios quedan organizados por herramienta y muestra.
- **Continuidad:** las lecturas limpias pueden reutilizarse después para clasificación taxonómica, ensamblaje o análisis funcional.

# Datos del taller

Trabajaremos dos escenarios:

1. **Lecturas cortas**, por ejemplo Illumina o DNBSEQ, usualmente en formato paired-end (`R1`, `R2`). En este caso nos enfocaremos en calidad por base, adaptadores, recorte con `fastp` y remoción de hospedero con Bowtie2.

2. **Lecturas largas**, por ejemplo Oxford Nanopore o PacBio, usualmente en formato single-end. En este caso nos enfocaremos en longitud de lectura, calidad media y filtrado con herramientas apropiadas para lecturas largas.

# Referencia a la documentación

Este taller se basa en la documentación oficial de `nf-core/taxprofiler`, especialmente en las secciones de uso, preparación de samplesheet, preprocesamiento de lecturas cortas y largas, y remoción de hospedero.

Documentación oficial:

<https://nf-co.re/taxprofiler/2.0.0>

# Objetivos

## Objetivo general

Aplicar un flujo reproducible de control de calidad de lecturas metagenómicas cortas y largas usando `nf-core/taxprofiler`, interpretando los reportes generados y justificando las decisiones de recorte, filtrado y remoción de hospedero.

## Objetivos específicos

Al finalizar el taller, el estudiante deberá ser capaz de:

- Reconocer las diferencias prácticas entre lecturas cortas y largas en datos metagenómicos.
- Organizar archivos FASTQ y construir un samplesheet compatible con `nf-core/taxprofiler`.
- Ejecutar una corrida inicial de calidad para evaluar el estado de las lecturas crudas.
- Interpretar resultados de herramientas de control de calidad y reportes integrados.
- Definir parámetros razonables de recorte y filtrado para lecturas cortas y largas.
- Ejecutar remoción de hospedero usando Bowtie2 para lecturas cortas.
- Identificar los archivos finales de lecturas listas para análisis posteriores.

# Estructura general del flujo

```text
FASTQ crudos
   |
   |-- 1. Organización de datos
   |-- 2. Construcción del samplesheet
   |-- 3. Control de calidad inicial
   |-- 4. Recorte / filtrado de calidad
   |-- 5. Remoción de hospedero
   |-- 6. Revisión de reportes MultiQC
   |-- 7. Selección de lecturas listas para análisis posterior
```

# Preparación del ambiente de trabajo

## Crear estructura de carpetas

Primero, cada estudiante debe ubicarse en su carpeta personal dentro del directorio de estudiantes del curso.

```{bash, eval=FALSE}
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE
```

Para lecturas largas:

```{bash, eval=FALSE}
mkdir -p taller_longreads
cd taller_longreads
mkdir -p data/long_reads_raw
```

Para lecturas cortas:

```{bash, eval=FALSE}
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE
mkdir -p taller_shortReads
cd taller_shortReads
mkdir -p data/short_reads_raw
mkdir -p metadata
```

# LECTURAS CORTAS

Para lecturas cortas se utilizarán archivos FASTQ pareados ubicados en el cluster Hypatia en la siguiente ruta:

```{bash, eval=FALSE}
/hpcfs/home/cursos/metagenomica_moderna/datos_shotgun/01_raw_reads/fastq
```

Cada muestra tiene dos archivos asociados:

```text
<ID>_1.fastq.gz  = lectura forward / R1
<ID>_2.fastq.gz  = lectura reverse / R2
```

Por ejemplo, para la muestra `SRR17048892`, los archivos que deben usarse son:

```text
SRR17048892_1.fastq.gz
SRR17048892_2.fastq.gz
```

## Asignación de muestras

Cada estudiante deberá trabajar con las muestras asignadas en la siguiente tabla. Para cada ID de secuencia, deben traer siempre los dos archivos correspondientes: el archivo forward (`_1.fastq.gz`) y el archivo reverse (`_2.fastq.gz`). No se debe analizar solo uno de los dos archivos, porque las lecturas cortas de este taller son paired-end.

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
| Pérez Rubiano, Claudia Constanza | SRR17048929 | SRR17048958 |
| Redondo Gonzalez, Marilin Yohandra | SRR17048984 | SRR17048921 |

## Copiar las lecturas cortas asignadas

Las lecturas crudas están en la siguiente ruta:

```{bash, eval=FALSE}
/hpcfs/home/cursos/metagenomica_moderna/datos_shotgun/01_raw_reads/fastq
```

Cada estudiante debe copiar sus archivos asignados a la carpeta `data/short_reads_raw`.

Plantilla general:

```{bash, eval=FALSE}
cp /hpcfs/home/cursos/metagenomica_moderna/datos_shotgun/01_raw_reads/fastq/SRRXXXXXXX_1.fastq.gz data/short_reads_raw/

cp /hpcfs/home/cursos/metagenomica_moderna/datos_shotgun/01_raw_reads/fastq/SRRXXXXXXX_2.fastq.gz data/short_reads_raw/
```

Deben reemplazar `SRRXXXXXXX` por el código de la muestra que les fue asignada.

Por ejemplo, si les asignaron `SRR17048892`, deben ejecutar:

```{bash, eval=FALSE}
cp /hpcfs/home/cursos/metagenomica_moderna/datos_shotgun/01_raw_reads/fastq/SRR17048892_1.fastq.gz data/short_reads_raw/

cp /hpcfs/home/cursos/metagenomica_moderna/datos_shotgun/01_raw_reads/fastq/SRR17048892_2.fastq.gz data/short_reads_raw/
```

Verificar que los archivos fueron copiados:

```{bash, eval=FALSE}
ls -lh data/short_reads_raw/
```

# Creación del archivo `samplesheet.csv`

Para ejecutar el flujo de trabajo con lecturas cortas, necesitamos crear un archivo llamado `samplesheet.csv`. Este archivo le indica al pipeline cuáles son las muestras que se van a analizar, dónde están ubicados los archivos FASTQ y cuál fue la plataforma de secuenciación utilizada.

En este taller, cada estudiante trabajará con dos muestras asignadas. Para cada muestra se deben incluir sus dos archivos paired-end:

- Lectura forward: `_1.fastq.gz`
- Lectura reverse: `_2.fastq.gz`

Estas lecturas provienen de una plataforma Illumina. Por lo tanto, en la columna `instrument_platform` se debe escribir `ILLUMINA`.

## Estructura del archivo `samplesheet.csv`

El archivo debe tener las siguientes columnas:

```csv
sample,run_accession,instrument_platform,fastq_1,fastq_2,fasta
```

| Columna | Descripción |
|---|---|
| `sample` | Nombre de la muestra. En este taller usaremos el código SRR de cada muestra. |
| `run_accession` | Identificador único de la corrida. Se puede construir usando el código de la muestra seguido de `_run0`. |
| `instrument_platform` | Plataforma de secuenciación. Para este taller será `ILLUMINA`. |
| `fastq_1` | Ruta al archivo FASTQ forward. |
| `fastq_2` | Ruta al archivo FASTQ reverse. |
| `fasta` | Se deja vacío porque estamos trabajando con lecturas FASTQ, no con archivos FASTA ensamblados. |

## Crear el archivo `samplesheet.csv`

Primero asegúrese de estar en la carpeta principal del taller:

```{bash, eval=FALSE}
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE/taller_shortReads
mkdir -p metadata
```

Para este ejemplo se usaron las muestras `SRR17048924` y `SRR17048929`:

```{bash, eval=FALSE}
cat > metadata/samplesheet.csv << 'EOF'
sample,run_accession,instrument_platform,fastq_1,fastq_2,fasta
SRR17048924,SRR17048924_run0,ILLUMINA,data/short_reads_raw/SRR17048924_1.fastq.gz,data/short_reads_raw/SRR17048924_2.fastq.gz,
SRR17048929,SRR17048929_run0,ILLUMINA,data/short_reads_raw/SRR17048929_1.fastq.gz,data/short_reads_raw/SRR17048929_2.fastq.gz,
EOF
```

Verificar el contenido:

```{bash, eval=FALSE}
cat metadata/samplesheet.csv
```

# Preparación del índice de Bowtie2 para remoción de huésped

Antes de ejecutar `nf-core/taxprofiler` con remoción de huésped, necesitamos tener disponible un índice de Bowtie2 del genoma humano.

En este taller usaremos un índice previamente construido a partir del genoma humano de referencia `GRCh38`. Este índice será utilizado por `taxprofiler` para identificar y remover las lecturas que alinean contra el huésped humano.

Cada estudiante debe copiar este índice dentro de su propia carpeta de trabajo.

## Crear carpeta para Bowtie2

```{bash, eval=FALSE}
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE/taller_shortReads
mkdir -p Bowtie2
cd Bowtie2
```

## Copiar el índice ya construido

En el taller no es necesario construir nuevamente el índice porque ya existe una versión preparada en la carpeta compartida del curso.

```{bash, eval=FALSE}
cp -r /hpcfs/home/cursos/metagenomica_moderna/Prueba/Databases/Bowtie2/INDEX .
```

Verificar:

```{bash, eval=FALSE}
ls -lh INDEX/
```

La carpeta debe contener archivos similares a:

```text
GRCh38.1.bt2l
GRCh38.2.bt2l
GRCh38.3.bt2l
GRCh38.4.bt2l
GRCh38.rev.1.bt2l
GRCh38.rev.2.bt2l
```

## Script usado para construir el índice

El índice fue construido previamente usando un script como el siguiente:

```{bash, eval=FALSE}
#!/bin/bash

#SBATCH --job-name=bowtie2
#SBATCH -p short
#SBATCH --cpus-per-task=32
#SBATCH --mem=80G
#SBATCH --time=1-00:00:00
#SBATCH -o bowtie2.o%j
#SBATCH -e bowtie2.e%j

module load bowtie2/2.4.5

bowtie2-build --large-index \
  /hpcfs/home/cursos/metagenomica_moderna/Prueba/Databases/GenomeHost/GRCh38.p14_genomic.fna \
  /hpcfs/home/cursos/metagenomica_moderna/Prueba/Databases/Bowtie2/INDEX/GRCh38
```

En este taller los estudiantes no necesitan ejecutar este script. Solo deben copiar la carpeta `INDEX`.

# Creación del archivo `db.csv`

Aunque en este taller no vamos a realizar clasificación taxonómica, `nf-core/taxprofiler` solicita un archivo de bases de datos mediante el parámetro `--databases`.

Normalmente, este archivo se utiliza para indicar al pipeline dónde están ubicadas las bases de datos de herramientas como Kraken2, Bracken, Kaiju, Centrifuge, entre otras.

Sin embargo, en esta práctica solo queremos ejecutar:

- Control de calidad de lecturas cortas.
- Limpieza con `fastp`.
- Remoción de lecturas del huésped con Bowtie2.

Por esta razón, no vamos a usar ninguna base de datos taxonómica real. Aun así, debemos crear un archivo `db.csv` mínimo para que el pipeline pueda pasar la validación inicial.

## Crear el archivo `db.csv`

Asegúrese de estar en la carpeta principal del taller:

```{bash, eval=FALSE}
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE/taller_shortReads
mkdir -p metadata
```

Crear el archivo:

```{bash, eval=FALSE}
cat > metadata/db.csv << 'EOF'
tool,db_name,db_params,db_type,db_path
kraken2,dummy_db,,short,Bowtie2/INDEX
EOF
```

Este archivo tiene la estructura que espera `nf-core/taxprofiler` para las bases de datos, pero en este caso se usa únicamente como archivo mínimo de validación.

La ruta `Bowtie2/INDEX` corresponde a una carpeta existente dentro del taller. No se usará como base de datos de Kraken2, porque en este flujo no activaremos Kraken2 ni ninguna otra herramienta de clasificación taxonómica.

Verificar:

```{bash, eval=FALSE}
cat metadata/db.csv
ls -lh Bowtie2/INDEX
```

# Configuración de Nextflow

Antes de ejecutar el pipeline, cree el archivo `nextflow.config`.

```{bash, eval=FALSE}
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE/taller_shortReads
nano nextflow.config
```

Pegue el siguiente contenido:

```groovy
process {
    executor = 'slurm'
    queue = 'medium'

    cpus = 2
    memory = '8.GB'
    time = '4.h'

    withName: 'FASTP' {
        cpus = 4
        memory = '8.GB'
        time = '6.h'
    }

    withName: 'BOWTIE2_ALIGN' {
        cpus = 16
        memory = '60.GB'
        time = '24.h'
    }

    withName: 'MULTIQC' {
        cpus = 2
        memory = '8.GB'
        time = '2.h'
    }
}

executor {
    queueSize = 4
}

singularity {
    enabled = true
    autoMounts = true
    pullTimeout = '12h'
}
```

# Ejecución principal de `nf-core/taxprofiler`

Después de preparar el `samplesheet.csv`, copiar el índice de Bowtie2, crear el archivo `db.csv` y preparar el archivo `nextflow.config`, podemos ejecutar el flujo principal de `nf-core/taxprofiler`.

En esta práctica usaremos `taxprofiler` únicamente para:

- Procesar lecturas cortas paired-end.
- Realizar limpieza de lecturas con `fastp`.
- Guardar las lecturas preprocesadas.
- Remover lecturas del huésped humano usando Bowtie2.
- Guardar las lecturas que no alinearon contra el genoma humano.
- Generar archivos finales listos para análisis posteriores.

No realizaremos clasificación taxonómica.

## Crear el job principal

Primero, ubíquese dentro de la carpeta principal del taller:

```{bash, eval=FALSE}
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE/taller_shortReads
```

Crear el archivo del job:

```{bash, eval=FALSE}
nano taxprofiler_job.sh
```

Dentro del archivo pegue el siguiente contenido. Recuerde reemplazar `NOMBRE_ESTUDIANTE` por el nombre de su carpeta.

```{bash, eval=FALSE}
#!/bin/bash

#SBATCH --job-name=nfcore_taxprofiler
#SBATCH -p medium
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=16
#SBATCH --mem=80G
#SBATCH --time=4-00:00:00
#SBATCH --mail-user=jf.meza@uniandes.edu.co
#SBATCH --mail-type=ALL
#SBATCH -o taxprofiler_job.o%j
#SBATCH -e taxprofiler_job.e%j

# ================================
# nf-core/taxprofiler
# Taller de calidad de lecturas cortas
# QC con fastp + remoción de huésped
# ================================

# Cargar módulos necesarios
module load jdk/19.0.2
module load singularity/3.7.1
module load nextflow/25.04.8

# Limpiar caché de comandos
hash -r

# Verificar versiones
nextflow -version
java -version

# Ejecutar nf-core/taxprofiler
nextflow run nf-core/taxprofiler \
  -r 1.2.6 \
  -resume \
  -profile singularity \
  -c /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE/taller_shortReads/nextflow.config \
  --input /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE/taller_shortReads/metadata/samplesheet.csv \
  --databases /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE/taller_shortReads/metadata/db.csv \
  --outdir /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE/taller_shortReads/output \
  --preprocessing_qc_tool falco \
  --perform_shortread_qc \
  --shortread_qc_tool fastp \
  --save_preprocessed_reads \
  --perform_shortread_hostremoval \
  --hostremoval_reference /hpcfs/home/cursos/metagenomica_moderna/Prueba/Databases/GenomeHost/GRCh38.p14_genomic.fna \
  --shortread_hostremoval_index /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE/taller_shortReads/Bowtie2/INDEX \
  --save_hostremoval_unmapped \
  --save_hostremoval_bam \
  --save_analysis_ready_fastqs
```

Para guardar el archivo en `nano`, use:

```text
Ctrl + O
Enter
Ctrl + X
```

## Ejecutar el job

```{bash, eval=FALSE}
sbatch taxprofiler_job.sh
```

Revisar el estado del job:

```{bash, eval=FALSE}
squeue -u $USER
```

Revisar archivos de salida y error:

```{bash, eval=FALSE}
ls -lh taxprofiler_job.o*
ls -lh taxprofiler_job.e*
```

# Explicación de los parámetros del job de `nf-core/taxprofiler`


El archivo `taxprofiler_job.sh` es el script que enviamos a Slurm para ejecutar `nf-core/taxprofiler` en el cluster.  
Este job tiene tres partes principales:

1. Solicitud de recursos al cluster.
2. Carga de módulos necesarios.
3. Ejecución del pipeline con los parámetros del taller.

---

## 1. Recursos solicitados a Slurm

La primera parte del script contiene las líneas que empiezan con `#SBATCH`.  
Estas líneas le indican al cluster cuántos recursos necesita el trabajo.

| Parámetro | Función |
|---|---|
| `--job-name=nfcore_taxprofiler` | Nombre del job en la cola de Slurm. |
| `-p medium` | Cola o partición donde se ejecutará el job. |
| `-N 1` | Número de nodos solicitados. |
| `-n 1` | Número de tareas principales. |
| `--cpus-per-task=16` | Número de CPUs disponibles para el job. |
| `--mem=80G` | Memoria RAM solicitada. |
| `--time=4-00:00:00` | Tiempo máximo de ejecución: 4 días. |
| `--mail-user` | Correo para recibir notificaciones. |
| `--mail-type=ALL` | Envía correo al iniciar, terminar o fallar. |
| `-o taxprofiler_job.o%j` | Archivo de salida estándar. |
| `-e taxprofiler_job.e%j` | Archivo de errores. |

:::{.callout-note}
El símbolo `%j` representa el identificador del job asignado por Slurm.  
Por ejemplo, si el job tiene ID `452932`, los archivos pueden llamarse `taxprofiler_job.o452932` y `taxprofiler_job.e452932`.
:::

---

## 2. Módulos necesarios

Antes de ejecutar el pipeline, cargamos los programas que necesita `taxprofiler`.

```{bash, eval=FALSE}
module load jdk/19.0.2
module load singularity/3.7.1
module load nextflow/25.04.8
```

| Módulo | ¿Para qué sirve? |
|---|---|
| `jdk/19.0.2` | Carga Java, necesario para ejecutar Nextflow. |
| `singularity/3.7.1` | Permite usar contenedores con las herramientas bioinformáticas. |
| `nextflow/25.04.8` | Ejecuta y organiza el flujo de trabajo. |

Después verificamos las versiones:

```{bash, eval=FALSE}
nextflow -version
java -version
```

Esto es útil para dejar registro de la ejecución y para diagnosticar errores si el pipeline falla.

---

## 3. Ejecución del pipeline

La ejecución principal comienza con:

```{bash, eval=FALSE}
nextflow run nf-core/taxprofiler
```

Esto le dice a Nextflow que vamos a ejecutar el pipeline `nf-core/taxprofiler`.

---

## 4. Parámetros generales de Nextflow

| Parámetro | Significado |
|---|---|
| `-r 1.2.6` | Ejecuta la versión `1.2.6` del pipeline. |
| `-resume` | Retoma una ejecución previa sin repetir procesos ya completados. |
| `-profile singularity` | Usa contenedores de Singularity. |
| `-c nextflow.config` | Usa un archivo de configuración personalizado. |

:::{.callout-tip}
La opción `-resume` es muy útil en el cluster.  
Si el pipeline falla por una ruta incorrecta, falta de memoria o un error temporal, se puede corregir el problema y volver a ejecutar el mismo job sin empezar desde cero.
:::

---

## 5. Archivos de entrada y salida

Estos parámetros indican qué archivos usa el pipeline y dónde guardará los resultados.

| Parámetro | Función |
|---|---|
| `--input` | Ruta del archivo `samplesheet.csv`. |
| `--databases` | Ruta del archivo `db.csv`. |
| `--outdir` | Carpeta donde se guardan los resultados. |

Ejemplo:

```{bash, eval=FALSE}
--input /hpcfs/home/cursos/metagenomica_moderna/estudiantes/j_meza/taller_shortReads/samplesheet.csv
--databases /hpcfs/home/cursos/metagenomica_moderna/estudiantes/j_meza/taller_shortReads/metadata/db.csv
--outdir /hpcfs/home/cursos/metagenomica_moderna/estudiantes/j_meza/taller_shortReads/output
```

:::{.callout-warning}
En este taller usamos `--databases` solo porque `taxprofiler` lo solicita durante la validación inicial.  
No vamos a realizar clasificación taxonómica, porque no activamos herramientas como `Kraken2`, `Bracken` o `Krona`.
:::

---

## 6. Control de calidad con `fastp`

Para limpiar las lecturas cortas usamos `fastp`.

```{bash, eval=FALSE}
--shortread_qc_tool fastp
--save_preprocessed_reads
```

| Parámetro | Función |
|---|---|
| `--shortread_qc_tool fastp` | Usa `fastp` para limpiar lecturas cortas. |
| `--save_preprocessed_reads` | Guarda las lecturas después del procesamiento. |

`fastp` permite:

- Remover bases de baja calidad.
- Detectar y recortar adaptadores.
- Filtrar lecturas problemáticas.
- Generar reportes `.html` y `.json`.

:::{.callout-note}
En este taller, los reportes de `fastp` serán una de las salidas principales para evaluar la calidad antes y después del trimming.
:::

---

## 7. Remoción de lecturas del huésped

Después del control de calidad, removemos lecturas que alinean contra el genoma humano.

```{bash, eval=FALSE}
--perform_shortread_hostremoval
--hostremoval_reference /hpcfs/home/cursos/metagenomica_moderna/Prueba/Databases/GenomeHost/GRCh38.p14_genomic.fna
--shortread_hostremoval_index /hpcfs/home/cursos/metagenomica_moderna/estudiantes/j_meza/taller_shortReads/Bowtie2/INDEX
```

| Parámetro | Función |
|---|---|
| `--perform_shortread_hostremoval` | Activa la remoción de huésped para lecturas cortas. |
| `--hostremoval_reference` | FASTA del genoma humano de referencia. |
| `--shortread_hostremoval_index` | Carpeta con el índice de Bowtie2. |

En este taller usamos el genoma humano de referencia:

```{bash, eval=FALSE}
GRCh38.p14_genomic.fna
```

Bowtie2 compara las lecturas contra este genoma y separa:

- Lecturas que alinean contra humano.
- Lecturas que no alinean contra humano.

Las lecturas que no alinean son las más importantes para análisis metagenómicos posteriores.

---

## 8. Archivos que queremos guardar

Estas opciones indican qué resultados intermedios y finales queremos conservar.

```{bash, eval=FALSE}
--save_hostremoval_unmapped
--save_hostremoval_bam
--save_analysis_ready_fastqs
```

| Parámetro | Resultado |
|---|---|
| `--save_hostremoval_unmapped` | Guarda las lecturas que no alinearon contra el genoma humano. |
| `--save_hostremoval_bam` | Guarda archivos BAM de la alineación contra el huésped. |
| `--save_analysis_ready_fastqs` | Guarda los FASTQ finales listos para análisis posteriores. |

:::{.callout-important}
Las lecturas `unmapped` son las lecturas que no alinearon contra el genoma humano.  
Estas son las lecturas que se usarían después para clasificación taxonómica, ensamblaje metagenómico o análisis funcional.
:::

---

## 9. ¿Qué NO estamos haciendo en este taller?

Aunque usamos `taxprofiler`, en esta práctica **no vamos a realizar clasificación taxonómica**.

Por lo tanto, no usamos:

```{bash, eval=FALSE}
--run_kraken2
--run_bracken
--run_krona
--run_profile_standardisation
```

El objetivo de este taller es llegar solo hasta:

```text
Lecturas crudas
      ↓
Limpieza con fastp
      ↓
Remoción de huésped con Bowtie2
      ↓
Lecturas limpias listas para análisis posterior
```

---

## 10. Resumen visual del job

```text
samplesheet.csv
      ↓
nf-core/taxprofiler
      ↓
fastp
      ↓
Lecturas limpias
      ↓
Bowtie2 contra GRCh38
      ↓
Lecturas humanas removidas
      ↓
FASTQ finales listos para análisis posterior
```

Al finalizar, los resultados se guardarán en la carpeta:

```{bash, eval=FALSE}
output/
```
# Resultados esperados en la carpeta `output`

Al finalizar la ejecución de `nf-core/taxprofiler`, se generará una carpeta llamada `output`, donde se almacenarán los resultados del procesamiento de las lecturas cortas.

En este taller, el pipeline se ejecutó únicamente para realizar:

- Control de calidad y limpieza de lecturas con `fastp`.
- Remoción de lecturas del huésped humano con Bowtie2.
- Generación de archivos FASTQ finales listos para análisis posteriores.

No se realizó clasificación taxonómica, por lo tanto no se esperan resultados de Kraken2, Bracken, Krona o Taxpasta.

## Revisar la carpeta de resultados

```{bash, eval=FALSE}
ls -lh output
find output -maxdepth 2 -type d
```

## Reportes de calidad generados por `fastp`

Una de las salidas más importantes del pipeline son los reportes de calidad generados por `fastp`. Estos reportes permiten evaluar la calidad de las lecturas antes y después del proceso de limpieza o trimming. En ellos se puede revisar información como:

- Número total de lecturas antes y después del filtrado.
- Porcentaje de lecturas conservadas.
- Calidad por posición.
- Distribución de contenido GC.
- Presencia de adaptadores.
- Bases de baja calidad removidas.
- Longitud de las lecturas antes y después del procesamiento.

Buscar reportes HTML:

```{bash, eval=FALSE}
find output -type f -name "*.html"
```

Buscar reportes JSON:

```{bash, eval=FALSE}
find output -type f -name "*.json"
```

Los archivos `.html` pueden descargarse y abrirse en un navegador web para revisar gráficamente la calidad de las lecturas antes y después del trimming.

## Lecturas después del trimming

Como en el job usamos la opción `--save_preprocessed_reads`, el pipeline guarda las lecturas procesadas después del filtrado y trimming realizado por `fastp`.

Para buscarlas:

```{bash, eval=FALSE}
find output -type f -name "*.fastq.gz"
```

## Remoción de lecturas del huésped

Después del procesamiento con `fastp`, el pipeline ejecuta la remoción de huésped usando Bowtie2. En esta etapa, las lecturas se alinean contra el genoma humano de referencia `GRCh38`.

El objetivo es separar:

- Lecturas que alinean contra el genoma humano.
- Lecturas que no alinean contra el genoma humano.

Las lecturas que no alinean contra el genoma humano son las más importantes para análisis metagenómicos posteriores, porque corresponden a la fracción no humana de la muestra.

Como en el job usamos `--save_hostremoval_unmapped`, el pipeline guarda las lecturas no alineadas contra el huésped.

```{bash, eval=FALSE}
find output -type f -name "*unmapped*.fastq.gz"
```

También usamos `--save_hostremoval_bam`, por lo tanto el pipeline puede guardar archivos BAM de la alineación contra el huésped.

```{bash, eval=FALSE}
find output -type f -name "*.bam"
```

## FASTQ finales listos para análisis

La opción `--save_analysis_ready_fastqs` indica al pipeline que guarde los archivos FASTQ finales listos para análisis posteriores. Estos archivos corresponden a las lecturas que pasaron por las etapas de limpieza y remoción de huésped.

```{bash, eval=FALSE}
find output -type f -name "*.fastq.gz"
```

Estos FASTQ finales pueden usarse posteriormente para análisis como clasificación taxonómica, ensamblaje metagenómico o estimación de abundancias, dependiendo del objetivo del estudio.

## Reporte general de MultiQC

El pipeline también genera un reporte integrado con MultiQC, que resume los resultados de las diferentes herramientas ejecutadas.

```{bash, eval=FALSE}
find output -type f -name "multiqc_report.html"
```

Este archivo puede descargarse y abrirse en un navegador web.

## Resumen de resultados esperados

```text
output/
├── fastp/
│   ├── reportes HTML de calidad
│   ├── reportes JSON de calidad
│   └── lecturas procesadas por fastp
├── bowtie2/
│   ├── resultados de alineación contra el huésped
│   ├── archivos BAM, si fueron guardados
│   └── lecturas no alineadas contra el genoma humano
├── multiqc/
│   └── reporte general multiqc_report.html
└── pipeline_info/
    └── información técnica de la ejecución del pipeline
```

## Interpretación general

En esta práctica, los archivos más importantes para revisar son:

1. Los reportes `.html` de `fastp`, porque muestran la calidad de las lecturas antes y después del trimming.
2. Los FASTQ procesados, porque corresponden a las lecturas limpias después del control de calidad.
3. Las lecturas `unmapped`, porque representan las secuencias que no alinearon contra el genoma humano.
4. El reporte `multiqc_report.html`, porque resume los resultados de todas las muestras en un solo archivo.

El flujo final puede resumirse así:

```text
Lecturas crudas
      ↓
Control de calidad y trimming con fastp
      ↓
Lecturas limpias
      ↓
Alineación contra genoma humano con Bowtie2
      ↓
Lecturas no humanas o unmapped
      ↓
FASTQ finales listos para análisis posteriores
```

> **Nota:** Los reportes HTML de `fastp` permiten comparar la calidad de las lecturas antes y después del procesamiento. Estos reportes son una de las salidas principales para interpretar si el trimming y filtrado mejoraron la calidad de los datos.

> **Importante:** Las lecturas más relevantes para análisis metagenómicos posteriores son las que no alinearon contra el genoma humano, es decir, las lecturas `unmapped` generadas durante la remoción de huésped.

> **Advertencia:** En este taller no se espera obtener resultados de clasificación taxonómica. Si aparecen carpetas de Kraken2, Bracken, Krona o Taxpasta, significa que accidentalmente se activó alguna herramienta de clasificación.

# LECTURAS LARGAS

En esta parte del taller trabajaremos con lecturas largas de Oxford Nanopore.  
El objetivo es ejecutar `nf-core/taxprofiler` únicamente para realizar control de calidad y preprocesamiento de lecturas largas.

A diferencia del flujo de lecturas cortas, en este caso:

- Las lecturas son **single-end**.
- No hay archivos forward y reverse.
- No usaremos Bowtie2.
- No haremos remoción de huésped.
- No haremos clasificación taxonómica.
- Usaremos herramientas para lecturas largas, como `porechop_abi` y `nanoq`.

---

## 1. Crear la carpeta del taller

Cada estudiante debe trabajar dentro de su carpeta personal.

Primero, entre a su carpeta:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/NOMBRE_ESTUDIANTE
```

Reemplace `NOMBRE_ESTUDIANTE` por el nombre de su carpeta.

Por ejemplo:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/j_meza
```

Ahora cree la carpeta principal del taller de lecturas largas:

```bash
mkdir -p taller_longreads
cd taller_longreads
```

Cree la estructura básica de carpetas:

```bash
mkdir -p data/long_reads_raw
mkdir -p metadata
mkdir -p output
mkdir -p logs
```

La estructura esperada será:

```text
taller_longreads/
├── data/
│   └── long_reads_raw/
├── metadata/
├── output/
└── logs/
```

---

## 2. Copiar las lecturas largas

Las lecturas largas se encuentran en la carpeta compartida del curso:

```bash
/hpcfs/home/cursos/metagenomica_moderna/Prueba/Datos_Long
```

En este taller usaremos dos archivos FASTQ de Oxford Nanopore:

```text
ERR3152364.fastq.gz
ERR3152366.fastq.gz
```

Copie las lecturas a su carpeta `data/long_reads_raw`:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Prueba/Datos_Long/ERR3152364.fastq.gz data/long_reads_raw/

cp /hpcfs/home/cursos/metagenomica_moderna/Prueba/Datos_Long/ERR3152366.fastq.gz data/long_reads_raw/
```

Verifique que los archivos quedaron copiados:

```bash
ls -lh data/long_reads_raw/
```

La salida esperada debe mostrar:

```text
ERR3152364.fastq.gz
ERR3152366.fastq.gz
```

También puede verificar que los archivos comprimidos no estén dañados:

```bash
gzip -t data/long_reads_raw/ERR3152364.fastq.gz
gzip -t data/long_reads_raw/ERR3152366.fastq.gz
```

Si no aparece ningún mensaje de error, los archivos están bien.

---

## 3. Crear el `samplesheet` para lecturas largas

En `nf-core/taxprofiler`, el archivo `samplesheet` mantiene la misma estructura general:

```text
sample,run_accession,instrument_platform,fastq_1,fastq_2,fasta
```

Sin embargo, para lecturas largas Nanopore hay una diferencia importante:

- Se llena solo la columna `fastq_1`.
- La columna `fastq_2` queda vacía.
- La columna `fasta` queda vacía.
- La plataforma se escribe como `OXFORD_NANOPORE`.

Cree el archivo `samplesheet_longreads.csv`:

```bash
cat > metadata/samplesheet_longreads.csv << 'EOF'
sample,run_accession,instrument_platform,fastq_1,fastq_2,fasta
ERR3152364,ERR3152364_run0,OXFORD_NANOPORE,data/long_reads_raw/ERR3152364.fastq.gz,,
ERR3152366,ERR3152366_run0,OXFORD_NANOPORE,data/long_reads_raw/ERR3152366.fastq.gz,,
EOF
```

Revise el archivo:

```bash
cat metadata/samplesheet_longreads.csv
```

Debe verse así:

```text
sample,run_accession,instrument_platform,fastq_1,fastq_2,fasta
ERR3152364,ERR3152364_run0,OXFORD_NANOPORE,data/long_reads_raw/ERR3152364.fastq.gz,,
ERR3152366,ERR3152366_run0,OXFORD_NANOPORE,data/long_reads_raw/ERR3152366.fastq.gz,,
```

---

## 4. Crear un archivo `db.csv` mínimo

Aunque en este taller no haremos clasificación taxonómica, `nf-core/taxprofiler` solicita un archivo de bases de datos mediante el parámetro `--databases`.

Para cumplir con la validación del pipeline, crearemos un archivo mínimo.  
Este archivo **no se usará para clasificar**, porque no activaremos Kraken2, Bracken, Krona ni ninguna otra herramienta taxonómica.

Cree el archivo:

```bash
cat > metadata/db_longreads.csv << 'EOF'
tool,db_name,db_params,db_type,db_path
kraken2,dummy_db,,long,data/long_reads_raw
EOF
```

Revise su contenido:

```bash
cat metadata/db_longreads.csv
```

Debe verse así:

```text
tool,db_name,db_params,db_type,db_path
kraken2,dummy_db,,long,data/long_reads_raw
```

> **Nota:** aunque el archivo menciona `kraken2`, Kraken2 no se ejecutará porque no usaremos el parámetro `--run_kraken2`.

---

## 5. Crear el archivo `nextflow_longreads.config`

Ahora cree el archivo de configuración de recursos para Nextflow:

```bash
nano nextflow_longreads.config
```

Pegue el siguiente contenido:

```groovy
process {
    executor = 'slurm'
    queue = 'medium'

    cpus = 2
    memory = '8.GB'
    time = '4.h'

    withName: 'PORECHOP_ABI' {
        cpus = 4
        memory = '8.GB'
        time = '12.h'
    }

    withName: 'NANOQ' {
        cpus = 4
        memory = '8.GB'
        time = '12.h'
    }

    withName: 'MULTIQC' {
        cpus = 2
        memory = '8.GB'
        time = '4.h'
    }
}

executor {
    queueSize = 4
}

singularity {
    enabled = true
    autoMounts = true
    pullTimeout = '12h'
}
```

Guarde el archivo con:

```text
Ctrl + O
Enter
Ctrl + X
```

---

## 6. Crear el job de ejecución

Cree el archivo del job:

```bash
nano taxprofiler_longreads_job.sh
```

Pegue el siguiente contenido:

```bash
#!/bin/bash

#SBATCH --job-name=taxprofiler_longreads
#SBATCH -p medium
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=8
#SBATCH --mem=40G
#SBATCH --time=2-00:00:00
#SBATCH --mail-user=jf.meza@uniandes.edu.co
#SBATCH --mail-type=ALL
#SBATCH -o logs/taxprofiler_longreads.o%j
#SBATCH -e logs/taxprofiler_longreads.e%j

# ================================
# nf-core/taxprofiler
# Taller de lecturas largas Nanopore
# Solo QC y preprocesamiento
# Sin remoción de huésped
# Sin clasificación taxonómica
# ================================

module load jdk/19.0.2
module load singularity/3.7.1
module load nextflow/25.04.8

hash -r

nextflow -version
java -version

nextflow run nf-core/taxprofiler \
  -r 1.2.6 \
  -resume \
  -profile singularity \
  -c nextflow_longreads.config \
  --input metadata/samplesheet_longreads.csv \
  --databases metadata/db_longreads.csv \
  --outdir output \
  --perform_longread_qc \
  --longread_adapterremoval_tool porechop_abi \
  --longread_filter_tool nanoq \
  --save_preprocessed_reads \
  --save_analysis_ready_fastqs
```

Guarde el archivo:

```text
Ctrl + O
Enter
Ctrl + X
```

---

## 7. Ejecutar el job

Envíe el job a Slurm:

```bash
sbatch taxprofiler_longreads_job.sh
```

Revise si el job está en cola o corriendo:

```bash
squeue -u $USER
```

Revise los archivos de salida y error:

```bash
ls -lh logs/
```

Para ver la salida del job:

```bash
cat logs/taxprofiler_longreads.o*
```

Para revisar errores:

```bash
cat logs/taxprofiler_longreads.e*
```

---

## 8. ¿Qué cambia respecto al flujo de lecturas cortas?

| Aspecto | Lecturas cortas | Lecturas largas |
|---|---|---|
| Plataforma | Illumina / DNBSEQ | Oxford Nanopore |
| Tipo de lectura | Paired-end | Single-end |
| Archivos por muestra | Dos: R1 y R2 | Uno: FASTQ único |
| `instrument_platform` | `ILLUMINA` | `OXFORD_NANOPORE` |
| `fastq_1` | Forward / R1 | FASTQ Nanopore |
| `fastq_2` | Reverse / R2 | Vacío |
| QC principal | `fastp` | `porechop_abi` + `nanoq` |
| Remoción de host | Bowtie2 | No se realiza en este taller |
| Clasificación taxonómica | No se realiza | No se realiza |

---

## 9. Resultados esperados

Cuando el pipeline termine correctamente, revise la carpeta `output`:

```bash
ls -lh output/
```

También puede explorar las carpetas internas:

```bash
find output -maxdepth 2 -type d
```

En este taller se esperan resultados relacionados con:

```text
porechop_abi/
nanoq/
multiqc/
pipeline_info/
```

---

## 10. Reportes de calidad

El pipeline generará reportes de calidad y preprocesamiento de las lecturas largas.

Busque archivos HTML con:

```bash
find output -type f -name "*.html"
```

También puede buscar archivos de resumen con:

```bash
find output -type f -name "*.txt"
find output -type f -name "*.log"
find output -type f -name "*.json"
```

El reporte general de MultiQC puede buscarse con:

```bash
find output -type f -name "multiqc_report.html"
```

Este archivo resume la ejecución del pipeline y los resultados principales de las herramientas usadas.

---

## 11. FASTQ procesados

Como usamos:

```bash
--save_preprocessed_reads
--save_analysis_ready_fastqs
```

el pipeline guardará archivos FASTQ procesados.

Puede buscarlos con:

```bash
find output -type f -name "*.fastq.gz"
```

Estos archivos representan lecturas largas después del preprocesamiento.

---

## 12. Interpretación general de las salidas

Al finalizar el taller, cada estudiante debe identificar:

1. Los reportes de calidad de las lecturas largas.
2. Las lecturas procesadas después de `porechop_abi` y `nanoq`.
3. El reporte integrado `multiqc_report.html`.
4. Los FASTQ finales listos para análisis posteriores.

El flujo ejecutado puede resumirse así:

```text
Lecturas largas crudas Nanopore
        ↓
Validación del samplesheet
        ↓
Remoción de adaptadores con porechop_abi
        ↓
Filtrado de lecturas largas con nanoq
        ↓
Reporte integrado con MultiQC
        ↓
FASTQ finales listos para análisis posterior
```

---
