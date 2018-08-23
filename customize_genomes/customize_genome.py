"""Takes a path to a genome and indexes it."""

import argparse
import subprocess
from os import path, system
import pathlib


def parseCmdLine():
    """Parse the command line options."""
    parser = argparse.ArgumentParser(
        description=('Performs the various steps needed to for a single pass '
                     'genome customization'))
    parser.add_argument(
        'genome', help='The path to the genome file')
    parser.add_argument(
        'vcf', help='The path to the genome\'s vcf file')
    parser.add_argument(
        'prefix', help='Base name to give intermediate files')
    parser.add_argument(
        'new', help='Name to give new genome')
    parser.add_argument(
        'reads_1', help='Path to read fasta pair 1')
    parser.add_argument(
        'reads_2', help='Path to read fasta pair 2')
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
        '-c', '--caller_haplotype', help='Don\'t use the haplotype caller to call variants',
        action='store_false')
    parser.add_argument(
        '-d', '--select_snps', help='Don\'t select SNPS from the haplotype caller vcf',
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


def customizeGenomePipeline(args):
    """Run the genome customization pipeline."""
    scriptDir = path.dirname(path.realpath(__file__))

    intermediateOutDir = path.join(args.intermediate, args.prefix)
    pathlib.Path(intermediateOutDir).mkdir(parents=True, exist_ok=True)
    intermediateOut = path.join(intermediateOutDir, args.prefix)

    statsOutDir = path.join(args.intermediate, args.prefix, "stats")
    pathlib.Path(statsOutDir).mkdir(parents=True, exist_ok=True)
    statsOut = path.join(statsOutDir, args.prefix)

    pathlib.Path(args.logs).mkdir(parents=True, exist_ok=True)
    logs = path.join(args.logs, args.prefix)

    variantsOutDir = path.join(args.results, args.prefix, "variants")
    pathlib.Path(variantsOutDir).mkdir(parents=True, exist_ok=True)
    variantsOut = path.join(variantsOutDir, args.prefix)

    resultsOutDir = path.join(args.results, args.prefix)
    pathlib.Path(resultsOutDir).mkdir(parents=True, exist_ok=True)
    resultsOut = path.join(resultsOutDir, args.new)

    prevJob = None
    if args.bwa:
        cmd = (
            f"sbatch --output={intermediateOut}_bwa.sam " +
            f"--error={logs}_bwa_align_err.log " +
            path.join(scriptDir, "sbatch", "bwa_mem.sbatch") +
            f" {args.genome} {args.reads_1} {args.reads_2}")
        prevJob = submitJob(cmd)
    if args.sort_bam:
        prevJob = genericJob(args.bwa, prevJob, "sort_bam",
                             logs, args.prefix, scriptDir, intermediateOut)
    if args.flagstat:
        if args.sort_bam:
            cmd = (
                f"sbatch --dependency=afterany:{prevJob}" +
                f"--output={statsOut}_alignment_metrics.txt " +
                f"--error={logs}_flagsts_err.log " +
                path.join(scriptDir, "sbatch", "flagstat.sbatch") +
                intermediateOut)
            prevJob = submitJob(cmd)
        else:
            cmd = (
                f"sbatch " +
                f"--output={statsOut}_alignment_metrics.txt " +
                f"--error={logs}_flagsts_err.log " +
                path.join(scriptDir, "sbatch", "flagstat.sbatch") +
                intermediateOut)
            prevJob = submitJob(cmd)
    if args.mark_duplicates:
        prevJob = genericJob(args.flagstat, prevJob, "mark_duplicates",
                             logs, args.prefix, scriptDir, intermediateOut)
    if args.base_recalibrate:
        prevJob = genericJob(args.mark_duplicates, prevJob,
                             "base_recalibrate", logs, args.prefix, scriptDir,
                             intermediateOut, args.genome, args.vcf)
    if args.caller_haplotype:
        prevJob = genericJob(args.base_recalibrate, prevJob,
                             "caller_haplotype", logs, args.prefix, scriptDir,
                             variantsOut, args.genome)
    if args.select_snps:
        prevJob = genericJob(args.caller_haplotype, prevJob,
                             "select_snps", logs, args.prefix, scriptDir,
                             variantsOut, args.genome)
    if args.select_indels:
        prevJob = genericJob(args.select_snps, prevJob,
                             "select_indels", logs, args.prefix, scriptDir,
                             variantsOut, args.genome)
    if args.filter_snps:
        prevJob = genericJob(args.select_indels, prevJob,
                             "filter_snps", logs, args.prefix, scriptDir,
                             variantsOut, args.genome)
    if args.alternate_ref_make:
        prevJob = genericJob(args.filter_snps, prevJob,
                             "alternate_ref_make", logs, args.prefix, scriptDir,
                             args.genome, variantsOut, resultsOut)

    system("squeue -u maxh")


def basicOut(scriptName, logs, prefix, scriptDir):
    """Produce the base of the cmds not depending on the previous job."""
    return (f"sbatch " +
            f"--output={logs}_{scriptName}_out.log " +
            f"--error={logs}_{scriptName}_err.log " +
            path.join(scriptDir, "sbatch", f"{scriptName}.sbatch")) + " "


def basicOutPrev(prevJob, scriptName, logs, prefix, scriptDir):
    """Produce the base of the cmds depending on the previous job."""
    return (f"sbatch --dependency=afterany:{prevJob}" +
            f"--output={logs}_{scriptName}_out.log " +
            f"--error={logs}_{scriptName}_err.log " +
            path.join(scriptDir, "sbatch", f"{scriptName}.sbatch")) + " "


def submitJob(cmd):
    """Submit the job, print the output, return job number."""
    print(f"Creating job with command:\n\t{cmd}")
    submitted = subprocess.getoutput(cmd)
    print(submitted)
    return submitted.split(" ")[-1]


def genericJob(prevTask, prevJob, scriptName, logs, prefix, scriptDir, *args):
    """Template for job cmds."""
    cmd = ""
    if prevTask:
        cmd = (
            basicOutPrev(prevJob, scriptName, logs, prefix, scriptDir) +
            " " + " ".join(args)
        )
    else:
        cmd = (
            basicOut(scriptName, logs, prefix, scriptDir) +
            " " + " ".join(args)
        )
    return submitJob(cmd)


def main():
    """Intiaties the logic of the program."""
    customizeGenomePipeline(parseCmdLine())


if __name__ == "__main__":
    main()
