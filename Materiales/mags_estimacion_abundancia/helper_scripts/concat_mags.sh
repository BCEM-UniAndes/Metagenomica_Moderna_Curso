#!/bin/bash

dereplicated_genomes="/hpcfs/home/cursos/metagenomica_moderna/Talleres/Prueba/mags_drep/drep_out/dereplicated_genomes"

cat ${dereplicated_genomes}/*.fa > representative_genomes.fasta
