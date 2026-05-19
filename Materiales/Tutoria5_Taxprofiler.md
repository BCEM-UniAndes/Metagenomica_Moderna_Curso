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

## Construcción de base de datos con nf-core/createtaxdb

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

## Construcción de una base de datos personalizada con nf-core/createtaxdb

En esta sección construiremos una base de datos personalizada de protozoarios usando `nf-core/createtaxdb`. Esta base será utilizada posteriormente en `nf-core/taxprofiler` para realizar la clasificación taxonómica de lecturas metagenómicas.

El objetivo de este paso es generar una base compatible con:

- **Kraken2**, para clasificación taxonómica.
- **Bracken**, para estimación de abundancias taxonómicas.

---

## 1. Ubicarse en la carpeta personal del curso

Cada estudiante debe trabajar dentro de su carpeta personal asignada en el curso. Primero, ubíquese en su directorio correspondiente:

```bash
cd /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Nombre_Carpeta
```

Verifique que se encuentra en la ruta correcta:

```bash
pwd
```

---

## 2. Crear la estructura de carpetas del taller

Dentro de su carpeta personal, cree una carpeta llamada `Taller5`:

```bash
mkdir Taller5
```

Ingrese a la carpeta:

```bash
cd Taller5
```

Ahora cree una carpeta para la construcción de la base de datos:

```bash
mkdir Create_DB
```

Ingrese a esta carpeta:

```bash
cd Create_DB
```

Dentro de `Create_DB`, cree dos carpetas:

```bash
mkdir Archivos
mkdir Genomes
```

La estructura esperada será:

```text
Taller5/
└── Create_DB/
    ├── Archivos/
    └── Genomes/
```

---

## 3. Copiar los genomas de referencia

Los genomas de referencia ya se encuentran disponibles en la carpeta general del taller. Para copiarlos a su carpeta de trabajo, entre primero a la carpeta `Genomes`:

```bash
cd Genomes
```

Luego copie los archivos `.fna`:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/*.fna .
```

Verifique que los archivos fueron copiados correctamente:

```bash
ls
```

Debería observar varios archivos con extensión `.fna`, correspondientes a genomas de protozoarios.

---

## 4. Copiar el archivo `samplesheet.csv`

El archivo `samplesheet.csv` contiene la información necesaria para que `nf-core/createtaxdb` sepa qué genomas utilizar y qué identificador taxonómico corresponde a cada uno.

Desde la carpeta `Genomes`, regrese a `Create_DB` y entre a `Archivos`:

```bash
cd ../Archivos
```

Copie el archivo `samplesheet.csv`:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Archivos/samplesheet.csv .
```

Revise que el archivo esté presente:

```bash
ls
```

---

## 5. Revisar y modificar el archivo `samplesheet.csv`

Abra el archivo con `nano`:

```bash
nano samplesheet.csv
```

El archivo tiene una estructura similar a esta:

```csv
id,taxid,fasta_dna
Blastocystis_ST1_NandII,478820,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Blastocystis_ST1_NandII.fna
Blastocystis_ST3_DL,3128535,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Blastocystis_ST3_DL.fna
Blastocystis_ST4_WR1,944170,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Blastocystis_ST4_WR1.fna
Blastocystis_ST6_SSI754,944208,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Blastocystis_ST6_SSI754.fna
Blastocystis_ST7,12968,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Blastocystis_ST7.fna
Entamoeba_histolytica_HM1IMSS,294381,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Entamoeba_histolytica_HM1IMSS.fna
Entamoeba_dispar_SAW760,370354,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Entamoeba_dispar_SAW760.fna
Entamoeba_moshkovskii_Laredo,41668,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Entamoeba_moshkovskii_Laredo.fna
Giardia_DH,5741,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Giardia_DH.fna
Giardia_AWB,5741,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Giardia_AWB.fna
Giardia_GS,658858,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Giardia_GS.fna
Pentatrichomonas_hominis,5728,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Pentatrichomonas_hominis.fna
Cryptosporidium_parvum_IowaII,353152,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Cryptosporidium_parvum_IowaII.fna
Cryptosporidium_hominis_TU502,353151,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Cryptosporidium_hominis_TU502.fna
Cyclospora_cayetanensis_CcayRef3,88456,/hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Genomes/Cyclospora_cayetanensis_CcayRef3.fna
```

### Descripción de las columnas

| Columna | Descripción |
|---|---|
| `id` | Nombre o identificador del genoma de referencia. |
| `taxid` | Identificador taxonómico de NCBI correspondiente al organismo. |
| `fasta_dna` | Ruta completa al archivo FASTA del genoma en formato `.fna`. |

### Punto importante

Cada estudiante debe modificar la columna `fasta_dna` para que apunte a la ruta donde están sus propios genomas copiados.

Por ejemplo, si su carpeta es:

```bash
/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Nombre_Carpeta/Taller5/Create_DB/Genomes
```

las rutas del `samplesheet.csv` deben apuntar a esa ubicación.

Ejemplo:

```csv
Blastocystis_ST3_DL,3128535,/hpcfs/home/cursos/metagenomica_moderna/estudiantes/Nombre_Carpeta/Taller5/Create_DB/Genomes/Blastocystis_ST3_DL.fna
```

Para guardar los cambios en `nano`:

```text
Ctrl + X
Y
Enter
```

---

## 6. Copiar el job para construir la base de datos

Regrese una carpeta, desde `Archivos` hacia `Create_DB`:

```bash
cd ../
```

Copie el archivo del job principal:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/db.sh .
```

Verifique que el archivo esté en la carpeta:

```bash
ls
```

Debe aparecer:

```text
db.sh
```

---

## 7. Revisar y modificar el archivo `db.sh`

Abra el archivo con `nano`:

```bash
nano db.sh
```

El archivo debe tener una estructura similar a esta:

```bash
#!/bin/bash

# ###### Zona de Parámetros de solicitud de recursos a SLURM ############################

#SBATCH --job-name=createdb
#SBATCH -p short
#SBATCH -N 1
#SBATCH -n 1
#SBATCH --cpus-per-task=16
#SBATCH --mem=120G
#SBATCH --time=2-00:00:00
#SBATCH -o createdb_job.o%j
#SBATCH -e createdb_error.e%j

# Cargar módulos

module load jdk/19.0.2
module load singularity/3.7.1
module load nextflow/25.04.8

hash -r

nextflow -version
java -version

nextflow run nf-core/createtaxdb \
  -r 2.1.0 \
  -resume \
  -profile singularity \
  --input /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Archivos/samplesheet.csv \
  --dbname kraken2_Protozoa \
  --nodesdmp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Database/nodes.dmp \
  --namesdmp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Database/names.dmp \
  --accession2taxid /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Database/nucl_gb.accession2taxid \
  --build_bracken \
  --build_kraken2 \
  --outdir /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/output1
```

---

## 8. Explicación de los parámetros de SLURM

| Línea | Descripción |
|---|---|
| `#SBATCH --job-name=createdb` | Nombre del job en SLURM. |
| `#SBATCH -p short` | Partición o cola donde se enviará el trabajo. |
| `#SBATCH -N 1` | Número de nodos solicitados. |
| `#SBATCH -n 1` | Número de tareas. |
| `#SBATCH --cpus-per-task=16` | Número de CPU asignadas al proceso. |
| `#SBATCH --mem=120G` | Memoria RAM solicitada. |
| `#SBATCH --time=2-00:00:00` | Tiempo máximo del job: 2 días. |
| `#SBATCH -o createdb_job.o%j` | Archivo de salida estándar. |
| `#SBATCH -e createdb_error.e%j` | Archivo de errores. |

---

## 9. Explicación de los parámetros de nf-core/createtaxdb

| Parámetro | Descripción |
|---|---|
| `nextflow run nf-core/createtaxdb` | Ejecuta el pipeline `createtaxdb`. |
| `-r 2.1.0` | Usa la versión 2.1.0 del pipeline. |
| `-resume` | Permite reanudar la ejecución si el pipeline se interrumpe. |
| `-profile singularity` | Ejecuta el pipeline usando contenedores de Singularity. |
| `--input` | Ruta al archivo `samplesheet.csv`. |
| `--dbname` | Nombre que tendrá la base de datos generada. |
| `--nodesdmp` | Archivo `nodes.dmp` del taxdump de NCBI. |
| `--namesdmp` | Archivo `names.dmp` del taxdump de NCBI. |
| `--accession2taxid` | Archivo que relaciona accesiones de secuencias con taxid. |
| `--build_bracken` | Indica que se debe construir una base compatible con Bracken. |
| `--build_kraken2` | Indica que se debe construir una base compatible con Kraken2. |
| `--outdir` | Carpeta donde se guardarán los resultados del pipeline. |

---

## 10. Rutas que deben modificar

Cada estudiante debe modificar las rutas que apuntan a sus propios archivos.

En particular, deben cambiar:

```bash
--input /ruta/a/su/Taller5/Create_DB/Archivos/samplesheet.csv
```

y:

```bash
--outdir /ruta/a/su/Taller5/Create_DB/output1
```

Por ejemplo:

```bash
--input /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Nombre_Carpeta/Taller5/Create_DB/Archivos/samplesheet.csv
```

```bash
--outdir /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Nombre_Carpeta/Taller5/Create_DB/output1
```

Recuerde reemplazar `Nombre_Carpeta` por el nombre real de su carpeta personal.

---

## 11. Rutas que NO deben modificar

Las siguientes rutas corresponden a archivos de taxonomía compartidos del curso. Por lo tanto, no es necesario modificarlas:

```bash
--nodesdmp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Database/nodes.dmp
```

```bash
--namesdmp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Database/names.dmp
```

```bash
--accession2taxid /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Database/nucl_gb.accession2taxid
```

Estos archivos contienen información taxonómica de referencia necesaria para que el pipeline pueda asociar las secuencias con sus identificadores taxonómicos.

---

## 12. Ejemplo de job modificado para un estudiante

A continuación se muestra un ejemplo de cómo debería quedar el bloque principal del job para un estudiante:

```bash
nextflow run nf-core/createtaxdb \
  -r 2.1.0 \
  -resume \
  -profile singularity \
  --input /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Nombre_Carpeta/Taller5/Create_DB/Archivos/samplesheet.csv \
  --dbname kraken2_Protozoa \
  --nodesdmp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Database/nodes.dmp \
  --namesdmp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Database/names.dmp \
  --accession2taxid /hpcfs/home/cursos/metagenomica_moderna/Talleres/Taller5/Create_DB/Database/nucl_gb.accession2taxid \
  --build_bracken \
  --build_kraken2 \
  --outdir /hpcfs/home/cursos/metagenomica_moderna/estudiantes/Nombre_Carpeta/Taller5/Create_DB/output1
```

---

## 13. Ejecutar el job

Una vez revisado y modificado el archivo `db.sh`, guarde los cambios en `nano`:

```text
Ctrl + X
Y
Enter
```

Luego envíe el job a SLURM:

```bash
sbatch db.sh
```

---

## 14. Revisar el estado del job

Para revisar si el job está corriendo:

```bash
squeue -u $USER
```

También puede revisar los archivos de salida y error:

```bash
ls
```

Deberían aparecer archivos similares a:

```text
createdb_job.oID
createdb_error.eID
```

Para ver el contenido del archivo de salida:

```bash
less createdb_job.oID
```

Para ver el archivo de error:

```bash
less createdb_error.eID
```

Reemplace `ID` por el número real del job asignado por SLURM.

---

## 15. Resultado esperado

Si el pipeline finaliza correctamente, se generará una carpeta de salida llamada:

```text
output1
```

Dentro de esta carpeta deberían encontrarse resultados como:

```text
output1/
├── kraken2/
├── bracken/
├── multiqc/
└── pipeline_info/
```

Las carpetas más importantes son:

| Carpeta | Contenido |
|---|---|
| `kraken2/` | Base de datos construida para Kraken2. |
| `bracken/` | Base de datos compatible con Bracken. |
| `multiqc/` | Reporte general del pipeline. |
| `pipeline_info/` | Información de ejecución, parámetros y trazabilidad del workflow. |

---

## 16. Resumen del flujo

```text
Crear carpetas de trabajo
        ↓
Copiar genomas de referencia
        ↓
Copiar y modificar samplesheet.csv
        ↓
Copiar y modificar db.sh
        ↓
Ejecutar nf-core/createtaxdb con sbatch
        ↓
Obtener base de datos Kraken2/Bracken
        ↓
Usar la base en nf-core/taxprofiler
```

Al finalizar este paso, cada estudiante tendrá una base de datos personalizada de protozoarios lista para ser utilizada en el análisis taxonómico con `nf-core/taxprofiler`.








