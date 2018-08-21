#!~/METHYL/bin/python

import argparse, subprocess, os

parser = argparse.ArgumentParser(description='Schedules all the jobs for a single pass genome customization')
parser.add_argument('name', default="test", help='The name you want for the output files')
parser.add_argument('genome', default="data/v4_B73_genome/Zea_mays.AGPv4.dna.toplevel.fa", help='The genome you wnat to customize')
args = parser.parse_args()

# run test job
cmd = f"sbatch --output=test/{args.name}.txt --error=logs/{args.name}.log test.sbatch {args.name}"
print(f"Creating job with command:\n\t{cmd}")
status, jobnum = subprocess.getstatusoutput(cmd)
if (status == 0):
    print(jobnum)
else:
    print("Error submitting test job!")

os.system("squeue -u maxh")