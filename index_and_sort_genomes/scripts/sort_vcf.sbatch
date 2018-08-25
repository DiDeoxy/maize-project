#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=12000M
#SBATCH --time=0-00:30

# $1 is vcf file
# $2 is output/input sorted vcf file
# $3 is reference genome
# $4 is output sorted vcf file with updated dict

java -jar $EBROOTPICARD/picard.jar SortVcf \
    I=$1 \
    O=$2 \
    SEQUENCE_DICTIONARY=$3
java -jar $EBROOTPICARD/picard.jar UpdateVcfSequenceDictionary \
    I=$2 \
    O=$4 \
    SEQUENCE_DICTIONARY=$3
rm $2