"""Runs fastqc and trimmomatic jobs."""

import sys
import argparse
import subprocess
import os
import pathlib
import jobs


def parseCmdLine():
    """Parse the command lien arguments."""
    parser = argparse.ArgumentParser(
        description=('Optionally runs fastqc on raw fastq reads, trims them '
                     'with trimmomatic, and runs fastqc on the trimmed '
                     'reads. Expects reads to by gzipped ending in fq.gz.'))
    parser.add_argument(
        'prefix',
        help='The prefix of reads [untreated/bisulfite/etc.].')
    parser.add_argument(
        'logs',
        help='Logs output directory.',
        nargs='?',
        default=os.path.join(os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))), "logs"))
    parser.add_argument(
        '-q', '--fastqc',
        help=('Don\'t perform fastqc.'),
        action='store_false')
    parser.add_argument(
        '-t', '--trim',
        help='Don\'t trim reads reads.',
        action='store_false')
    parser.add_argument(
        '--fastqc_out',
        help='The output directory for fastqc.',
        required=not ('-r' in sys.argv or '--raw_fastqc' in sys.argv))
    parser.add_argument(
        '--trim_out',
        help=('The output directory for trimmomatic. Required if reads are '
              'to be trimmed'),
        required=not ('-t' in sys.argv or '--trim' in sys.argv))
    parser.add_argument(
        '-d', "--dir",
        help=('A directory containing forward, [reverse, and unpaired] fastq '
              'files. Required is -f, -u, or -r are not set'),
        required=not (('-f' in sys.argv or '--forward' in sys.argv) or
                      #   ('-r' in sys.argv or '--reverse' in sys.argv) or
                      ('-u' in sys.argv or '--unpaired' in sys.argv)))
    parser.add_argument(
        '-f', '--forward',
        help=('Paths to raw or trimmed forward reads. Assumes in same order '
              'as -r and -u if used. Required if -d and -u are not used.'),
        action='append',
        required=not (('-d' in sys.argv or '--dir' in sys.argv) or
                      ('-u' in sys.argv or '--unpaired' in sys.argv)))
    parser.add_argument(
        '-r' '--reverse',
        help=('Paths to raw or trimmed reverse reads. Assumes in same order '
              'as -f and -u if used. Required if -d and -u are not used.'),
        action='append',
        required=not (('-d' in sys.argv or '--dir' in sys.argv) or
                      ('-u' in sys.argv or '--unpaired' in sys.argv)))
    parser.add_argument(
        '-u', '--unpaired',
        help=('Paths to raw or trimmed unpaired reads. Assumes in same order '
              'as -f and -r if used. If -d or --dir is used becomes an '
              'indicator for whether unpaired reads are present in additon '
              'to forward and reverse. Used for single end reads if -f and '
              '-r are not used.'),
        action='store_true' if ('-d' in sys.argv or '--dir' in sys.argv)
        else 'append',
        required=not (('-f' in sys.argv or '--forward' in sys.argv) and
                      ('-r' in sys.argv or '--reverse' in sys.argv)))
    return parser.parse_args()


def readTrimPipeline(args):
    """Run fastqc on the input file or directory."""
    logs, scriptDir = jobs.baseDirs(args.logs, args.prefix,
                                    os.path.realpath(__file__))

    fastqcRawOutDir = os.path.join(args.fastqc_out, f"raw_{args.prefix}")
    pathlib.Path(fastqcRawOutDir).mkdir(parents=True, exist_ok=True)

    fastqcTrimmedOutDir = os.path.join(
        args.fastqc_out, f"trimmed_{args.prefix}")
    pathlib.Path(fastqcTrimmedOutDir).mkdir(parents=True, exist_ok=True)

    if args.dir and args.unpaired:
        raw_fastqs = [file_ for file_ in os.listdir(
            args.dir) if file_.endswith(".fq.gz")]
        prevJob = jobs.genericJob(0, args.fastqc, "fastqc_raw", logs,
                                  scriptDir, args.prefix, fastqcRawOutDir,
                                  " ".join(raw_fastqs))
        if args.trim:
            for i in range(0, len(raw_fastqs), 3):
                pf, uf, pr, ur = fourTrim(args.trim_dir,
                                          raw_fastqs[i].split(".fq.gz")[0],
                                          raw_fastqs[i+1].split(".fq.gz")[0])

                prevJob = jobs.genericJob(prevJob, args.trim, "trim_pe", logs,
                                          scriptDir, args.prefix,
                                          raw_fastqs[i], raw_fastqs[i+1],
                                          pf, uf, pr, ur)
                se = os.path.join(args.trim_dir, raw_fastqs[i+2].split(
                    ".fq.gz")[0])
                prevJob = jobs.genericJob(prevJob, args.trim, "trim_se", logs,
                                          scriptDir, args.prefix,
                                          raw_fastqs[i+2], se)
                jobs.genericJob(prevJob, args.fastqc_trimmed,
                                "fastqc_trimmed", logs, scriptDir,
                                args.prefix, fastqcTrimmedOutDir,
                                " ".join([pf, uf, pr, ur, se]))
        else:
            trimmed_fastqs = [file_ for file_ in os.listdir(
                args.read1) if file_.endswith(".fq.gz")]
            jobs.genericJob(prevJob, args.fastqc_trimmed, "fastqc_trimmed",
                            logs, scriptDir, args.prefix,
                            fastqcTrimmedOutDir, " ".join(trimmed_fastqs))
    else:
        prevJob = jobs.genericJob(prevJob, args.raw_fastqc, "fastqc_raw",
                                  logs, scriptDir, args.prefix,
                                  fastqcRawOutDir,
                                  " ".join([args.read1, args.read2]))
        if args.trim:
            pf, uf, pr, ur = fourTrim(args.trim_dir, args.read1.split(".")[0],
                                      args.read2.split(".")[0])
            prevJob = jobs.genericJob(prevJob, args.trim, "trim", logs,
                                      scriptDir, args.prefix,
                                      args.read1, args.read2, pf, uf, pr, ur)
            jobs.genericJob(prevJob, args.fastqc_trimmed, "fastqc_trimmed",
                            logs, scriptDir, args.prefix,
                            fastqcTrimmedOutDir, " ".join([pf, uf, pr, ur]))
        else:
            jobs.genericJob(prevJob, args.fastqc_trimmed, "fastqc_trimmed",
                            logs, scriptDir, args.prefix,
                            fastqcTrimmedOutDir,
                            " ".join([args.read1, args.read2]))


def fourTrim(trim, prefix1, prefix2):
    """Create the four output file names for trimmomatic."""
    return (f"{os.path.join(trim, prefix1)}_paired.fq.gz",
            f"{os.path.join(trim, prefix1)}_unpaired.fq.gz",
            f"{os.path.join(trim, prefix2)}_paired.fq.gz",
            f"{os.path.join(trim, prefix2)}_unpaired.fq.gz")


def main():
    """Parse cmd line arguments and pass to functions."""
    readTrimPipeline(parseCmdLine())


if __name__ == "__main__":
    main()
