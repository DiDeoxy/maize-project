#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=4000M
#SBATCH --time=0-11:00

# $1 is path to genome
# $2 and $3 are paths to paired end reads

module load bwa/0.7.17
bwa mem -t 16 \
    -R '@RG\tID:M1\tSM:EF09B\tLB:lib1\tPL:illumina\tPU:unit1' \
    -M $1 \
    $2 $3
report