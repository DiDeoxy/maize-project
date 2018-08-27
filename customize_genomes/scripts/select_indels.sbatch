#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=3000M
#SBATCH --time=0-02:00

# $1 is path to output directory + file prefix

module load gatk/4.0.0.0
java -jar $GATK -T SelectVariants \
    -nt 16 \
    -R $2 \
    -V $1.vcf \
    -selectType INDEL \
    -o $1_indels.vcf 
report