"""Takes a path to a genome and indexes it."""

import argparse
import os

from amaize import jobs, sbatch


def parserCmdLine():
    """Parse the command line options."""
    parser = argparse.ArgumentParser(
        description=('Performs the various indexing operations needed for a '
                     'genome in the customization pipeline'))
    parser.add_argument(
        'genome_path',
        help='The path to the genome')
    parser.add_argument(
        'vcf',
        help='The path to the vcf file')
    parser.add_argument(
        'logs',
        help='Logs output directory',
        nargs='?',
        default=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "logs"))
    parser.add_argument(
        '-b', '--bwa_index',
        help='Perform BWA indexing',
        action='store_true')
    parser.add_argument(
        '-p', '--picard',
        help='Perform Picard CreateSequenceDictionary indexing',
        action='store_true')
    parser.add_argument(
        '-f', '--faidx',
        help='Perform Samtools faidx indexing',
        action='store_true')
    parser.add_argument(
        '-s', '--sort_vcf',
        help='Sort the vcf',
        action='store_true')
    return parser.parse_args()


def index(args):
    """Indexes the given genome with the specified indexers."""
    genome = os.path.basename(args.genome_path).split(".")[0]
    logs = jobs.outDir(args.logs, genome)
    vcf = args.vcf.split(".")

    bwa = jobs.tempScript(sbatch.bwaIndexScript())
    jobs.job(0, args.bwa_index, logs, f"{genome}_bwa_index", bwa.name, genome,
             0, args.prefix, args.genome_path)
    os.unlink(bwa.name)

    pic = jobs.tempScript(sbatch.picardIndexScript())
    jobs.job(0, args.picard, logs, f"{genome}_picard_index", pic.name, genome,
             0, args.prefix, args.genome_path)
    os.unlink(pic.name)

    fai = jobs.tempScript(sbatch.faidxScript())
    jobs.job(0, args.faidx, logs, f"{genome}_faidx", fai.name, genome, 0,
             args.prefix, args.genome_path)
    os.unlink(fai.name)

    vcf = jobs.tempScript(sbatch.sortVcfScript())
    jobs.job(0, args.sort_vcf, logs, f"{genome}_sort_vcf", vcf.name, genome, 0,
             args.prefix, args.vcf,
             (vcf[0] + '_sorted.' + vcf[1]), args.genome_path,
             (vcf[0] + '_sorted_updated.' + vcf[1]))
    os.unlink(bwa.name)

    os.system("squeue -u maxh")


def main():
    """Parse the command line arguments and pass on to indexing function."""
    index(parserCmdLine())


if __name__ == "__main__":
    main()
