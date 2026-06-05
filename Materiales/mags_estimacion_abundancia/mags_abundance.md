# Estimación de abundancia de MAGs

La estimación de abundancia de MAGs consiste en mapear los reads de secuenciación contra un conjunto de genomas representativos. El número de reads que mapea contra cada MAG se usa como una medida de su abundancia. Para comparar entre muestras, estos conteos pueden normalizarse posteriormente según el número total de reads mapeados por muestra, obteniendo estimaciones de abundancia relativa.

En esta sección se usarán tres herramientas principales. **Bowtie2** se usará para construir el índice de los MAGs representativos y mapear los reads contra ellos. **samtools** se usará para procesar los archivos SAM/BAM generados durante el mapeo. **msamtools** se usará para generar tablas de abundancia a partir de los archivos BAM filtrados.

## Configuración de directorios de salida

Cree una nueva carpeta llamada `mags_abundance_estimation`. Dentro de esta carpeta, cree los siguientes subdirectorios:

```bash
mkdir -p bowtie_index_out
mkdir -p bowtie_mapping_out
mkdir -p msamtools_out
```

La estructura esperada será:

```bash
mags_abundance_estimation/
├── bowtie_index_out/
├── bowtie_mapping_out/
└── msamtools_out/
```

## Crear el archivo FASTA con los MAGs representativos

Antes de construir el índice de Bowtie2, todos los MAGs representativos deben concatenarse en un solo archivo FASTA. Para esto, use el script `concat_mags.sh`, disponible en la carpeta `helper_scripts`.

Copie el script a su carpeta `mags_abundance_estimation`:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/helper_scripts/concat_mags.sh mags_abundance_estimation/
```

Abra el script y modifique la variable `dereplicated_genomes` con la ruta correcta a la carpeta que contiene los MAGs representativos generados por dRep:

Ejecute el script:

```bash
bash concat_mags.sh
```

Este paso generará un archivo llamado `representative_genomes.fasta` que contendrá todos los MAGs representativos concatenados y será usado para construir el índice de `Bowtie2`.

## Crear el índice de Bowtie2

Para mapear los reads contra los MAGs representativos, primero se debe crear un índice de Bowtie2 a partir del archivo `representative_genomes.fasta`.

Un índice es una versión procesada y optimizada del archivo FASTA de referencia. En lugar de buscar directamente en toda la secuencia cada vez que se mapea un read, Bowtie2 usa este índice para encontrar coincidencias de manera mucho más rápida y eficiente.

Cree un script llamado `run_bowtie2_index.sh`:

```bash
nano run_bowtie2_index.sh
```

Copie el siguiente contenido y modifique la variable `representative_genomes` con la ruta correcta al archivo `representative_genomes.fasta`:

```bash
#!/bin/bash

#SBATCH -J bowtie_index
#SBATCH -D .
#SBATCH -e bowtie_index_%j.err
#SBATCH -o bowtie_index_%j.out
#SBATCH --cpus-per-task=8
#SBATCH --time=2:00:00	
#SBATCH --mem=6000

module load bowtie2/2.4.5 

representative_genomes="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_abundance_estimation/representative_genomes.fasta"

bowtie2-build $representative_genomes bowtie_index_out/INDEX
```

Después de crear y guardar el script, dele permisos de ejecución y envíelo al clúster:

```bash
chmod +x run_bowtie2_index.sh
sbatch run_bowtie2_index.sh
```

Cuando termine el proceso, la carpeta `bowtie_index_out` contendrá archivos como:

```bash
bowtie_index_out/
├── INDEX.1.bt2
├── INDEX.2.bt2
├── INDEX.3.bt2
├── INDEX.4.bt2
├── INDEX.rev.1.bt2
└── INDEX.rev.2.bt2
```

Estos archivos forman el índice de Bowtie2, una representación comprimida de los MAGs representativos que permite mapear reads de forma rápida y eficiente.

## Crear el archivo `manifest.csv`

Antes de ejecutar el mapeo con Bowtie2, se debe crear un archivo llamado `manifest.csv`. Este archivo contiene la información de las muestras y las rutas a los archivos de reads pareados que serán mapeados contra los MAGs representativos.

El `manifest.csv` será usado por el script de mapeo para identificar, por cada muestra, cuál archivo corresponde al read forward (`R1`) y cuál corresponde al read reverse (`R2`).

Para generar este archivo, primero cree un archivo de texto con las rutas de todos los reads limpios que se van a procesar de la siguiente manera:

```bash
ls -1 -d /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/clean_reads/*.fastq.gz > file_path.txt
```

Este comando genera un archivo llamado `file_path.txt`, con una ruta por línea.

Luego copie el script `generate_manifest.sh` desde la carpeta `helper_scripts` a su carpeta `mags_abundance_estimation`:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/helper_scripts/generate_manifest.sh mags_abundance_estimation
```

Después, ejecute el script usando como entrada el archivo `file_path.txt`:

```bash
bash generate_manifest.sh file_path.txt
```

Esto generará un archivo llamado:

```bash
manifest.csv
```

Puede revisar su contenido con:

```bash
head manifest.csv
```

El archivo debe tener una estructura similar a esta:

```csv
sample,R1,R2
SRR17048892,/ruta/a/reads_limpios/SRR17048892_1.fastq.gz,/ruta/a/reads_limpios/SRR17048892_2.fastq.gz
SRR17048902,/ruta/a/reads_limpios/SRR17048902_1.fastq.gz,/ruta/a/reads_limpios/SRR17048902_2.fastq.gz
```

Este archivo `manifest.csv` será usado posteriormente por el script de mapeo con Bowtie2.


## Mapear reads contra los MAGs representativos

Después de crear el índice y archivo de manifiesto, el siguiente paso es mapear los reads limpios de cada muestra contra los MAGs representativos. Para esto, cree un script llamado `run_bowtie2_mapping.sh`:

```bash
nano run_bowtie2_mapping.sh
```

Copie el siguiente contenido y modifique las variables `manifest` e `index` con las rutas correctas:

```bash
#!/bin/bash

#SBATCH -J bowtie_mapping
#SBATCH -D .
#SBATCH -e bowtie_mapping_%j.err
#SBATCH -o bowtie_mapping_%j.out
#SBATCH --cpus-per-task=6
#SBATCH --time=8:00:00	
#SBATCH --mem=8000

module load bowtie2/2.4.5 samtools/1.16.1 
source /hpcfs/home/cursos/metagenomica_moderna/conda/bin/activate
conda activate msamtools

manifest="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_abundance_estimation/manifest.csv"
index="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_abundance_estimation/bowtie_index"

# Loop through each line of the manifest file (skipping the header)
tail -n +2 "$manifest" | while IFS=',' read -r sample R1 R2; do
        
    # Bowtie2 mapping
    bowtie2 --threads 6 -x $index/INDEX -1 "$R1" -2 "$R2" -S bowtie_mapping/${sample}.sam

    # Convert SAM to BAM
    samtools view -F 4 -bS bowtie_mapping/${sample}.sam > bowtie_mapping/${sample}-RAW.bam

    # Using msamtools to filter aligments
    msamtools filter -b -l 80 -p 95 -z 80 bowtie_mapping/${sample}-RAW.bam > bowtie_mapping/${sample}.filtered.bam
    
    # Sort BAM file by name (needed for masamtools profile)
    samtools sort -n -@ 4 bowtie_mapping/${sample}.filtered.bam -o bowtie_mapping/${sample}.sorted.bam
   
    rm bowtie_mapping/${sample}.sam
    rm bowtie_mapping/${sample}-RAW.bam
    rm bowtie_mapping/${sample}.filtered.bam
    
done

```

Después de guardar el script, dele permisos de ejecución y envíelo al clúster:

```bash
chmod +x run_bowtie2_mapping.sh
sbatch run_bowtie2_mapping.sh
```

Este script realiza cinco pasos principales. Primero, mapea los reads pareados contra el índice de Bowtie2. Luego convierte el archivo SAM a BAM y conserva únicamente los reads que mapearon. Después filtra los alineamientos con `msamtools`, conservando reads de al menos 80 bp, con al menos 95% de identidad y con al menos 80% de la longitud del read alineada. Posteriormente ordena el archivo BAM por nombre, un requisito para `msamtools profile`. Finalmente elimina archivos intermedios para ahorrar espacio.

Cuando termine el proceso, la carpeta `bowtie_mapping_out` contendrá archivos como:

```bash
bowtie_mapping_out/
└── sample.sorted.bam
```

Estos archivos contienen los alineamientos filtrados de alta confianza y serán usados para estimar la abundancia de los MAGs.

## Crear la tabla contig-to-bin para msamtools

Para estimar la abundancia por MAG, `msamtools profile` necesita saber a qué MAG pertenece cada contig. Esta información se proporciona mediante un archivo `.stb`, también conocido como tabla **scaffold-to-bin** o **contig-to-bin**.

El archivo `.stb` debe tener dos columnas: la primera contiene el identificador del MAG y la segunda el identificador del contigs. De esta manera, `msamtools` puede sumar la señal de mapeo de todos los contigs que forman parte de un mismo MAG.

Para generar esta tabla se usará el script `parse_stb.py`, desarrollado por los desarrolladores de **inStrain**. Este script permite leer archivos FASTA de genomas o MAGs y extraer automáticamente la relación entre cada contig y el MAG correspondiente.

Primero, copie el script desde la carpeta `helper_scripts` a su carpeta `mags_abundance_estimation`:

```bash
cp /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/helper_scripts/parse_stb.py mags_abundance_estimation
```

Ahora ejecute el script indicando la carpeta donde están los MAGs representativos seleccionados por dRep:

```bash
python parse_stb.py -f /hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_drep/drep_out/dereplicated_genomes/* -o representative_genomes.stb
```

Este comando procesa los archivos FASTA de los MAGs representativos, extrae los identificadores de los contigs y los asigna al MAG correspondiente. El archivo generado se llamará:

```bash
representative_genomes.stb
```

Este archivo será usado como entrada para `msamtools profile` durante la estimación de abundancia de los MAGs.

## Ejecutar msamtools para estimar abundancia

Una vez generada la tabla `representative_genomes.stb`, se puede estimar la abundancia de los MAGs en cada muestra.

Cree un script llamado `run_msamtools_profile.sh`:

```bash
nano run_msamtools_profile.sh
```

Copie el siguiente contenido y modifique las variables `manifest` y `stb_representatives` con las rutas correctas:

```bash
#!/bin/bash

#SBATCH -J msamtools_profile
#SBATCH -D .
#SBATCH -e msamtools_profile_%j.err
#SBATCH -o msamtools_profile_%j.out
#SBATCH --cpus-per-task=8
#SBATCH --time=1:00:00	
#SBATCH --mem=1000

source /hpcfs/home/cursos/metagenomica_moderna/conda/bin/activate
conda activate msamtools

manifest="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_abundance_estimation/manifest.csv"
stb_representatives="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_abundance_estimation/representative_genomes.stb"

# Loop through each line of the manifest file (skipping the header)
tail -n +2 "$manifest" | while IFS=',' read -r sample R1 R2; do
    
    msamtools profile bowtie_mapping/${sample}.sorted.bam --label="$sample" --unit=ab --nolen --genome $stb_representatives -o msamtools_out/$sample.profile.txt.gz 

done
```

Después de guardar el script, dele permisos de ejecución y envíelo al clúster:

```bash
chmod +x run_msamtools_profile.sh
sbatch run_msamtools_profile.sh
```

La opción `--unit=ab` indica que la abundancia se reportará como conteos crudos de reads. La opción `--nolen` indica que no se aplicará normalización por longitud del genoma.

## Descripción de la salida

Cuando termine la estimación de abundancia, la carpeta `msamtools_out` contendrá archivos comprimidos con las tablas de abundancia para cada muestra:

```bash
msamtools_out/
└── sample.profile.txt.gz
```

Para descomprimir y revisar los archivos, use:

```bash
gunzip msamtools_out/*.gz
```

Los archivos resultantes contienen estadísticas de mapeo y estimaciones de abundancia para cada MAG representativo analizado.
