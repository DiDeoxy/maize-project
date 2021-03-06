"""Runs fastqc and trimmomatic jobs."""

import argparse
import itertools
import os
import sys

from amaize import jobs, sbatch


def baseParser(parser):
    """Parse common arguments."""
    parser.add_argument(
        'kind',
        help='The kind of reads [WGS/bisulfite/untreated/etc.].')
    parser.add_argument(
        'logs',
        help=('Logs output base directory. Defaults to a directory called '
              'logs in the same directory as the script. Creates '
              'subdirectories based on sample names extracted from file name '
              'using --separator.'),
        nargs='?',
        default=os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "logs"))
    parser.add_argument(
        '-s', '--separator',
        help='The symbol separting the sample name in the file names from '
        'the rest of the name. Defuault: underscore, \"_\"',
        nargs="?",
        default='_')
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
    return parser


def parseCmdLine():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(
        description=('Optionally runs fastqc on raw fastq reads, trims them '
                     'with trimmomatic, and runs fastqc on the trimmed '
                     'reads. Expects reads to by gzipped ending in fq.gz.'))

    subparsers = parser.add_subparsers(help='sub-command [-h, --help]',
                                       dest="command")
    parserDir = subparsers.add_parser(
        'DIR',
        help=('Run program in directory mode. Performs operations on '
              'compressed fastq files in a directory.'))
    parserDir = baseParser(parserDir)
    parserDir.add_argument(
        'dir',
        help=('The directory containing the compressed fastq files. Expects '
              'extension .fq.gz'))
    parserDir.add_argument(
        '-e', '--ends',
        help=('Indicate whether forward, reverse, and unpaired reads are '
              'present [1], only forward and reverse reads are present [2], '
              'or only unpaired reads are present [3].'),
        type=int,
        choices=[1, 2, 3])
    parserFiles = subparsers.add_parser(
        'FILES',
        help=('Run program in file mode. Performs operations on supplied '
              'forward, reverse, and unpaired reads if supplied.'))
    parserFiles = baseParser(parserFiles)
    parserFiles.add_argument(
        '-f', '--forward',
        help=('Paths to one or more raw or trimmed forward reads. Assumes in '
              'same order as -r and -u if used. Required if -r is used.'),
        action='append',
        required=('-r' in sys.argv or '--reverse' in sys.argv))
    parserFiles.add_argument(
        '-r', '--reverse',
        help=('Paths to one or more raw or trimmed reverse reads. Assumes in '
              'same order as -f and -u if used. Required if -f is used.'),
        action='append',
        required=('-f' in sys.argv or '--forward' in sys.argv))
    parserFiles.add_argument(
        '-u', '--unpaired',
        help=('Paths to one or more raw or trimmed unpaired reads. Assumes '
              'in same order as -f and -r if used. Otherwise reads are '
              'processed as single end.'),
        action=('append'))

    args = parser.parse_args()
    if args.fastqc_raw is None and args.trim is None and \
            args.fastqc_trimmed is None:
        parser.error('At least one of --fastqc_raw, --trim, '
                     '--fastqc_trimmed is requried.')

    return args


def fourTrimOut(trimDir, forward, reverse):
    """Create the four output file names for trimmomatic."""
    sampleF = forward.split(".fq.gz")[0]
    sampleR = reverse.split(".fq.gz")[0]
    return (os.path.join(trimDir, f"{sampleF}_paired_trimmed.fq.gz"),
            os.path.join(trimDir, f"{sampleF}_unpaired_trimmed.fq.gz"),
            os.path.join(trimDir, f"{sampleR}_paired_trimmed.fq.gz"),
            os.path.join(trimDir, f"{sampleR}_unpaired_trimmed.fq.gz"))


def trimPE(args, prevJob, logs, trimDir, sample, forward, reverse):
    """Trim paired-end fastq files."""
    pf, uf, pr, ur = fourTrimOut(trimDir, forward, reverse)
    tpe = jobs.tempScript(sbatch.trimPEScript())
    prevJobPE = jobs.job(prevJob, args.trim, logs, "trim_PE", tpe.name, sample,
                         0, forward, reverse, pf, uf, pr, ur)
    os.unlink(tpe.name)
    return (prevJobPE, pf, uf, pr, ur)


def trimSE(args, prevJob, logs, trimDir, sample, unpaired):
    """Trim single-end fastq files."""
    se = os.path.join(trimDir, f"{unpaired.split('.fq.gz')[0]}_trimmed.fq.gz")
    tse = jobs.tempScript(sbatch.trimSEScript())
    prevJobSE = jobs.job(prevJob, args.trim, logs, "trim_SE", tse.name, sample,
                         0, unpaired, se)
    os.unlink(tse.name)
    return (prevJobSE, se)


def trim(args, prevJob, outDir, sample, *reads):
    """Trim fastq files."""
    trimDir = jobs.outDir(args.trim_out, outDir)
    logs = jobs.outDir(args.logs, outDir)
    if len(reads) == 3:
        prevJobPE, pf, uf, pr, ur = trimPE(
            args, prevJob, logs, trimDir, sample, reads[0], reads[1])
        prevJobSE, se = trimSE(args, prevJob, logs, trimDir, sample, reads[2])
        return (prevJobPE, prevJobSE), (pf, uf, pr, ur, se)
    elif len(reads) == 2:
        prevJobPE, pf, uf, pr, ur = trimPE(
            args, prevJob, logs, trimDir, sample, reads[0], reads[1])
        return prevJobPE, (pf, uf, pr, ur)
    else:
        prevJobSE, se = trimSE(args, prevJob, logs, trimDir, sample, reads)


def fastqc(args, prevJob, outDir, sample, state, *fastqs):
    """Perform fastqc on the given reads."""
    fastqcRawOutDir = jobs.outDir(args.fastqc_out, outDir)
    logs = jobs.outDir(args.logs, outDir)
    fqc = jobs.tempScript(sbatch.fastqcScript())
    prevJob = jobs.job(
        prevJob, args.fastqc_raw, logs, f"fastqc_{state}", fqc.name, sample, 0,
        fastqcRawOutDir, *fastqs)
    os.unlink(fqc.name)
    return prevJob


def fastqcTrimFastqc(args, fastqs, n):
    """Fastqc and trim appropriately."""
    for i in range(0, len(fastqs), n):
        sample = os.path.basename(fastqs[i]).split(args.separator)[0]
        outDir = os.path.join(args.kind, sample)
        if args.fastqc_raw:
            prevJob = fastqc(args, 0, outDir, sample, "raw", *fastqs[i:i+n])
        if args.trim:
            prevJob, trimmed = trim(args, prevJob, outDir, sample,
                                    *fastqs[i:i+n])
            if args.fastqc_trimmed:
                prevJob = fastqc(args, prevJob, outDir, sample, "trimmed",
                                 *trimmed)
        elif args.fastqc_trimmed:
            fastqc(args, prevJob, outDir, sample, "trimmed", *fastqs[i:i+n])


def pipeline(args):
    """Run fastq and trimmomatic appropriately depending on options."""
    fastqs = []
    if args.command == "DIR":
        fastqs = [file_ for file_ in os.listdir(
            args.dir) if file_.endswith(".fq.gz")]
    elif args.forward and args.reverse and args.unpaired:
        fastqs = list(itertools.chain(
            *zip(args.forward, args.reverse, args.unpaired)))
    elif args.forward and args.reverse:
        fastqs = list(itertools.chain(*zip(args.forward, args.reverse)))
    else:
        fastqs = args.unpaired

    if (args.command == "DIR" and args.ends == 1) or \
            (args.forward and args.reverse and args.unpaired):
        fastqcTrimFastqc(args, fastqs, 3)
    elif args.ends == 2 or (args.forward and args.reverse):
        fastqcTrimFastqc(args, fastqs, 2)
    else:
        fastqcTrimFastqc(args, fastqs, 1)


def main():
    """Parse cmd line arguments and pass to functions."""
    pipeline(parseCmdLine())


if __name__ == "__main__":
    main()
