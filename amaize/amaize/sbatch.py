"""sbatch scripts."""


def fastqcScript():
    """Return the fastqc script text."""
    return """\
#!/usr/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=3
#SBATCH --mem-per-cpu=500M
#SBATCH --time=0-00:30

# $1 is output directory of untreated fastqc reports
# $2 is untreated fasta file or files

module load fastqc/0.11.5
fastqc -t 3 --noextract -o "$@"
sacct -j $SLURM_JOB_ID.batch --format=JobName,JobID,TimeLimit,Elapsed,Start,End,CPUTime,MaxVMSize,MaxRSS,AveRSS
"""


def trimPEScript():
    """Return the fastqc script text."""
    return """\
#!/usr/bin/bash

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem-per-cpu=1000M
#SBATCH --time=0-03:00

# $1 is forward
# $2 is reverse
# $3 is output paired forward
# $4 is output unpaired forward
# $5 is output paired reverse
# $6 is output unpaired reverse

module load trimmomatic/0.36
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
sacct -j $SLURM_JOB_ID.batch --format=JobName,JobID,TimeLimit,Elapsed,Start,End,CPUTime,MaxVMSize,MaxRSS,AveRSS
"""


def trimSEScript():
    """Return the fastqc script text."""
    return """\
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
sacct -j $SLURM_JOB_ID.batch --format=JobName,JobID,TimeLimit,Elapsed,Start,End,CPUTime,MaxVMSize,MaxRSS,AveRSS
"""


def faidxScript():
    """Return the faidx script text."""
    return """\
#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4000M
#SBATCH --time=0-00:05

module load samtools/1.9
samtools faidx $1
sacct -j $SLURM_JOB_ID.batch --format=JobName,JobID,TimeLimit,Elapsed,Start,End,CPUTime,MaxVMSize,MaxRSS,AveRSS
"""


def sortVcfScript():
    """Return the sort vcf scritp."""
    return """\
#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=12000M
#SBATCH --time=0-00:30

# $1 is vcf file
# $2 is output/input sorted vcf file
# $3 is reference genome
# $4 is output sorted vcf file with updated dict

module load picard/2.18.9
java -jar $EBROOTPICARD/picard.jar SortVcf \
    I=$1 \
    O=$2 \
    SEQUENCE_DICTIONARY=$3
java -jar $EBROOTPICARD/picard.jar UpdateVcfSequenceDictionary \
    I=$2 \
    O=$4 \
    SEQUENCE_DICTIONARY=$3
rm $2
sacct -j $SLURM_JOB_ID.batch --format=JobName,JobID,TimeLimit,Elapsed,Start,End,CPUTime,MaxVMSize,MaxRSS,AveRSS
"""


def picardIndexScript():
    """Return the picard index script."""
    return """\
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
sacct -j $SLURM_JOB_ID.batch --format=JobName,JobID,TimeLimit,Elapsed,Start,End,CPUTime,MaxVMSize,MaxRSS,AveRSS
"""


def bwaIndexScript():
    """Return the bwa index script."""
    return """\
#!/usr/bin/bash

#SBATCH --nodes=1 
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=4000M
#SBATCH --time=0-01:00

module load bwa/0.7.17
bwa index $1
sacct -j $SLURM_JOB_ID.batch --format=JobName,JobID,TimeLimit,Elapsed,Start,End,CPUTime,MaxVMSize,MaxRSS,AveRSS
"""
