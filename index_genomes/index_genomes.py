"""Takes a path to a genome and indexes it."""

import argparse
import subprocess
import os


def index(name):
    """Indexes the genome."""
    cmd = f"sbatch --output=test/{name}.txt --error=logs/{name}.log test.sbatch {name}"
    print(f"Creating job with command:\n\t{cmd}")
    status, jobnum = subprocess.getstatusoutput(cmd)
    if (status == 0):
        print(jobnum)
    else:
        print("Error submitting test job!")

    os.system("squeue -u maxh")


def main():
    """Parse the command line arguments and pass on to functions."""
    parser = argparse.ArgumentParser(
        description='Performs the various indexing operations needed for a genome in the customization pipeline')
    parser.add_argument('name', default="test", help='The name you want for the output files')
    parser.add_argument('value', default="Max", help='The value you want printed')
    args = parser.parse_args()
    index(args.name)


if __name__ == "__main__":
    main()
