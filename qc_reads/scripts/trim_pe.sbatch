#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=1000M
#SBATCH --time=0-03:00

# $1 is read 1
# $2 is read 2
# $3 is output paired read 1
# $4 is output unpaired read 1
# $5 is output paired read 2
# $6 is output unpaired read 2

java -jar $EBROOTTRIMMOMATIC/trimmomatic-0.36.jar \
    -threads 16
    PE \
    $1 $2 \
    $3 $4 \
    $5 $6 \
    # ILLUMINACLIP:<find out>(fastqc?) \
    LEADING:3 \
    TRAILING:3 \
    SLIDINGWINDOW:4:15 \
    MINLEN:36
report