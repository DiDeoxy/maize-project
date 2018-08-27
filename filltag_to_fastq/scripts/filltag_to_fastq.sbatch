#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=2000M
#SBATCH --time=0-02:00

# $1 is filltag file
# $2 is outpath
# $3 is outfile prefix

python scripts/filltag_to_fastq.py $1 $2 $3
report