"""Takes a path to a genome and indexes it."""

import argparse
import subprocess
import os


def index(args):
    """Indexes the given genome with the specified indexers."""
    basename = os.path.dirname(args.path)

    if args.bwa:
        cmd = (
            "sbatch --nodes=1 --ntasks=1 --cpus-per-task=1 "
            "--mem-per-cpu=4000M --time=0-02:00 "
            f"--output=logs/{args.prefix}_bwa_index.log "
            f"bwa index {args.path}")
        print(f"Creating job with command:\n\t{cmd}")
        status, jobnum = subprocess.getstatusoutput(cmd)
        if (status == 0):
            print(jobnum)
        else:
            print("Error submitting BWA job!")
    if args.picard:
        cmd = (
            "sbatch --nodes=1 --ntasks=1 --cpus-per-task=1 "
            "--mem-per-cpu=4000M --time=0-00:05 "
            f"--output=logs/{args.prefix}_picard_index.log "
            "java -jar $EBROOTPICARD/picard.jar CreateSequenceDictionary"
            f"REFERENCE={args.path} OUTPUT={basename}/{args.prefix}.dict")
        print(f"Creating job with command:\n\t{cmd}")
        status, jobnum = subprocess.getstatusoutput(cmd)
        if (status == 0):
            print(jobnum)
        else:
            print("Error submitting Picard job!")
    if args.faidx:
        cmd = (
            "sbatch --nodes=1 --ntasks=1 --cpus-per-task=1 "
            "--mem-per-cpu=4000M --time=0-00:05 "
            f"--output=logs/{args.prefix}_faidx_index.log "
            f"samtools faidx {args.path}")
        print(f"Creating job with command:\n\t{cmd}")
        status, jobnum = subprocess.getstatusoutput(cmd)
        if (status == 0):
            print(jobnum)
        else:
            print("Error submitting faidx job!")

    os.system("squeue -u maxh")


def main():
    """Parse the command line arguments and pass on to functions."""
    parser = argparse.ArgumentParser(
        description=('Performs the various indexing operations needed for a '
                     'genome in the customization pipeline'))
    parser.add_argument('path', help='The path to the genome')
    parser.add_argument(
        'prefix', help='Prefix to give to output files (index, logs)')
    parser.add_argument('--bwa', help='Perform BWA indexing',
                        action='store_true')
    parser.add_argument(
        '--picard',
        help='Perform Picard CreateSequenceDictionary indexing',
        action='store_true')
    parser.add_argument('--faidx', help='Perform Samtools faidx indexing',
                        action='store_true')
    index(parser.parse_args())


if __name__ == "__main__":
    main()
