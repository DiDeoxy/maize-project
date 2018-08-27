#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=3000M
#SBATCH --time=1-16:00

# $1 is path to output directory + file prefix
# $2 is genome path

java -jar $GATK -T HaplotypeCaller \
    -nct 16 \
    -I $1_marked.bam \
    -BQSR $1_recal.table \
    -R $2 \
    -mmq 10 \
    -o $1.vcf
report