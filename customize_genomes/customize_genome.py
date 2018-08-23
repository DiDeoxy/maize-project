"""Takes a path to a genome and indexes it."""

import argparse
import subprocess
from os import path, system
import pathlib


def parse():
    """Parse the command line options."""
    parser = argparse.ArgumentParser(
        description=('Performs the various steps needed to for a single pass '
                     'genome customization'))
    parser.add_argument(
        'genome', help='The path to the genome file')
    parser.add_argument(
        'vcf', help='The path to the genome\'s vcf file')
    parser.add_argument(
        'prefix', help='Base name to give intermdiate files')
    parser.add_argument(
        'new', help='Name to give new genome')
    parser.add_argument(
        'reads_1', help='Path to read pair 1')
    parser.add_argument(
        'reads_2', help='Path to read pair 2')
    parser.add_argument(
        'intermediate', help='Output directory for intermediate steps',
        default="scratch/maxh/intermediate/untreated_alignments")
    parser.add_argument(
        'results', help='Output directory for intermediate steps',
        default="scratch/maxh/results/untreated_alignments")
    parser.add_argument(
        'logs', help='Logs output directory',
        default=path.join(path.dirname(path.realpath(__file__)), "logs"))
    parser.add_argument(
        '-b', '--bwa', help='Don\'t perform BWA alignment',
        action='store_false')
    parser.add_argument(
        '-s', '--sort_bam',
        help='Don\'t sort the output alignment sam by genomic position and output bam',
        action='store_false')
    parser.add_argument(
        '-f', '--flagstat', help='Don\'t calculate the alignment statistics',
        action='store_false')
    parser.add_argument(
        '-m', '--mark_duplicates', help='Don\'t mark duplicate reads in sorted bam file',
        action='store_false')
    parser.add_argument(
        '-r', '--base_recalibrate', help='Don\'t recalibrate the base scores of the aligned reads',
        action='store_false')
    parser.add_argument(
        '-h', '--haplotype_caller', help='Don\'t use the haplotype caller to call variants',
        action='store_false')
    parser.add_argument(
        '-s', '--select_snps', help='Don\'t select SNPS from the haplotype caller vcf',
        action='store_false')
    parser.add_argument(
        '-i', '--select_indels', help='Don\'t select INDELS from the haplotype caller vcf',
        action='store_false')
    parser.add_argument(
        '-v', '--variant_filter', help='Don\'t filter out SNPs near INDELS',
        action='store_false')
    parser.add_argument(
        '-a', '--alternate_ref_make', help='Don\'t modify the current reference with the filtered SNPs',
        action='store_false')
    return parser.parse_args()


def customize(args):
    """Run the genome customization pipeline."""
    scriptDir = path.dirname(path.realpath(__file__))

    intermediateOut = path.join(args.intermediate, args.prefix)
    pathlib.Path(intermediateOut).mkdir(parents=True, exist_ok=True)

    statsOut = path.join(args.intermediate, args.prefix, "stats")
    pathlib.Path(statsOut).mkdir(parents=True, exist_ok=True)

    pathlib.Path(args.logs).mkdir(parents=True, exist_ok=True)

    variantsOut = path.join(args.results, args.prefix, "variants",)
    pathlib.Path(variantsOut).mkdir(parents=True, exist_ok=True)

    resultsOut = path.join(args.results, args.prefix)
    pathlib.Path(resultsOut).mkdir(parents=True, exist_ok=True)

    prevJob = None
    if args.bwa:
        cmd = (
            "sbatch --output=%s " % path.join(intermediateOut, f"{args.prefix}_bwa.sam") +
            "--error=%s " % path.join(args.logs, f"{args.prefix}_bwa_align_err.log") +
            path.join(scriptDir, "sbatch", "bwa_mem.sbatch") +
            f" {args.genome} {args.reads_1} {args.reads_2}")
        print(f"Creating job with command:\n\t{cmd}")
        submitted = subprocess.getoutput(cmd)
        print(submitted)
        prevJob = submitted.split(" ")[-1]
    if args.sort_bam:
        cmd = (
            basicOut(prevJob, "sort_bam", args.logs, args.prefix, scriptDir) +
            f" {intermediateOut}")
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))
    if args.flagstat:
        cmd = (
            f"sbatch --dependency=afterany:{prevJob}" +
            "--output=%s " % path.join(statsOut, f"{args.prefix}_alignment_metrics.txt") +
            "--error=%s " % path.join(args.logs, f"{args.prefix}_flagstat_err.log") +
            path.join(scriptDir, "sbatch", "flagstat.sbatch") +
            f" {intermediateOut}")
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))
    if args.mark_duplicates:
        cmd = (
            basicOut(prevJob, "mark_duplicates", args.logs, args.prefix, scriptDir) +
            f" {intermediateOut}")
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))
    if args.base_recalibrate:
        cmd = (
            basicOut(prevJob, "base_recalibrate", args.logs, args.prefix, scriptDir) +
            f" {intermediateOut} {args.genome} {args.vcf}")
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))
    if args.haplotype_caller:
        cmd = (
            basicOut(prevJob, "haplotype_caller", args.logs, args.prefix, scriptDir) +
            f" {variantsOut} {args.genome}")
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))
    if args.select_snps:
        cmd = (
            basicOut(prevJob, "select_snps", args.logs, args.prefix, scriptDir) +
            f" {variantsOut} {args.genome}")
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))
    if args.select_indels:
        cmd = (
            basicOut(prevJob, "select_indels", args.logs, args.prefix, scriptDir) +
            f" {variantsOut} {args.genome}")
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))
    if args.filter_snps:
        cmd = (
            basicOut(prevJob, "filter_snps", args.logs, args.prefix, scriptDir) +
            f" {variantsOut} {args.genome}")
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))
    if args.alternate_ref_make:
        cmd = (
            basicOut(prevJob, "alernate_ref_make", args.logs, args.prefix, scriptDir) +
            f" {args.genome} {variantsOut}_snps.vcf " +
            path.join(resultsOut, f"{args.new}"))
        print(f"Creating job with command:\n\t{cmd}")
        print(subprocess.getoutput(cmd))

    system("squeue -u maxh")


def basicOut(prevJob, scriptName, logs, prefix, scriptDir):
    """Produce the base of the cmds."""
    return (f"sbatch --dependency=afterany:{prevJob}" +
            "--output=%s " % path.join(logs, f"{prefix}_{scriptName}_out.log") +
            "--error=%s " % path.join(logs, f"{prefix}_{scriptName}_err.log") +
            path.join(scriptDir, "sbatch", f"{scriptName}.sbatch"))


def main():
    """Intiaties the logic of the program."""
    customize(parse())


if __name__ == "__main__":
    main()
