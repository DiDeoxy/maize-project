#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=12
#SBATCH --mem-per-cpu=10000M
#SBATCH --time=0-04:00

# $1 is output directory of untreated fastqc reports
# $2 is untreated fasta file or files

fastqc -t 12 --noextract -o $1 $2