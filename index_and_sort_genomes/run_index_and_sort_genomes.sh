#!/usr/bin/bash

## index the B73 AGPv4.40 reference genome and sort its vcf
python \
    scripts/index_and_sort_genomes.py \
    /scratch/maxh/data/v4_B73_genome/Zea_mays.AGPv4.dna.toplevel.fa \
    /scratch/maxh/data/v4_B73_genome/zea_mays.vcf \
    B73

## make a copy of the dict with a modified name
# cp v4_B73_genome/Zea_mays.AGPv4.dna.toplevel.fa.dict v4_B73_genome/Zea_mays.AGPv4.dna.toplevel.dict
