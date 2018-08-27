#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=12000M
#SBATCH --time=0-00:20

# $1 is path to output directory + file prefix
# $2 is genome path

java -jar $GATK -T VariantFiltration \
    -R $2 \
    -V $1_snps.vcf \
    --mask $1_indels.vcf \
    --maskExtension 3 \
    --maskName "snps_near_indels" \
    --filterExpression 'QD < 2.0 || FS > 60.0 || MQ < 40.0 || ReadPosRankSum < -8.0 || SOR > 4.0' \
    --filterName "basic_snp_filter" \
    -o variants/$1_snps_filtered.vcf
report