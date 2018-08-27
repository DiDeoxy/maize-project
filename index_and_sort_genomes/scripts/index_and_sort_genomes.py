"""Takes a path to a genome and indexes it."""

import argparse
import subprocess
import os
import pathlib
import jobs


def index(args):
    """Indexes the given genome with the specified indexers."""
    logs, scriptDir = jobs.baseDirs(args.logs, args.prefix,
                                    os.path.realpath(__file__))

    vcf = args.vcf.split(".")

    prevJob = jobs.genericJob(0, args.bwa_index, "bwa_index", logs, scriptDir,
                              args.prefix, args.genome)
    prevJob = jobs.genericJob(prevJob, args.picard, "picard_index", logs,
                              scriptDir, args.prefix, args.genome)
    prevJob = jobs.genericJob(prevJob, args.faidx, "faidx", logs, scriptDir,
                              args.prefix, args.genome)
    prevJob = jobs.genericJob(prevJob, args.sort_vcf, "sort_vcf", logs,
                              scriptDir, args.prefix, args.vcf,
                              (vcf[0] + '_sorted.' + vcf[1]), args.genome,
                              (vcf[0] + '_sorted_updated.' + vcf[1]))

    os.system("squeue -u maxh")


def main():
    """Parse the command line arguments and pass on to indexing function."""
    parser = argparse.ArgumentParser(
        description=('Performs the various indexing operations needed for a '
                     'genome in the customization pipeline'))
    parser.add_argument(
        'genome',
        help='The path to the genome')
    parser.add_argument(
        'vcf',
        help='The path to the vcf file')
    parser.add_argument(
        'prefix',
        help='Prefix to give to logs')
    parser.add_argument(
        'logs',
        help='Logs output directory',
        nargs='?',
        default=os.path.join(os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))), "logs"))
    parser.add_argument(
        '-b', '--bwa_index',
        help='Don\'t perform BWA indexing',
        action='store_false')
    parser.add_argument(
        '-p', '--picard',
        help='Don\'t perform Picard CreateSequenceDictionary indexing',
        action='store_false')
    parser.add_argument(
        '-f', '--faidx',
        help='Don\'t perform Samtools faidx indexing',
        action='store_false')
    parser.add_argument(
        '-s', '--sort_vcf',
        help='Don\'t sort the vcf',
        action='store_false')
    index(parser.parse_args())


if __name__ == "__main__":
    main()
