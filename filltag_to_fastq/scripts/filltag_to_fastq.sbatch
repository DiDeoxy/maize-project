#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=32000M
#SBATCH --time=0-01:00

# $1 is filltag file
# $2 is outpath
# $3 is outfile prefix

python filltag_to_fastq.py $1 $2 $3