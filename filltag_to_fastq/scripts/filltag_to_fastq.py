"""Convert filltag format reads to fastq format."""

import argparse
import os
import pathlib
import subprocess
import contextlib
import re


def silentremove(*filenames):
    """Delete file if it exists."""
    with contextlib.suppress(FileNotFoundError):
        for filename in filenames:
            os.remove(filename)


def formatReadsAndCompress(args):
    """Convert the filltag reads to fastq and compress."""
    pathlib.Path(args.out).mkdir(parents=True, exist_ok=True)
    r1 = os.path.join(args.out, f"{args.prefix}_R1.fq")
    r2 = os.path.join(args.out, f"{args.prefix}_R2.fq")
    up = os.path.join(args.out, f"{args.prefix}_unpaired.fq")
    silentremove(r1, r2, up)
    with open(args.filltag, 'r') as filltag, \
            open(r1, 'a') as read1, \
            open(r2, 'a') as read2, \
            open(up, 'a') as unpaired:
        filltag.readline()
        filltag.readline()
        count = 1
        for line in filltag:
            line.rstrip()
            reads = re.compile(r"\s+").split(line)
            count += 1
            if (len(reads) == 4):
                unpaired.write(
                    f"@ID:{args.prefix}.{count}\n{reads[2]}\n+\n{reads[1]}\n")
            else:
                read1.write(
                    f"@ID:{args.prefix}.{count}\n{reads[3]}\n+\n{reads[1]}\n")
                read2.write(
                    f"@ID:{args.prefix}.{count}\n{reads[4]}\n+\n{reads[2]}\n")
            count += 1

    subprocess.run(["pigz", "-p", "16", args.filltag])
    subprocess.run(["pigz", "-p", "16", r1])
    subprocess.run(["pigz", "-p", "16", r2])
    subprocess.run(["pigz", "-p", "16", up])
    silentremove(r1, r2, up, args.filltag)


def main():
    """Parse the cmd line and pass arguments to formatter/compresser."""
    parser = argparse.ArgumentParser(
        description=('Converts filltag format reads to fasta'))
    parser.add_argument('filltag', help='The path to the filltag file')
    parser.add_argument('out', help='The output directory')
    parser.add_argument('prefix', help='Prefix for the fasta file')
    formatReadsAndCompress(parser.parse_args())


if __name__ == "__main__":
    main()
