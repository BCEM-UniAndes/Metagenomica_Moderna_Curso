# Tutorial 00. Introducción a Linux y al uso del clúster

## Objetivo del tutorial

Este tutorial tiene como propósito introducir los conceptos básicos de Linux y del uso del clúster de cómputo de alto rendimiento Hypatia de la Universidad de los Andes, necesarios para desarrollar análisis bioinformáticos en metagenómica de lecturas cortas y largas.

Al finalizar este tutorial, el estudiante deberá ser capaz de:

* Comprender qué es un clúster de cómputo y por qué se utiliza en bioinformática.
* Identificar conceptos básicos como nodo, CPU, memoria RAM, partición, cola y job.
* Conectarse al clúster mediante SSH.
* Navegar por el sistema de archivos usando comandos básicos de Linux.
* Crear, copiar, mover, visualizar y eliminar archivos y carpetas.
* Transferir archivos entre el computador local y el clúster.
* Escribir y enviar un job básico usando Slurm.
* Consultar el estado de los trabajos enviados al clúster.

---

# 1. ¿Por qué necesitamos Linux en metagenómica?

La mayoría de herramientas utilizadas en bioinformática y metagenómica se ejecutan desde la terminal de Linux. Esto incluye programas para:

* Control de calidad de lecturas: `FastQC`, `fastp`, `NanoPlot`.
* Ensamblaje metagenómico: `MEGAHIT`, `metaSPAdes`, `Flye`, `metaFlye`.
* Clasificación taxonómica: `Kraken2`, `Bracken`, `Kaiju`, `Centrifuge`, `MetaPhlAn`.
* Anotación funcional: `eggNOG-mapper`, `PROKKA`, `Bakta`.
* Binning y recuperación de MAGs: `MetaBAT2`, `MaxBin2`, `CONCOCT`, `DAS Tool`.
* Ejecución de pipelines reproducibles: `Nextflow`, `Snakemake`, `nf-core`, `Quimme2`.

En metagenómica los archivos suelen ser muy grandes. Un solo archivo FASTQ puede ocupar varios GB y algunos análisis requieren muchas CPU, memoria RAM y varios días de ejecución. Por esta razón, los análisis no suelen hacerse en computadores personales, sino en clústeres de cómputo.

---

# 2. ¿Qué es un clúster de cómputo?

Un clúster es un conjunto de computadores conectados entre sí que trabajan como una infraestructura de cómputo compartida. En lugar de ejecutar los análisis directamente en un computador personal, los usuarios envían tareas al clúster para que sean ejecutadas en nodos especializados.

En términos simples:

> Un clúster es como un conjunto de computadores potentes organizados para ejecutar tareas pesadas de forma ordenada, eficiente y compartida entre muchos usuarios.

En bioinformática, un clúster permite ejecutar análisis que requieren:

* Muchas CPU.
* Gran cantidad de memoria RAM.
* Mucho espacio de almacenamiento.
* Ejecuciones largas.
* Procesamiento paralelo de muchas muestras.

---

# 3. Conceptos básicos del clúster

## 3.1 Nodo

Un nodo es una máquina individual dentro del clúster. Cada nodo tiene sus propios recursos computacionales, como:

* CPU o procesadores.
* Memoria RAM.
* Disco temporal o local.
* En algunos casos, GPU.

Ejemplo: si el clúster tiene 20 nodos, significa que tiene 20 computadores disponibles para ejecutar trabajos.

---

## 3.2 CPU o core

Una CPU o core es una unidad de procesamiento. Muchos programas bioinformáticos pueden usar varios cores al mismo tiempo para acelerar el análisis.

Por ejemplo:

```bash
fastp --thread 8
```

En este caso, `fastp` utilizaría 8 CPU o threads.

No siempre más CPU significa mayor velocidad. Algunos programas escalan bien con muchas CPU, mientras que otros no.

---

## 3.3 Memoria RAM

La memoria RAM es el espacio temporal que usa un programa mientras se está ejecutando.

Algunos análisis metagenómicos requieren mucha memoria, especialmente:

* Ensamblaje metagenómico.
* Construcción de bases de datos.
* Clasificación taxonómica con bases grandes.
* Binning de MAGs.
* Anotación funcional masiva.

Si se solicita poca memoria, el job puede fallar con errores como:

```text
Out of memory
Killed
Exceeded memory limit
```

---

## 3.4 Job

Un job es una tarea que se envía al clúster para ser ejecutada.

Un job puede ser algo simple, como listar archivos, o algo pesado, como ensamblar un metagenoma.

Ejemplos de jobs:

* Ejecutar control de calidad con `FastQC`.
* Ensamblar lecturas con `MEGAHIT`.
* Clasificar lecturas con `Kraken2`.
* Ejecutar un pipeline completo de `nf-core/taxprofiler`.

---

## 3.5 Scheduler o gestor de trabajos

El scheduler es el sistema encargado de organizar los jobs enviados por los usuarios.

En muchos clústeres se utiliza **Slurm**.

Slurm decide:

* Cuándo se ejecuta un job.
* En qué nodo se ejecuta.
* Cuántas CPU recibe.
* Cuánta memoria puede usar.
* Cuánto tiempo máximo puede durar.

Los usuarios no ejecutan análisis pesados directamente en el nodo de login. En su lugar, crean un script de trabajo y lo envían al scheduler.

---

# 4. Particiones del clúster

Las particiones son grupos de nodos organizados según sus características y límites de uso. También pueden entenderse como colas de trabajo.

Cada partición puede tener límites diferentes de:

* Tiempo máximo de ejecución.
* Memoria disponible.
* Número de CPU.
* Tipo de nodo.
* Prioridad o finalidad.

Un ejemplo general de particiones es:

| Partición | Uso típico               | Tiempo máximo aproximado | Ejemplos de análisis                                      |
| --------- | ------------------------ | -----------------------: | --------------------------------------------------------- |
| `short`   | Trabajos rápidos         |             Hasta 2 días | FastQC, scripts pequeños, revisión de archivos            |
| `medium`  | Trabajos intermedios     |              Varios días | Kraken2, Bracken, filtrados, algunos ensamblajes pequeños |
| `long`    | Trabajos largos          |     Hasta varias semanas | Pipelines largos, anotación, clasificación masiva         |
| `bigmem`  | Trabajos de alta memoria |                 Variable | metaSPAdes, bases de datos grandes, ensamblajes pesados   |
| `gpu`     | Trabajos con GPU         |                 Variable | Herramientas que requieran aceleración gráfica o CUDA     |

> Nota: los nombres y límites exactos dependen de la configuración del clúster de la universidad. Antes de enviar un job, se recomienda revisar las particiones disponibles con `sinfo`.

Para consultar las particiones disponibles:

```bash
sinfo
```

Ejemplo de salida:

```text
PARTITION AVAIL  TIMELIMIT  NODES  STATE NODELIST
short        up 2-00:00:00      4   idle  node[01-04]
medium       up 7-00:00:00      6   mix   node[05-10]
long         up 30-00:00:00     4   idle  node[11-14]
bigmem       up 15-00:00:00     2   idle  node[15-16]
```

---

# 5. Conexión al clúster mediante SSH

Para conectarse al clúster se usa el comando `ssh` desde una terminal.

La estructura general es:

```bash
ssh usuario@servidor
```

Ejemplo:

```bash
ssh miusuario@cluster.uniandes.edu.co
```

Después de ejecutar el comando, el sistema pedirá la contraseña institucional o el método de autenticación configurado.

Una vez dentro, se estará ubicado en el nodo de login.

> Importante: el nodo de login se usa para preparar archivos, revisar resultados, editar scripts y enviar jobs. No debe usarse para ejecutar análisis pesados.

---

# 6. Estructura básica de archivos en Linux

Linux organiza los archivos en una estructura jerárquica de carpetas.

Algunas rutas comunes son:

| Ruta                  | Significado                                 |
| --------------------- | ------------------------------------------- |
| `/home/usuario`       | Carpeta personal del usuario                |
| `/hpcfs/home/usuario` | Carpeta de trabajo en algunos clústeres HPC |
| `/tmp`                | Carpeta temporal                            |
| `.`                   | Carpeta actual                              |
| `..`                  | Carpeta anterior                            |
| `~`                   | Carpeta personal del usuario                |

Para saber en qué carpeta estamos:

```bash
pwd
```

Ejemplo de salida:

```text
/hpcfs/home/usuario
```

---

# 7. Comandos básicos de Linux

## 7.1 Ver la ruta actual: `pwd`

```bash
pwd
```

Muestra la carpeta actual.

---

## 7.2 Listar archivos: `ls`

```bash
ls
```

Lista los archivos y carpetas del directorio actual.

Opciones útiles:

```bash
ls -l
```

Muestra archivos en formato detallado.

```bash
ls -lh
```

Muestra tamaños en formato legible, por ejemplo MB o GB.

```bash
ls -ltr
```

Ordena archivos por fecha de modificación.

```bash
ls *.fastq.gz
```

Lista archivos que terminan en `.fastq.gz`.

---

## 7.3 Cambiar de carpeta: `cd`

```bash
cd nombre_carpeta
```

Ejemplo:

```bash
cd metagenomica
```

Volver una carpeta atrás:

```bash
cd ..
```

Ir a la carpeta personal:

```bash
cd ~
```

Ir a una ruta absoluta:

```bash
cd /hpcfs/home/usuario/proyecto_metagenomica
```

---

## 7.4 Crear carpetas: `mkdir`

```bash
mkdir resultados
```

Crear varias carpetas:

```bash
mkdir raw_data qc_results scripts logs
```

Crear carpetas anidadas:

```bash
mkdir -p proyecto_metagenomica/{raw_data,results,scripts,logs}
```

---

## 7.5 Copiar archivos: `cp`

```bash
cp archivo.txt copia_archivo.txt
```

Copiar un archivo a otra carpeta:

```bash
cp muestra1.fastq.gz raw_data/
```

Copiar una carpeta completa:

```bash
cp -r carpeta_original carpeta_copia
```

---

## 7.6 Mover o renombrar archivos: `mv`

Mover un archivo:

```bash
mv archivo.txt results/
```

Renombrar un archivo:

```bash
mv viejo_nombre.txt nuevo_nombre.txt
```

---

## 7.7 Eliminar archivos y carpetas: `rm`

Eliminar un archivo:

```bash
rm archivo.txt
```

Eliminar una carpeta y todo su contenido:

```bash
rm -r carpeta
```

Eliminar sin pedir confirmación:

```bash
rm -rf carpeta
```

> Advertencia: `rm -rf` debe usarse con mucho cuidado. En Linux, los archivos eliminados desde la terminal normalmente no van a una papelera de reciclaje.

---

## 7.8 Visualizar archivos pequeños: `cat`

```bash
cat archivo.txt
```

Muestra todo el contenido del archivo en pantalla. Se recomienda solo para archivos pequeños.

---

## 7.9 Visualizar archivos página por página: `more` y `less`

```bash
more archivo.txt
```

```bash
less archivo.txt
```

Con `less`, se puede navegar usando:

* Flecha arriba/abajo.
* Barra espaciadora para avanzar.
* `q` para salir.

---

## 7.10 Ver las primeras líneas: `head`

```bash
head archivo.txt
```

Ver las primeras 20 líneas:

```bash
head -n 20 archivo.txt
```

Ejemplo útil para FASTQ:

```bash
zcat muestra_R1.fastq.gz | head
```

---

## 7.11 Ver las últimas líneas: `tail`

```bash
tail archivo.log
```

Ver las últimas 50 líneas:

```bash
tail -n 50 archivo.log
```

Seguir un archivo en tiempo real:

```bash
tail -f archivo.log
```

Esto es muy útil para revisar logs de jobs mientras se están ejecutando.

---

## 7.12 Contar líneas, palabras y caracteres: `wc`

```bash
wc archivo.txt
```

Contar solo líneas:

```bash
wc -l archivo.txt
```

Ejemplo para contar secuencias en un FASTQ comprimido:

```bash
zcat muestra.fastq.gz | wc -l
```

Como cada lectura FASTQ ocupa 4 líneas, el número aproximado de lecturas sería:

```bash
zcat muestra.fastq.gz | wc -l
```

Luego se divide entre 4.

---

## 7.13 Buscar texto dentro de archivos: `grep`

```bash
grep "palabra" archivo.txt
```

Buscar una muestra en un archivo CSV:

```bash
grep "DCL_001" samplesheet.csv
```

Buscar ignorando mayúsculas/minúsculas:

```bash
grep -i "kraken" archivo.log
```

Buscar errores en logs:

```bash
grep -i "error" *.log
```

---

## 7.14 Comprimir y descomprimir archivos

Comprimir con gzip:

```bash
gzip archivo.fastq
```

Descomprimir:

```bash
gunzip archivo.fastq.gz
```

Ver archivos comprimidos sin descomprimir:

```bash
zcat archivo.fastq.gz | head
```

Descomprimir archivos `.tar.gz`:

```bash
tar -xzvf archivo.tar.gz
```

Comprimir una carpeta:

```bash
tar -czvf resultados.tar.gz results/
```

---

## 7.15 Ver espacio en disco

Ver espacio general:

```bash
df -h
```

Ver cuánto ocupa una carpeta:

```bash
du -sh carpeta
```

Ver el tamaño de todas las carpetas del directorio actual:

```bash
du -sh *
```

---

## 7.16 Ver procesos activos

```bash
top
```

También puede usarse:

```bash
htop
```

si está disponible en el sistema.

---

# 8. Comandos útiles para archivos FASTQ y FASTA

## 8.1 Ver las primeras líneas de un FASTQ comprimido

```bash
zcat muestra_R1.fastq.gz | head
```

Un archivo FASTQ tiene bloques de 4 líneas por lectura:

```text
@identificador_de_la_lectura
ACGTACGTACGT
+
FFFFFFFFFFFF
```

---

## 8.2 Contar lecturas en un FASTQ

```bash
zcat muestra_R1.fastq.gz | wc -l
```

El resultado se divide entre 4.

También se puede hacer directamente:

```bash
echo $(( $(zcat muestra_R1.fastq.gz | wc -l) / 4 ))
```

---

## 8.3 Contar secuencias en un FASTA

```bash
grep -c "^>" archivo.fasta
```

---

## 8.4 Ver nombres de secuencias en un FASTA

```bash
grep "^>" archivo.fasta | head
```

---

# 9. Transferencia de archivos con `scp`

El comando `scp` permite copiar archivos entre el computador local y el clúster.

## 9.1 Copiar desde el computador local hacia el clúster

Desde la terminal del computador local:

```bash
scp archivo.txt usuario@cluster.uniandes.edu.co:/hpcfs/home/usuario/
```

Copiar una carpeta completa:

```bash
scp -r carpeta_local usuario@cluster.uniandes.edu.co:/hpcfs/home/usuario/
```

---

## 9.2 Copiar desde el clúster hacia el computador local

Desde la terminal del computador local:

```bash
scp usuario@cluster.uniandes.edu.co:/hpcfs/home/usuario/resultados.tar.gz .
```

El punto `.` significa la carpeta actual del computador local.

---

# 10. Organización recomendada de un proyecto metagenómico

Una estructura ordenada facilita el análisis y evita errores.

Ejemplo:

```text
proyecto_metagenomica/
├── raw_data/
│   ├── muestra1_R1.fastq.gz
│   ├── muestra1_R2.fastq.gz
│   ├── muestra2_R1.fastq.gz
│   └── muestra2_R2.fastq.gz
├── samplesheets/
│   └── samplesheet.csv
├── scripts/
│   ├── fastqc.sh
│   ├── kraken2.sh
│   └── nextflow_taxprofiler.sh
├── results/
│   ├── fastqc/
│   ├── kraken2/
│   └── multiqc/
├── logs/
└── README.md
```

Crear esta estructura:

```bash
mkdir -p proyecto_metagenomica/{raw_data,samplesheets,scripts,results,logs}
```

---

# 11. Introducción a Slurm

Slurm es el sistema que permite enviar trabajos al clúster.

Los comandos más importantes son:

| Comando             | Función                      |
| ------------------- | ---------------------------- |
| `sbatch`            | Enviar un job al clúster     |
| `squeue`            | Ver jobs en cola o ejecución |
| `scancel`           | Cancelar un job              |
| `sinfo`             | Ver particiones y nodos      |
| `scontrol show job` | Ver detalles de un job       |
| `sacct`             | Consultar jobs finalizados   |

---

# 12. ¿Cómo se escribe un job?

Un job de Slurm es un archivo de texto, normalmente con extensión `.sh`, que contiene:

1. Encabezado con recursos solicitados.
2. Carga de módulos o ambientes.
3. Comandos que se van a ejecutar.

Ejemplo básico:

```bash
nano mi_primer_job.sh
```

Contenido del archivo:

```bash
#!/bin/bash

#SBATCH --job-name=primer_job
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --output=logs/primer_job_%j.out
#SBATCH --error=logs/primer_job_%j.err

# Mostrar información básica
echo "El job inició en:"
date

hostname
pwd

# Comando de ejemplo
ls -lh

# Finalización
echo "El job terminó en:"
date
```

Guardar y salir de `nano`:

* `Ctrl + O` para guardar.
* `Enter` para confirmar.
* `Ctrl + X` para salir.

Enviar el job:

```bash
sbatch mi_primer_job.sh
```

Si el job fue enviado correctamente, Slurm mostrará algo similar a:

```text
Submitted batch job 123456
```

---

# 13. Significado de las directivas `#SBATCH`

| Directiva         | Significado                                |
| ----------------- | ------------------------------------------ |
| `--job-name`      | Nombre del job                             |
| `--partition`     | Partición donde se ejecutará               |
| `--nodes`         | Número de nodos solicitados                |
| `--ntasks`        | Número de tareas                           |
| `--cpus-per-task` | Número de CPU por tarea                    |
| `--mem`           | Memoria RAM solicitada                     |
| `--time`          | Tiempo máximo de ejecución                 |
| `--output`        | Archivo donde se guarda la salida estándar |
| `--error`         | Archivo donde se guardan los errores       |

El símbolo `%j` se reemplaza automáticamente por el ID del job.

Ejemplo:

```bash
#SBATCH --output=logs/job_%j.out
```

Si el ID del job es `123456`, el archivo será:

```text
logs/job_123456.out
```

---

# 14. Consultar el estado de un job

Ver todos los jobs del usuario:

```bash
squeue -u $USER
```

Ver todos los jobs en el clúster:

```bash
squeue
```

Ver información detallada de un job:

```bash
scontrol show job 123456
```

Cancelar un job:

```bash
scancel 123456
```

Consultar jobs finalizados:

```bash
sacct -j 123456
```

Consultar uso de recursos:

```bash
sacct -j 123456 --format=JobID,JobName,Partition,State,Elapsed,MaxRSS,AllocCPUS
```

---

# 15. Estados comunes de un job en Slurm

| Estado | Significado                                        |
| ------ | -------------------------------------------------- |
| `PD`   | Pending: el job está en cola esperando recursos    |
| `R`    | Running: el job está corriendo                     |
| `CG`   | Completing: el job está finalizando                |
| `CD`   | Completed: el job terminó correctamente            |
| `F`    | Failed: el job falló                               |
| `TO`   | Timeout: el job superó el tiempo solicitado        |
| `OOM`  | Out of memory: el job superó la memoria solicitada |
| `CA`   | Cancelled: el job fue cancelado                    |

---

# 16. Ejemplo de job para FastQC

Este job ejecuta `FastQC` sobre archivos FASTQ comprimidos.

```bash
#!/bin/bash

#SBATCH --job-name=fastqc_metagenomica
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=logs/fastqc_%j.out
#SBATCH --error=logs/fastqc_%j.err

# Cargar módulo, si está disponible en el clúster
module load fastqc

# Crear carpeta de resultados
mkdir -p results/fastqc

# Ejecutar FastQC
fastqc raw_data/*.fastq.gz \
  --threads 4 \
  --outdir results/fastqc
```

Enviar:

```bash
sbatch scripts/fastqc.sh
```

---

# 17. Ejemplo de job para Kraken2

```bash
#!/bin/bash

#SBATCH --job-name=kraken2_metagenomica
#SBATCH --partition=medium
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=80G
#SBATCH --time=1-00:00:00
#SBATCH --output=logs/kraken2_%j.out
#SBATCH --error=logs/kraken2_%j.err

module load kraken2

mkdir -p results/kraken2

kraken2 \
  --db /ruta/a/base_de_datos_kraken2 \
  --threads 16 \
  --paired \
  raw_data/muestra_R1.fastq.gz raw_data/muestra_R2.fastq.gz \
  --report results/kraken2/muestra.report \
  --output results/kraken2/muestra.output
```

---

# 18. Ejemplo de job para Nextflow

Muchos pipelines modernos, como los de `nf-core`, se ejecutan con Nextflow.

Ejemplo general:

```bash
#!/bin/bash

#SBATCH --job-name=nfcore_taxprofiler
#SBATCH --partition=medium
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=80G
#SBATCH --time=4-00:00:00
#SBATCH --output=logs/taxprofiler_%j.out
#SBATCH --error=logs/taxprofiler_%j.err

module load jdk
module load singularity
module load nextflow

nextflow run nf-core/taxprofiler \
  -profile singularity \
  --input samplesheets/samplesheet.csv \
  --databases databases.csv \
  --outdir results/taxprofiler \
  -resume
```

> Nota: en Nextflow, el job principal envía tareas adicionales al clúster según la configuración del pipeline. Por eso es importante revisar el archivo de configuración y los recursos asignados a cada proceso.

---

# 19. Buenas prácticas en el clúster

## 19.1 No ejecutar análisis pesados en el nodo de login

El nodo de login es compartido por todos los usuarios. Se debe usar para:

* Conectarse al clúster.
* Organizar archivos.
* Editar scripts.
* Enviar jobs.
* Revisar logs ligeros.

No se debe usar para:

* Ejecutar ensamblajes.
* Correr Kraken2 con bases grandes.
* Ejecutar pipelines completos.
* Procesar muchos archivos FASTQ.

---

## 19.2 Pedir recursos razonables

Solicitar demasiados recursos puede hacer que el job espere más tiempo en cola. Solicitar pocos recursos puede hacer que falle.

Ejemplo incorrecto para FastQC:

```bash
#SBATCH --cpus-per-task=64
#SBATCH --mem=500G
```

Ejemplo razonable:

```bash
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
```

---

## 19.3 Revisar siempre los logs

Después de ejecutar un job, revisar:

```bash
ls -lh logs/
```

Ver salida:

```bash
less logs/job_123456.out
```

Ver errores:

```bash
less logs/job_123456.err
```

Buscar errores:

```bash
grep -i "error" logs/*.err
```

---

## 19.4 Usar nombres claros

Evitar nombres como:

```text
prueba.sh
nuevo.sh
final.sh
final_final.sh
```

Preferir nombres informativos:

```text
01_fastqc.sh
02_fastp_trim.sh
03_kraken2.sh
04_bracken.sh
05_multiqc.sh
```

---

## 19.5 Mantener una estructura reproducible

Todo análisis debería tener:

* Datos de entrada claros.
* Scripts guardados.
* Logs conservados.
* Resultados organizados.
* Archivo README con descripción del análisis.

---

# 20. Editores de texto en terminal

## 20.1 Usar `nano`

Crear o editar un archivo:

```bash
nano script.sh
```

Comandos básicos:

| Acción       | Comando    |
| ------------ | ---------- |
| Guardar      | `Ctrl + O` |
| Confirmar    | `Enter`    |
| Salir        | `Ctrl + X` |
| Cortar línea | `Ctrl + K` |
| Pegar línea  | `Ctrl + U` |
| Buscar texto | `Ctrl + W` |

---

# 21. Permisos de ejecución

Para ejecutar un script directamente, primero se deben dar permisos de ejecución:

```bash
chmod +x script.sh
```

Luego se puede ejecutar:

```bash
./script.sh
```

Sin embargo, en el clúster los jobs normalmente se envían con:

```bash
sbatch script.sh
```

---

# 22. Variables útiles en Bash

Una variable guarda información que puede reutilizarse.

Ejemplo:

```bash
SAMPLE="muestra1"
```

Usar la variable:

```bash
echo $SAMPLE
```

Ejemplo aplicado:

```bash
SAMPLE="muestra1"
R1="raw_data/${SAMPLE}_R1.fastq.gz"
R2="raw_data/${SAMPLE}_R2.fastq.gz"

ls -lh $R1 $R2
```

---

# 23. Bucles básicos en Bash

Un bucle permite repetir una acción sobre varios archivos.

Ejemplo:

```bash
for file in raw_data/*.fastq.gz
 do
   echo "Procesando $file"
 done
```

Ejemplo para listar tamaños:

```bash
for file in raw_data/*.fastq.gz
 do
   ls -lh $file
 done
```

---

# 24. Ejercicio práctico 1: crear estructura del proyecto

1. Conectarse al clúster.
2. Crear una carpeta llamada `curso_metagenomica`.
3. Crear las subcarpetas `raw_data`, `scripts`, `results`, `logs` y `samplesheets`.
4. Verificar la estructura con `ls`.

Comandos sugeridos:

```bash
mkdir -p curso_metagenomica/{raw_data,scripts,results,logs,samplesheets}
cd curso_metagenomica
ls -lh
```

---

# 25. Ejercicio práctico 2: crear y enviar un primer job

Crear el archivo:

```bash
nano scripts/test_cluster.sh
```

Contenido:

```bash
#!/bin/bash

#SBATCH --job-name=test_cluster
#SBATCH --partition=short
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:05:00
#SBATCH --output=logs/test_cluster_%j.out
#SBATCH --error=logs/test_cluster_%j.err

echo "Hola, este es mi primer job en el clúster"
echo "Fecha de inicio:"
date
echo "Nodo donde corre el job:"
hostname
echo "Carpeta actual:"
pwd
echo "Archivos disponibles:"
ls -lh
echo "Fecha de finalización:"
date
```

Enviar:

```bash
sbatch scripts/test_cluster.sh
```

Revisar estado:

```bash
squeue -u $USER
```

Revisar resultados:

```bash
ls -lh logs/
less logs/test_cluster_*.out
less logs/test_cluster_*.err
```

---

# 26. Errores frecuentes

## 26.1 El job queda mucho tiempo en cola

Posibles causas:

* Se solicitaron demasiadas CPU.
* Se solicitó demasiada memoria.
* La partición está ocupada.
* El tiempo solicitado es muy largo.

Revisar con:

```bash
squeue -u $USER
scontrol show job JOBID
```

---

## 26.2 El job falla por memoria

Mensaje típico:

```text
Out of memory
Killed
OOM
```

Solución:

* Aumentar `--mem`.
* Usar una partición con más memoria.
* Reducir el tamaño de entrada.
* Revisar si el programa permite dividir el análisis por muestras.

---

## 26.3 El job falla por tiempo

Mensaje típico:

```text
TIMEOUT
```

Solución:

* Aumentar `--time`.
* Usar una partición de mayor duración.
* Optimizar el comando.

---

## 26.4 El comando no existe

Mensaje típico:

```text
command not found
```

Posibles soluciones:

```bash
module avail
module load nombre_programa
which nombre_programa
```

---

# 27. Resumen de comandos esenciales

| Comando   | Uso                                    |
| --------- | -------------------------------------- |
| `pwd`     | Mostrar carpeta actual                 |
| `ls`      | Listar archivos                        |
| `cd`      | Cambiar de carpeta                     |
| `mkdir`   | Crear carpetas                         |
| `cp`      | Copiar archivos                        |
| `mv`      | Mover o renombrar archivos             |
| `rm`      | Eliminar archivos                      |
| `cat`     | Ver archivos pequeños                  |
| `less`    | Ver archivos grandes página por página |
| `more`    | Ver archivos página por página         |
| `head`    | Ver primeras líneas                    |
| `tail`    | Ver últimas líneas                     |
| `grep`    | Buscar texto                           |
| `wc`      | Contar líneas, palabras o caracteres   |
| `du -sh`  | Ver tamaño de carpetas                 |
| `df -h`   | Ver espacio en disco                   |
| `scp`     | Transferir archivos                    |
| `ssh`     | Conectarse a servidor remoto           |
| `nano`    | Editar archivos en terminal            |
| `chmod`   | Cambiar permisos                       |
| `sbatch`  | Enviar job                             |
| `squeue`  | Ver cola de jobs                       |
| `scancel` | Cancelar job                           |
| `sinfo`   | Ver particiones                        |
| `sacct`   | Revisar jobs finalizados               |

---

# 28. Recomendaciones finales

Antes de ejecutar cualquier análisis metagenómico en el clúster:

1. Revisar que los archivos de entrada existan.
2. Confirmar que las rutas sean correctas.
3. Crear carpetas para resultados y logs.
4. Solicitar recursos adecuados.
5. Probar primero con una muestra pequeña.
6. Revisar los archivos `.out` y `.err`.
7. Documentar los comandos usados.
8. No borrar archivos de trabajo sin estar seguro.

La bioinformática reproducible depende tanto del análisis como de la organización. Un buen manejo de Linux y del clúster es fundamental para trabajar de forma eficiente, segura y ordenada en proyectos de metagenómica.

---

# 29. Actividad sugerida para entregar

Cada estudiante debe crear una carpeta en el clúster con la siguiente estructura:

```text
apellido_nombre_metagenomica/
├── raw_data/
├── scripts/
├── results/
├── logs/
└── README.md
```

Dentro de `scripts/`, debe incluir un job llamado:

```text
test_cluster.sh
```

El job debe imprimir:

* Nombre del estudiante.
* Fecha y hora.
* Nodo donde se ejecutó.
* Ruta actual.
* Lista de archivos del proyecto.

El estudiante debe entregar:

1. Captura o contenido del archivo `.out`.
2. Captura o contenido del archivo `.err`.
3. El script `test_cluster.sh`.
4. Una breve explicación de qué significa cada directiva `#SBATCH` utilizada.
