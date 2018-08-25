"""Takes a path to a genome and indexes it."""

import argparse
import subprocess
import os
import pathlib
import jobs


def parseCmdLine():
    """Parse the command line options."""
    parser = argparse.ArgumentParser(
        description=('Performs the various steps needed to for a single pass '
                     'genome customization'))
    parser.add_argument(
        'genome',
        help='The path to the genome file')
    parser.add_argument(
        'vcf',
        help='The path to the genome\'s vcf file')
    parser.add_argument(
        'prefix',
        help='Base name to give intermediate files')
    parser.add_argument(
        'new',
        help='Name to give new genome')
    parser.add_argument(
        'reads1',
        help='Path to read fasta pair 1')
    parser.add_argument(
        'reads2',
        help='Path to read fasta pair 2')
    parser.add_argument(
        'intermediate',
        help='Output directory for intermediate steps',
        nargs='?',
        default="scratch/maxh/intermediate/untreated_alignments")
    parser.add_argument(
        'results',
        help='Output directory for intermediate steps',
        nargs='?',
        default="scratch/maxh/results/untreated_alignments")
    parser.add_argument(
        'logs',
        help='Logs output directory',
        nargs='?',
        default=os.path.join(os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))), "logs"))
    parser.add_argument(
        '-b', '--bwa',
        help='Don\'t perform BWA alignment',
        action='store_false')
    parser.add_argument(
        '-s', '--sort_bam',
        help=('Don\'t sort the output alignment sam'
              'by genomic position and output bam'),
        action='store_false')
    parser.add_argument(
        '-f', '--flagstat',
        help='Don\'t calculate the alignment statistics',
        action='store_false')
    parser.add_argument(
        '-m', '--mark_duplicates',
        help='Don\'t mark duplicate reads in sorted bam file',
        action='store_false')
    parser.add_argument(
        '-r', '--base_recalibrate',
        help='Don\'t recalibrate the base scores of the aligned reads',
        action='store_false')
    parser.add_argument(
        '-c', '--caller_haplotype',
        help='Don\'t use the haplotype caller to call variants',
        action='store_false')
    parser.add_argument(
        '-d', '--select_snps',
        help='Don\'t select SNPS from the haplotype caller vcf',
        action='store_false')
    parser.add_argument(
        '-i', '--select_indels',
        help='Don\'t select INDELS from the haplotype caller vcf',
        action='store_false')
    parser.add_argument(
        '-v', '--variant_filter',
        help='Don\'t filter out SNPs near INDELS',
        action='store_false')
    parser.add_argument(
        '-a', '--alternate_ref_make',
        help='Don\'t modify the current reference with the filtered SNPs',
        action='store_false')
    return parser.parse_args()


def customizeGenomePipeline(args):
    """Run the genome customization pipeline."""
    logs, scriptDir = jobs.baseDirs(args.logs, args.prefix,
                                    os.path.realpath(__file__))

    intermediateOutDir = os.path.join(args.intermediate, args.prefix)
    pathlib.Path(intermediateOutDir).mkdir(parents=True, exist_ok=True)
    intermediateOut = os.path.join(intermediateOutDir, args.prefix)

    resultsOutDir = os.path.join(args.results, args.prefix)
    pathlib.Path(resultsOutDir).mkdir(parents=True, exist_ok=True)
    resultsOut = os.path.join(resultsOutDir, args.new)

    variantsOutDir = os.path.join(resultsOutDir, "variants")
    pathlib.Path(variantsOutDir).mkdir(parents=True, exist_ok=True)
    variantsOut = os.path.join(variantsOutDir, args.prefix)

    statsOutDir = os.path.join(resultsOutDir, "stats")
    pathlib.Path(statsOutDir).mkdir(parents=True, exist_ok=True)
    statsOut = os.path.join(statsOutDir, args.prefix)

    prevJob = 0
    if args.bwa:
        cmd = (f"sbatch " +
               f"--output={intermediateOut}_bwa.sam " +
               f"--error={logs}_bwa_align_err.log " +
               os.path.join(scriptDir, "bwa_mem.sbatch") +
               f" {args.genome} {args.reads1} {args.reads2}")
        prevJob = jobs.submitJob(cmd)
    prevJob = jobs.genericJob(prevJob, args.sort_bam, "sort_bam",
                              logs, scriptDir,
                              intermediateOut)
    if prevJob and args.flagstat:
        cmd = (f"sbatch --dependency=afterany:{prevJob}" +
               f"--output={statsOut}_alignment_metrics.txt " +
               f"--error={logs}_flagstats_err.log " +
               os.path.join(scriptDir, "flagstat.sbatch") +
               intermediateOut)
        prevJob = jobs.submitJob(cmd)
    elif args.flagstat:
        cmd = (f"sbatch " +
               f"--output={statsOut}_alignment_metrics.txt " +
               f"--error={logs}_flagstats_err.log " +
               os.path.join(scriptDir, "flagstat.sbatch") +
               intermediateOut)
        prevJob = jobs.submitJob(cmd)
    prevJob = jobs.genericJob(prevJob, args.mark_duplicates,
                              "mark_duplicates", logs, scriptDir,
                              intermediateOut)
    prevJob = jobs.genericJob(prevJob, args.base_recalibrate,
                              "base_recalibrator", logs, scriptDir,
                              intermediateOut, args.genome, args.vcf)
    prevJob = jobs.genericJob(prevJob, args.caller_haplotype,
                              "haplotype_caller", logs, scriptDir,
                              variantsOut, args.genome)
    prevJob = jobs.genericJob(prevJob, args.select_snps, "select_snps",
                              logs, scriptDir, variantsOut, args.genome)
    prevJob = jobs.genericJob(prevJob, args.select_indels, "select_indels",
                              logs, scriptDir, variantsOut, args.genome)
    prevJob = jobs.genericJob(prevJob, args.filter_snps, "filter_snps",
                              logs, scriptDir, variantsOut, args.genome)
    prevJob = jobs.genericJob(prevJob, args.alternate_ref_make,
                              "make_alternate_ref", logs, scriptDir,
                              args.genome, variantsOut, resultsOut)

    subprocess.run("squeue -u maxh")


def main():
    """Initiaties the logic of the program."""
    customizeGenomePipeline(parseCmdLine())


if __name__ == "__main__":
    main()
