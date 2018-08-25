"""Runs fastqc and trimmomatic jobs."""

import argparse
import subprocess
import os
import pathlib
import jobs


def parseCmdLine():
    """Parse the command lien arguments."""
    parser = argparse.ArgumentParser(
        description=('Runs fastqc on raw fastq reads, trims them with '
                     'trimmomatic, and then runs fastqc on the trimmed reads'))
    parser.add_argument(
        '-d', "--dir",
        help=('Run on all paired fastq files in directory.\n'
              'Files must be paired end and in consecutive order'),
        action='store_true')
    parser.add_argument(
        'prefix',
        help='The prefix of reads [untreated/bisulfite/etc.]')
    parser.add_argument(
        'fastqc_out',
        help='The path to the base output directory for fastqc')
    parser.add_argument(
        'logs',
        help='Logs output directory',
        nargs='?',
        default=os.path.join(os.path.dirname(os.path.dirname(
            os.path.realpath(__file__))), "logs"))
    parser.add_argument(
        '--read1',
        help=('The path to the forward raw or trimmed fastq reads or the '
              'directory containing paired consecutive forward and reverse '
              'reads'),
        required=True)
    parser.add_argument(
        '--read2',
        help='The path to the reverse raw or trimmed fastq reads')
    parser.add_argument(
        '--trim_dir',
        help='The path to the trimmed fastq file/directory')
    parser.add_argument(
        '-r', '--raw_fastqc',
        help=('Don\'t perform fastqc on raw reads. '
              'Flag if submitting trimmed reads'),
        action='store_false')
    parser.add_argument(
        '-t', '--trim',
        help='Don\'t perform trim reads reads',
        action='store_false')
    parser.add_argument(
        '-f', '--fastqc_trimmed',
        help='Don\'t perform fastqc on trimmed reads',
        action='store_false')
    return parser.parse_args()


def readTrimPipeline(args):
    """Run fastqc on the input file or directory."""
    logs, scriptDir = jobs.baseDirs(args.logs, args.prefix,
                                    os.path.realpath(__file__))

    fastqcRaw = f"raw_{args.prefix}"
    fastqcRawOutDir = os.path.join(args.fastqc_out, fastqcRaw)
    pathlib.Path(fastqcRawOutDir).mkdir(parents=True, exist_ok=True)

    fastqcTrimmed = f"trimmed_{args.prefix}"
    fastqcTrimmedOutDir = os.path.join(args.fastqc_out, fastqcTrimmed)
    pathlib.Path(fastqcTrimmedOutDir).mkdir(parents=True, exist_ok=True)

    if args.dir:
        raw_fastqs = [file_ for file_ in os.listdir(
            args.read1) if file_.endswith(".fq.gz")]
        prevJob = jobs.genericJob(0, args.raw_fastqc, "fastqc_raw", logs,
                                  scriptDir,
                                  fastqcRawOutDir, " ".join(raw_fastqs))
        if args.trim:
            for i in range(0, len(raw_fastqs), 2):
                pf, uf, pr, ur = fourTrim(args.trim_dir,
                                          raw_fastqs[1].split(".")[0],
                                          raw_fastqs[2].split(".")[0])
                prevJob = jobs.genericJob(prevJob, args.trim, "trim", logs,
                                          scriptDir,
                                          raw_fastqs[i], raw_fastqs[i+1],
                                          pf, uf, pr, ur)
                jobs.genericJob(prevJob, args.fastqc_trimmed,
                                "fastqc_trimmed", logs, scriptDir,
                                fastqcTrimmedOutDir, pf, uf, pr, ur)
        else:
            trimmed_fastqs = [file_ for file_ in os.listdir(
                args.read1) if file_.endswith(".fq.gz")]
            jobs.genericJob(prevJob, args.fastqc_trimmed, "fastqc_trimmed",
                            logs, scriptDir,
                            fastqcTrimmedOutDir, *trimmed_fastqs)
    else:
        prevJob = jobs.genericJob(prevJob, args.raw_fastqc, "fastqc_raw",
                                  logs, scriptDir,
                                  fastqcRawOutDir, args.raw)
        if args.trim:
            pf, uf, pr, ur = fourTrim(args.trim_dir, args.read1.split(".")[0],
                                      args.read2.split(".")[0])
            prevJob = jobs.genericJob(prevJob, args.trim, "trim", logs,
                                      scriptDir,
                                      args.read1, args.read2, pf, uf, pr, ur)
            jobs.genericJob(prevJob, args.fastqc_trimmed, "fastqc_trimmed",
                            logs, scriptDir,
                            fastqcTrimmedOutDir, pf, uf, pr, ur)
        else:
            jobs.genericJob(prevJob, args.fastqc_trimmed, "fastqc_trimmed",
                            logs, scriptDir,
                            fastqcTrimmedOutDir, args.read1, args.read2)

    os.system("squeue -u maxh")


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
