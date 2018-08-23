#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=12000M
#SBATCH --time=0-04:00

# $1 is path to output directory + file prefix

java -jar $EBROOTPICARD/picard.jar MarkDuplicates \
    I=$1_sorted.bam \
    O=$1_marked.bam \
    M=$1_marked_dups_metrics.txt \
    CREATE_INDEX=true
rm $1_sorted.bam $1_sorted.bai