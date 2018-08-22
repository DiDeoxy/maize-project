#!/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 #maximum number of tasks in the batch script
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=100M #min memeory per cpu
#SBATCH --time=0-00:05

echo "Hello World! My name is $1."
