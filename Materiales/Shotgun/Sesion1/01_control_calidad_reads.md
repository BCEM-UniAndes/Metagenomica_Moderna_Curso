# Control de calidad de lecturas metagenómicas con `nf-core/mag`

## 1. Objetivo de esta sección

En esta primera parte del curso trabajaremos la etapa de **control de calidad de lecturas metagenómicas** usando `nf-core/mag`. El objetivo es preparar archivos FASTQ de alta calidad para análisis posteriores, eliminando adaptadores, recortando bases de baja calidad, removiendo contaminantes técnicos como **PhiX** y, cuando sea necesario, eliminando lecturas del **huésped**. En `nf-core/mag`, esta etapa se apoya principalmente en **fastp**, **FastQC**, **Bowtie2** y **MultiQC**.

## 2. ¿Qué hace la etapa de calidad en `nf-core/mag`?

La etapa de calidad de `nf-core/mag` realiza, para lecturas cortas, cuatro tareas principales:

1. **Evaluación inicial de calidad** con **FastQC** sobre los FASTQ crudos.
2. **Recorte de adaptadores y filtrado de calidad** con **fastp** por defecto.
3. **Remoción de lecturas PhiX** mediante alineamiento con **Bowtie2**.
4. **Remoción de lecturas del huésped** usando **Bowtie2** contra una referencia especificada por el usuario.

Al final, los resultados quedan integrados en un **reporte MultiQC**, que resume métricas clave antes y después del procesamiento.

## 3. Estructura sugerida de directorios

Para mantener el trabajo ordenado en el curso, se propone la siguiente estructura:

```bash
curso_metagenomica/
├── 01_raw_reads/
│   └── fastq/
├── 02_metadata/
│   └── samplesheet.csv
├── 03_params/
│   ├── params_qc.yaml
│   └── custom_qc.config
├── 04_results/
│   └── mag_qc/
└── 05_logs/
