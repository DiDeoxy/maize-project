#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=500M
#SBATCH --time=0-00:10

# $1 is path to output directory + file prefix

samtools flagstat $1_sorted.bam 