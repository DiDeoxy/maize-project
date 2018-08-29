"""sbatch scripts as functions for outputting to temp files."""


def fastqcScript():
    """Return the fastqc script text."""
    return """\
#!/usr/bin/bash

# SBATCH --nodes=1
# SBATCH --ntasks=1
# SBATCH --cpus-per-task=1
# SBATCH --mem-per-cpu=1000M
# SBATCH --time=0-00:20

# $1 is output directory of untreated fastqc reports
# $2 is untreated fasta file or files

module load fastqc/0.11.5
fastqc --noextract -o "$@"
report"""


def trimPEScript():
    """Return the fastqc script text."""
    return """\
#!/usr/bin/bash

# SBATCH --nodes=1
# SBATCH --ntasks=1
# SBATCH --cpus-per-task=16
# SBATCH --mem-per-cpu=1000M
# SBATCH --time=0-03:00

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
report"""


def trimSEScript():
    """Return the fastqc script text."""
    return """\
#!/usr/bin/bash

# SBATCH --nodes=1
# SBATCH --ntasks=1
# SBATCH --cpus-per-task=16
# SBATCH --mem-per-cpu=1000M
# SBATCH --time=0-03:00

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
report"""
