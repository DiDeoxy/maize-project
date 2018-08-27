#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=4000M
#SBATCH --time=0-03:00

# $1 is path to output directory + file prefix
# $2 is genome path
# $3 is sorted vcf

java -jar $GATK -T BaseRecalibrator \
    -nct 16 \
    -I $1_marked.bam \
    -R $2 \
    -knownSites $3 \
    -o $1_recal.table
report