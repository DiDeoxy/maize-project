#!/usr/bin/bash

## sort the vcf file into proper order
# sbatch sort_vcf.sbatch

## index the B73 AGPv4.40 reference genome, make a copy of the dict with a modified name
# python index_genomes.py v4_B73_genome/Zea_mays.AGPv4.dna.toplevel.fa B73 -f
# cp v4_B73_genome/Zea_mays.AGPv4.dna.toplevel.fa.dict v4_B73_genome/Zea_mays.AGPv4.dna.toplevel.dict
