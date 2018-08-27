#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=1000M
#SBATCH --time=0-03:00

# $1 is input reads
# $2 is output reads

module load trimmomatic/0.36
java -jar $EBROOTTRIMMOMATIC/trimmomatic-0.36.jar \
    -threads 16
    SE \
    $1 \
    $2 \
    # ILLUMINACLIP:<find out>(fastqc?) \
    LEADING:3 \
    TRAILING:3 \
    SLIDINGWINDOW:4:15 \
    MINLEN:36
report