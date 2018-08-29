#!~/METHYL/bin/python

import argparse, subprocess, os

parser = argparse.ArgumentParser(description='Tests running a batch file with python')
parser.add_argument('name', default="test", help='The name you want for the output files')
parser.add_argument('value', default="Max", help='The value you want printed')
args = parser.parse_args()

# run test job
cmd = f"sbatch --output=test/{args.name}.txt --error=logs/{args.name}.log test.sbatch {args.value}"
print(f"Creating job with command:\n\t{cmd}")
status, jobnum = subprocess.getstatusoutput(cmd)
if (status == 0):
    print(jobnum)
else:
    print("Error submitting test job!")

os.system("squeue -u maxh")