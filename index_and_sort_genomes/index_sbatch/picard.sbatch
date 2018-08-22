#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4000M
#SBATCH --time=0-00:05

java -jar $EBROOTPICARD/picard.jar CreateSequenceDictionary \
    REFERENCE=$1 OUTPUT=$2/$3.dict