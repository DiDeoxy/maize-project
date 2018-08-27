#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=18000M
#SBATCH --time=0-04:00

# $1 is path to output directory + file prefix

module load picard/2.18.9
java -jar $EBROOTPICARD/picard.jar SortSam \
	INPUT=$1_bwa.sam \
	OUTPUT=$1_sorted.bam \
	SORT_ORDER=coordinate \
	CREATE_INDEX=true
rm $1.sam
report