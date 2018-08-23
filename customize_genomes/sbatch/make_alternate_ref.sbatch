#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=12000M
#SBATCH --time=0-01:00

# $1 is reference genome
# $2 is snps
# $3 is the new reference extension

java -jar $GATK -T FastaAlternateReferenceMaker \
   -R $1 \
   -V $2 \
   -o $3.fasta