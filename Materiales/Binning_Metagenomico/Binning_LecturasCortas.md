# Tutorial: Binning metagenómico de lecturas cortas con nf-core/mag

## 1. nf-core/mag: binning metagenómico

`nf-core/mag` es un pipeline bioinformático desarrollado por la comunidad de nf-core para el análisis reproducible de datos metagenómicos. Este pipeline permite realizar control de calidad, remoción de contaminación, ensamblaje metagenómico, binning, refinamiento de bins, evaluación de calidad, clasificación taxonómica y anotación funcional.

En este tutorial nos enfocaremos únicamente en la etapa de **binning metagenómico** a partir de ensamblajes previamente generados con lecturas cortas.

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

En este tutorial se usarán ensamblajes ya generados con **MEGAHIT** y se realizará binning con tres herramientas:

| Herramienta | Descripción general |
|---|---|
| `MetaBAT2` | Agrupa contigs usando cobertura diferencial y composición de tetranucleótidos. |
| `MaxBin2` | Usa modelos probabilísticos basados en composición de secuencia y cobertura para agrupar contigs. |
| `SemiBin2` | Usa aprendizaje semi-supervisado para mejorar la agrupación de contigs en metagenomas. |

Además, se usará:

| Herramienta | Función |
|---|---|
| `DAS Tool` | Refina y combina los bins generados por diferentes herramientas. |
| `CheckM2` | Evalúa la calidad de los MAGs estimando completitud y contaminación. |

---

## 3. Objetivo del tutorial

Realizar el **binning metagenómico de lecturas cortas** usando `nf-core/mag` a partir de ensamblajes precomputados.

En este tutorial se utilizarán:

- Lecturas paired-end previamente procesadas.
- Ensamblajes metagenómicos generados con `MEGAHIT`.
- `nf-core/mag` versión 5.4.2.
- `MetaBAT2`, `MaxBin2` y `SemiBin2` como herramientas de binning.
- `DAS Tool` para refinamiento de bins.
- `CheckM2` para evaluación de calidad de MAGs.

---

## 4. Ingreso al cluster

Ingrese al cluster de la Universidad de los Andes usando `ssh`:

```bash
ssh metagenomica_moderna@hypatia.uniandes.edu.co
```

La contraseña será compartida por el instructor durante la sesión.

---

## 5. Ubicación espacio de trabajo

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

Dentro de su carpeta personal, cree una carpeta para el taller:

```bash
mkdir Taller_Binning
```

Ingrese a la carpeta:

```bash
cd Taller_Binning
```

Cree una carpeta específica para lecturas cortas:

```bash
mkdir shortReads
```

Ingrese a la carpeta:

```bash
cd shortReads
```

Dentro de `shortReads`, cree tres carpetas:

```bash
mkdir Ensamblajes
mkdir Data
mkdir Secuencias
```

La estructura esperada será:

```text
Taller_Binning/
└── shortReads/
    ├── Ensamblajes/
    │   ├── MEGAHIT-CodigoID1.contigs.fa.gz
    │   └── MEGAHIT-CodigoID2.contigs.fa.gz
    │
    ├── Data/
    │   ├── samplesheet_reads.csv
    │   ├── samplesheet_ensamblaje.csv
    │   └── mag.config
    │
    ├── Secuencias/
    │   ├── CodigoID1_run0_host_removed.unmapped_1.fastq.gz
    │   ├── CodigoID1_run0_host_removed.unmapped_2.fastq.gz
    │   ├── CodigoID2_run0_host_removed.unmapped_1.fastq.gz
    │   └── CodigoID2_run0_host_removed.unmapped_2.fastq.gz
    │
    └── mag.sh
```

---

## 7. Secuencias asignadas

Cada estudiante trabajará con dos muestras.

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
| Rodriguez Rodriguez, Laura Daniela | SRR17048892 | SRR17048904 |
| Lopez Ramirez, Gina Pilar | SRR17048899 | SRR17048898 |
| Pedraza Herrera, Luz Adriana | SRR17048969 | SRR17048982 |
| Perez Mejia, Julian Andres | SRR17048929 | SRR17048958 |
| Pérez Rubiano, Claudia Constanza | SRR17048893 | SRR17048896 |
| Redondo Gonzalez, Marilin Yohandra | SRR17048984 | SRR17048921 |

---

## 8. Copiar las secuencias asignadas

Ingrese a la carpeta `Secuencias` de su espacio de trabajo:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Secuencias
```

Para copiar una muestra, use la siguiente estructura general:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Taxprofiler/Secuencias/CodigoID_run0_host_removed.unmapped_1.fastq.gz .

cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Taxprofiler/Secuencias/CodigoID_run0_host_removed.unmapped_2.fastq.gz .
```

Debe reemplazar `CodigoID` por el código real de su muestra.

Por ejemplo, si su muestra es `SRR17048892`, debe ejecutar:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Taxprofiler/Secuencias/SRR17048892_run0_host_removed.unmapped_1.fastq.gz .

cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Taxprofiler/Secuencias/SRR17048892_run0_host_removed.unmapped_2.fastq.gz .
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

## 9. Copiar los ensamblajes

Ingrese a la carpeta `Ensamblajes` de su espacio de trabajo:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Ensamblajes
```

Para copiar los ensamblajes, use la siguiente estructura general:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/MAG/output/Assembly/MEGAHIT/MEGAHIT-CodigoID.contigs.fa.gz .
```

Debe reemplazar `CodigoID` por el código real de su muestra.

Por ejemplo, si sus muestras son `SRR17048892` y `SRR17048893`, debe ejecutar:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/MAG/output/Assembly/MEGAHIT/MEGAHIT-SRR17048892.contigs.fa.gz .

cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/MAG/output/Assembly/MEGAHIT/MEGAHIT-SRR17048893.contigs.fa.gz .
```

Al finalizar, revise que los archivos se copiaron correctamente:

```bash
ls -lh
```
Como cada estudiante tiene dos muestras, deberían aparecer dos archivos `.contigs.fa.gz`.

---

## 10. Crear el archivo `samplesheet_reads.csv`

El archivo `samplesheet_reads.csv` le indica a `nf-core/mag` cuáles muestras se van a analizar y dónde se encuentran los archivos de lecturas procesadas.

Aunque en este tutorial se usarán ensamblajes precomputados, `nf-core/mag` también necesita las lecturas para mapearlas contra los contigs y calcular cobertura. Esta cobertura es necesaria para el binning metagenómico.

Ingrese a la carpeta `Data`:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Data
```

Copie el archivo base:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/shortReads/Data/samplesheet_reads.csv .
```

Abra el archivo con `nano`:

```bash
nano samplesheet_reads.csv
```

El archivo debe tener la siguiente estructura:

```csv
sample,group,short_reads_1,short_reads_2,long_reads,short_reads_platform
CodigoID1,0,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Secuencias/CodigoID1_run0_host_removed.unmapped_1.fastq.gz,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Secuencias/CodigoID1_run0_host_removed.unmapped_2.fastq.gz,,ILLUMINA
CodigoID2,1,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Secuencias/CodigoID2_run0_host_removed.unmapped_1.fastq.gz,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Secuencias/CodigoID2_run0_host_removed.unmapped_2.fastq.gz,,ILLUMINA
```

Debe modificar:

- `CodigoID1` por el código de su primera muestra.
- `CodigoID2` por el código de su segunda muestra.
- `Carpeta_personal` por el nombre de su carpeta asignada.

### Descripción de las columnas

| Columna | Descripción |
|---|---|
| `sample` | Nombre o identificador de la muestra. Debe coincidir con el `id` del archivo `samplesheet_ensamblaje.csv`. |
| `group` | Grupo de ensamblaje/binning. En este tutorial cada muestra tendrá un grupo diferente. |
| `short_reads_1` | Ruta absoluta al archivo FASTQ de la lectura forward o R1. |
| `short_reads_2` | Ruta absoluta al archivo FASTQ de la lectura reverse o R2. |
| `long_reads` | Ruta a lecturas largas. En este tutorial se deja vacío porque se usan lecturas cortas. |
| `short_reads_platform` | Plataforma de secuenciación. Para este taller se usará `ILLUMINA`. |

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
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/shortReads/Data/samplesheet_ensamblaje.csv .
```

Abra el archivo con `nano`:

```bash
nano samplesheet_ensamblaje.csv
```

El archivo debe tener la siguiente estructura:

```csv
id,group,assembler,fasta
CodigoID1,0,MEGAHIT,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Ensamblajes/MEGAHIT-CodigoID1.contigs.fa.gz
CodigoID2,1,MEGAHIT,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Ensamblajes/MEGAHIT-CodigoID2.contigs.fa.gz
```

Debe modificar:

- `CodigoID1` por el código de su primera muestra.
- `CodigoID2` por el código de su segunda muestra.
- `Carpeta_personal` por el nombre de su carpeta asignada.

### Descripción de las columnas

| Columna | Descripción |
|---|---|
| `id` | Identificador del ensamblaje. Debe coincidir con la columna `sample` del archivo `samplesheet_reads.csv`. |
| `group` | Grupo de ensamblaje/binning. Debe coincidir con la columna `group` del archivo `samplesheet_reads.csv`. |
| `assembler` | Ensamblador usado para generar los contigs. En este tutorial se usará `MEGAHIT`. |
| `fasta` | Ruta absoluta al archivo FASTA del ensamblaje. Puede estar comprimido en formato `.gz`. |

### Punto importante

El archivo de lecturas y el archivo de ensamblajes deben coincidir en `sample/id` y en `group`.

Ejemplo:

```text
samplesheet_reads.csv              samplesheet_ensamblaje.csv
sample = SRR17048892        →       id = SRR17048892
group  = 0                  →       group = 0
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
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/shortReads/Data/mag.config .
```

Abra el archivo:

```bash
nano mag.config
```
Cada estudiante debe modificar las rutas de `workDir` y `cacheDir`.

Agregar esta línea:

```groovy
workDir = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/work'
```

Reemplazando `Carpeta_personal` por su carpeta real.

También agregue esta línea:

```groovy
cacheDir = '/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/singularity_cache'
```

Reemplazando `Carpeta_personal` por su carpeta real.

Estas rutas son importantes porque Nextflow necesita escribir archivos temporales, logs, contenedores y archivos intermedios. Por esta razón, `workDir` y `cacheDir` deben estar en una carpeta donde el estudiante tenga permisos de escritura.

Para guardar y salir de `nano`:

```text
Ctrl + X
Y
Enter
```

---

## 13. Copiar el job principal

Una vez configurados los archivos anteriores, regrese desde `Data` hacia `shortReads`:

```bash
cd ../
```

Copie el job base:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller_Binning/shortReads/mag.sh .
```

Abra el archivo:

```bash
nano mag.sh
```

El archivo debe tener una estructura similar a esta:

```bash
#!/bin/bash

#SBATCH --job-name=nfcore_mag_binning
#SBATCH -p medium
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=18
#SBATCH --mem=120G
#SBATCH --time=8-00:00:00
#SBATCH --mail-user=jf.meza@uniandes.edu.co
#SBATCH --mail-type=ALL
#SBATCH -o mag_binning_job.o%j
#SBATCH -e mag_binning_job.e%j

module load jdk/19.0.2
module load singularity/3.7.1
module load nextflow/25.04.8
hash -r

nextflow run nf-core/mag -r 5.4.2 \
  -resume \
  -profile singularity \
  -c /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Data/mag.config \
  --input /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Data/samplesheet_reads.csv \
  --assembly_input /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Carpeta_personal/Taller_Binning/shortReads/Data/samplesheet_ensamblaje.csv \
  --outdir output \
  --skip_concoct \
  --skip_comebin \
  --skip_metabinner \
  --skip_metaeuk \
  --skip_gtdbtk \
  --skip_prokka \
  --bowtie2_mode="--very-sensitive" \
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

Desde la carpeta `shortReads`, envíe el job a SLURM:

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
less mag_binning_job.oJOBID
```

Y el archivo de error con:

```bash
less mag_binning_job.eJOBID
```

Debe reemplazar `JOBID` por el número real de su job.

---

## 15. Archivos de salida

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

## 16. Descripción general de los resultados

### 16.1 `Assembly/`

Esta carpeta contiene información relacionada con los ensamblajes usados por el pipeline.

Como en este tutorial se están usando ensamblajes precomputados mediante `--assembly_input`, el pipeline no vuelve a ensamblar las lecturas. Sin embargo, puede organizar, validar o usar los ensamblajes como entrada para los pasos posteriores.

Aquí se pueden encontrar archivos relacionados con:

- Contigs de entrada.
- Enlaces o copias de ensamblajes.
- Resultados de evaluación de ensamblaje si se ejecutan procesos como QUAST.

---

### 16.2 `Binning/`

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
Binning/
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
Tambien esta carpeta contiene los bins refinados por `DAS Tool`.

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

Por último esta carpeta contiene la carpeta "QC"

Esta carpeta contiene los resultados de evaluación de calidad de los bins o MAGs.

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
Quality_check/
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
