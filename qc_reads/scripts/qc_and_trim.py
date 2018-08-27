"""Runs fastqc and trimmomatic jobs."""

import sys
import argparse
import subprocess
import os
import pathlib
import itertools
import jobs

# need to make sample name automatic and perform fastqc on each sample
# separately so i can output to seeparate log directories


def parseCmdLine():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(
        description=('Optionally runs fastqc on raw fastq reads, trims them '
                     'with trimmomatic, and runs fastqc on the trimmed '
                     'reads. Expects reads to by gzipped ending in fq.gz.'))
    parser.add_argument(
        'kind',
        help='The kind of reads [untreated/bisulfite/etc.].')
    parser.add_argument(
        'sample',
        help='The sample name.')
    parser.add_argument(
        'logs',
        help=('Logs output base directory. Logs will be placed in a '
              'subdirectory with the given sample as its name.'),
        nargs='?',
        default=os.path.join(os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))), "logs"))
    parser.add_argument(
        '-q', '--fastqc_raw',
        help=('Perform fastqc on raw reads.'),
        action='store_true')
    parser.add_argument(
        '-t', '--trim',
        help='Trim reads with trimmomatic.',
        action='store_true')
    parser.add_argument(
        '-w', '--fastqc_trimmed',
        help=('Perform fastqc on trimmed reads.'),
        action='store_true')
    parser.add_argument(
        '--fastqc_out',
        help=('The output directory for fastqc. Required if reads are to be '
              'quality assessed. Files will be placed in a subdirectory with '
              'the given read type [raw or trimmed] and sample as its name.'),
        required=('-q' in sys.argv or '--fastqc_raw' in sys.argv))
    parser.add_argument(
        '--trim_out',
        help=('The output directory for trimmomatic. Required if reads are '
              'to be trimmed. Files will be placed in a subdirectory with '
              'the given sample as its name.'),
        required=('-t' in sys.argv or '--trim' in sys.argv))
    parser.add_argument(
        '-d', "--dir",
        help=('A directory containing [forward, reverse, and/or unpaired] '
              'fastq files. Required if -forward, -reverse, and -r are not '
              'set'),
        required=not ((('-f' in sys.argv or '--forward' in sys.argv) and
                       ('-r' in sys.argv or '--reverse' in sys.argv)) or
                      ('-u' in sys.argv or '--unpaired' in sys.argv)))
    parser.add_argument(
        '-e', '--ends',
        help=('If -d or --dir is used use this to indicate whether '
              'forward, reverse, and unpaired reads are present [1], only '
              'forward and reverse reads are present [2], or only unpaired '
              'reads are present [3].'),
        type=int,
        choices=[1, 2, 3],
        required=('-d' in sys.argv or '--dir' in sys.argv))
    parser.add_argument(
        '-f', '--forward',
        help=('Paths to one or more raw or trimmed forward reads. Assumes in '
              'same order as -r and -u if used. Required if -d and -u are not '
              'used.'),
        action='append',
        required=(not ('-d' in sys.argv or '--dir' in sys.argv) or
                  ('-r' in sys.argv or '--reverse' in sys.argv)))
    parser.add_argument(
        '-r', '--reverse',
        help=('Paths to one or more raw or trimmed reverse reads. Assumes in '
              'same order as -f and -u if used. Required if -d and -u are '
              'not used.'),
        action='append',
        required=(not ('-d' in sys.argv or '--dir' in sys.argv) or
                  ('-f' in sys.argv or '--forward' in sys.argv)))
    parser.add_argument(
        '-u', '--unpaired',
        help=('Paths to one or more raw or trimmed unpaired reads. Assumes '
              'in same order as -f and -r if used, if not reads are '
              'processed as single end.'),
        action=('append'),
        required=not(('-d' in sys.argv or '--dir' in sys.argv) and
                     ('-f' in sys.argv or '--forward' in sys.argv) and
                     ('-r' in sys.argv or '--reverse' in sys.argv)))
    args = parser.parse_args()
    if args.fastqc_raw is None and args.trim is None and \
            args.fastqc_trimmed is None:
        parser.error('At least one of --fastqc_raw, --trim, '
                     '--fastqc_trimmed is requried.')
    return args


def fourTrimOut(trim, forward, reverse):
    """Create the four output file names for trimmomatic."""
    sampleF = forward.split(".fq.gz")[0]
    sampleR = reverse.split(".fq.gz")[0]
    return (f"{os.path.join(trim, sampleF)}_paired_trimmed.fq.gz",
            f"{os.path.join(trim, sampleF)}_unpaired_trimmed.fq.gz",
            f"{os.path.join(trim, sampleR)}_paired_trimmed.fq.gz",
            f"{os.path.join(trim, sampleR)}_unpaired_trimmed.fq.gz")


def trimPE(args, prevJob, logs, scriptDir, forward, reverse):
    """Trim paired-end fastq files."""
    pf, uf, pr, ur = fourTrimOut(args.trim_out, forward, reverse)
    prevJobPE = jobs.job(prevJob, args.trim, "trim_pe.sbatch", logs,
                         scriptDir, args.sample, 0, forward,
                         reverse, pf, uf, pr, ur)
    return (prevJobPE, pf, uf, pr, ur)


def trimSE(args, prevJob, logs, scriptDir, unpaired):
    """Trim single-end fastq files."""
    sePre = os.path.join(args.trim_out, unpaired.split('.fq.gz')[0])
    se = f"{sePre}_trimmed.fq.gz"
    prevJobSE = jobs.job(prevJob, args.trim, "trim_se.sbatch", logs,
                         scriptDir, args.sample, 0, unpaired, se)
    return (prevJobSE, se)


def fastqcTrimFastqc(args):
    """Run fastq and trimmomatic appropriately depending on options."""
    logs, scriptDir = jobs.baseDirs(args.logs, args.sample,
                                    os.path.realpath(__file__))

    fastqs = []
    if args.dir:
        fastqs = [file_ for file_ in os.listdir(
            args.dir) if file_.endswith(".fq.gz")]
    elif args.forward and args.reverse and args.unpaired:
        fastqs = list(itertools.chain(
            *zip(args.forward, args.reverse, args.unpaired)))
    elif args.forwards and args.reverese:
        fastqs = list(itertools.chain(*zip(args.forward, args.reverse)))
    else:
        fastqs = args.unpaired

    if args.fastqc_raw:
        fastqcRawOutDir = os.path.join(
            args.fastqc_out, os.path.join(
                f"raw_{args.kind}", f"{args.sample}_raw"))
        pathlib.Path(fastqcRawOutDir).mkdir(parents=True, exist_ok=True)
        prevJob = jobs.job(
            0, args.fastqc_raw, "fastqc.sbatch", logs, scriptDir, args.sample,
            f"--cpus-per-task={len(fastqs) // 2}", fastqcRawOutDir,
            " ".join(fastqs))

    if args.trim and args.fastqc_trimmed:
        fastqcTrimmedOutDir = os.path.join(
            args.fastqc_out, os.path.join(
                f"trimmed_{args.kind}", f"{args.sample}_trimmed"))
        pathlib.Path(fastqcTrimmedOutDir).mkdir(parents=True, exist_ok=True)
        trimmed = []
        prevJob2 = []
        if args.ends == 1 or \
                (args.forward and args.reverse and args.unpaired):
            for i in range(0, len(fastqs), 3):
                prevJobPE, pf, uf, pr, ur = trimPE(
                    args, prevJob, logs, scriptDir, fastqs[i],
                    fastqs[i+1])
                prevJobSE, se = trimSE(
                    args, prevJob, logs, scriptDir, fastqs[i+2])
                trimmed = [pf, uf, pr, ur, se]
                prevJob2 = (prevJobSE, prevJobPE)
        elif args.ends == 2 or (args.forward and args.reverse):
            for i in range(0, len(fastqs), 2):
                prevJob2, *trimmed = trimPE(
                    args, prevJob, logs, scriptDir, fastqs[i],
                    fastqs[i+1])
        else:
            for i in range(len(fastqs)):
                prevJob2, trimmed = trimSE(
                    args, prevJob, logs, scriptDir, fastqs[i])

        jobs.job(
            prevJob2, args.fastqc_trimmed, "fastqc.sbatch", logs,
            scriptDir, args.sample, f"--cpus-per-task={len(fastqs) // 2}",
            fastqcTrimmedOutDir, " ".join(trimmed))
    elif args.fastqc_trimmed:
        fastqcTrimmedOutDir = os.path.join(
            args.fastqc_out, os.path.join(
                f"trimmed_{args.kind}", f"{args.sample}_trimmed"))
        pathlib.Path(fastqcTrimmedOutDir).mkdir(parents=True, exist_ok=True)
        jobs.job(
            prevJob2, args.fastqc_trimmed, "fastqc.sbatch", logs,
            scriptDir, args.sample, f"--cpus-per-task={len(fastqs) // 2}",
            fastqcTrimmedOutDir, " ".join(fastqs))


def main():
    """Parse cmd line arguments and pass to functions."""
    fastqcTrimFastqc(parseCmdLine())


if __name__ == "__main__":
    main()
