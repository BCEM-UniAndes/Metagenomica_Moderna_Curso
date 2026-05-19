# Introducción a nf-core/taxprofiler

`nf-core/taxprofiler` es un flujo de trabajo bioinformático desarrollado bajo el ecosistema **nf-core** y ejecutado con **Nextflow**. Su objetivo principal es realizar la **clasificación taxonómica de muestras metagenómicas**, usando diferentes herramientas especializadas como Kraken2, Bracken, Kaiju, Centrifuge, MetaPhlAn, entre otras.

En este taller utilizaremos `taxprofiler` para analizar lecturas metagenómicas previamente procesadas. Es decir, las secuencias ya pasaron por pasos previos como control de calidad y remoción de hospedero. Por esta razón, en esta práctica no realizaremos trimming, filtrado ni eliminación de contaminantes humanos dentro del pipeline.

De forma general, el flujo de trabajo recibe tres elementos principales:

1. Un archivo `samplesheet.csv`, donde se indican las muestras y las rutas a los archivos FASTQ.
2. Un archivo `db.csv`, donde se especifican las bases de datos taxonómicas que se van a utilizar.
3. Un archivo de configuración `nextflow.config`, donde se ajustan recursos computacionales y parámetros del entorno de ejecución.

En esta práctica correremos principalmente:

- **Kraken2**, para asignar taxonomía a las lecturas mediante comparación contra bases de datos de referencia.
- **Bracken**, para reestimar abundancias taxonómicas a partir de los resultados de Kraken2.
- **Krona**, para generar visualizaciones interactivas de la composición taxonómica.
- **Taxpasta**, para estandarizar y enriquecer las tablas taxonómicas con nombres, rangos y linajes.

El resultado final será una carpeta de salida con reportes taxonómicos, tablas de abundancia, archivos interactivos de visualización y reportes generales del flujo de trabajo. Estos archivos permitirán explorar qué organismos están presentes en cada muestra y comparar los perfiles taxonómicos entre muestras.

## Construcción de una base de datos personalizada con nf-core/createtaxdb

Antes de ejecutar `nf-core/taxprofiler`, es necesario definir contra qué bases de datos se van a comparar las lecturas metagenómicas. Aunque existen bases de datos generales ya construidas, en este taller vamos a crear una base de datos personalizada enfocada en organismos de interés para el análisis taxonómico.

Para esto utilizaremos `nf-core/createtaxdb`, un flujo de trabajo de nf-core diseñado para construir bases de datos taxonómicas personalizadas a partir de un conjunto de genomas de referencia. Este pipeline permite preparar archivos FASTA y construir bases compatibles con diferentes clasificadores metagenómicos, incluyendo Kraken2 y Bracken, que serán las herramientas principales utilizadas en este taller.

<p align="center">
  <img src="https://raw.githubusercontent.com/nf-core/createtaxdb/master/docs/images/nf-core-createtaxdb_logo_light.png" width="450">
</p>

De forma general, `createtaxdb` requiere tres componentes principales:

1. Un archivo `samplesheet.csv`, donde se indican los genomas de referencia que se usarán para construir la base.
2. Archivos de taxonomía de NCBI, como `nodes.dmp`, `names.dmp` y `nucl_gb.accession2taxid`.
3. Parámetros que indiquen qué bases se desean construir, por ejemplo `--build_kraken2` y `--build_bracken`.

En este taller construiremos una base de datos personalizada para clasificación taxonómica de protozoarios. Esta base será usada posteriormente por `nf-core/taxprofiler` para clasificar las lecturas metagenómicas con Kraken2 y estimar abundancias con Bracken.

El flujo general será:

```text
Genomas de referencia (.fna)
        ↓
samplesheet.csv con ID, taxid y ruta al FASTA
        ↓
nf-core/createtaxdb
        ↓
Base de datos Kraken2/Bracken
        ↓
nf-core/taxprofiler
        ↓
Clasificación taxonómica de las muestras
