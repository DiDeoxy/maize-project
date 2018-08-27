#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4000M
#SBATCH --time=0-00:05

# $1 is the reference genome

module load picard/2.18.9
java -jar $EBROOTPICARD/picard.jar CreateSequenceDictionary \
    REFERENCE=$1 OUTPUT=$1.dict
report