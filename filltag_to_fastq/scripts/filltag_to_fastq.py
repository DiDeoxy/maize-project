"""Convert filltag format reads to fastq format."""

import argparse
import os
import pathlib
import subprocess


def formatReadsAndCompress(args):
    """Convert the filltag reads to fastq and compress."""
    pathlib.Path(args.out).mkdir(parents=True, exist_ok=True)
    r1 = os.path.join(args.out, f"{args.prefix}_R1.fq")
    r2 = os.path.join(args.out, f"{args.prefix}_R2.fq")
    with open(args.filltag, 'r') as filltag, \
            open(r1, 'a') as read1, \
            open(r2, 'a') as read2:
        count = 1
        for line in filltag:
            line.rstrip()
            reads = line.split(" ")
            if ((not reads[0].startswith("#")) and (len(reads) > 4)):
                read1.write(
                    f"@ID:{args.prefix}.{count}\n{reads[3]}\n+\n{reads[1]}\n")
                read2.write(
                    f"@ID:{args.prefix}.{count}\n{reads[4]}\n+\n{reads[2]}\n")
                count += 1
    subprocess.run(f"pigz -p 16 {r1}")
    subprocess.run(f"pigz -p 16 {r2}")


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
