"""Takes a path to a genome and indexes it."""

import argparse
import subprocess
import os


def index(args):
    """Indexes the given genome with the specified indexers."""
    dr = os.path.dirname(args.genome)
    bn = os.path.basename(args.genome)

    if args.bwa:
        cmd = (
            f"sbatch --output=logs/{args.prefix}_bwa_index.log "
            f"index_sbatch/bwa.sbatch {args.genome}")
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))
    if args.picard:
        cmd = (
            f"sbatch --output=logs/{args.prefix}_picard_index.log "
            f"index_sbatch/picard.sbatch {args.genome} {dr} {bn}")
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))
    if args.faidx:
        cmd = (
            f"sbatch --output=logs/{args.prefix}_faidx_index.log "
            f"index_sbatch/faidx.sbatch {args.genome}")
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))

    os.system("squeue -u maxh")


def main():
    """Parse the command line arguments and pass on to indexing function."""
    parser = argparse.ArgumentParser(
        description=('Performs the various indexing operations needed for a '
                     'genome in the customization pipeline'))
    parser.add_argument('genome', help='The path to the genome')
    parser.add_argument(
        'prefix', help='Prefix to give to logs')
    parser.add_argument('-b', '--bwa', help='Perform BWA indexing',
                        action='store_true')
    parser.add_argument(
        '-p', '--picard',
        help='Perform Picard CreateSequenceDictionary indexing',
        action='store_true')
    parser.add_argument('-f', '--faidx', help='Perform Samtools faidx indexing',
                        action='store_true')
    index(parser.parse_args())


if __name__ == "__main__":
    main()
