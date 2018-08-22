#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=12000M
#SBATCH --time=0-01:00
#SBATCH --output=logs/B73_sort_vcf.log

java -jar $EBROOTPICARD/picard.jar SortVcf \
    I=v4_B73_genome/zea_mays.vcf \
    O=v4_B73_genome/zea_mays_sorted.vcf \
    SEQUENCE_DICTIONARY=v4_B73_genome/Zea_mays.AGPv4.dna.toplevel.fa.dict
java -jar $EBROOTPICARD/picard.jar UpdateVcfSequenceDictionary \
    I=v4_B73_genome/zea_mays_sorted.vcf \
    O=v4_B73_genome/zea_mays_sorted2.vcf \
    SEQUENCE_DICTIONARY=v4_B73_genome/Zea_mays.AGPv4.dna.toplevel.fa.dict
rm v4_B73_genome/zea_mays_sorted.vcf