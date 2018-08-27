#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=12
#SBATCH --mem-per-cpu=1000M
#SBATCH --time=0-00:05

# $1 is output directory of untreated fastqc reports
# $2 is untreated fasta file or files

module load fastqc/0.11.5
fastqc -t 12 --noextract -o "$@"
report