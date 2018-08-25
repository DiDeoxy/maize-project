"""Job submitting functions."""

import os
import subprocess
import pathlib


def baseDirs(logs, prefix, path):
    """Create the logs and script dirs."""
    pathlib.Path(logs).mkdir(parents=True, exist_ok=True)
    return (os.path.join(logs, prefix),
            (os.path.join(os.path.dirname(os.path.dirname(path)), "scripts")))


def basicOut(scriptName, logs, scriptDir):
    """Produce the base of the cmds not depending on the previous job."""
    return (f"sbatch " +
            f"--output={logs}_{scriptName}_out.log " +
            f"--error={logs}_{scriptName}_err.log " +
            os.path.join(scriptDir, f"{scriptName}.sbatch") + " ")


def basicOutPrev(prevJob, scriptName, logs, scriptDir):
    """Produce the base of the cmds depending on the previous job."""
    return (f"sbatch --dependency=afterany:{prevJob}" +
            f"--output={logs}_{scriptName}_out.log " +
            f"--error={logs}_{scriptName}_err.log " +
            os.path.join(scriptDir, f"{scriptName}.sbatch") + " ")


def submitJob(cmd):
    """Submit the job, print the output, return job number."""
    print(f"Creating job with command:\n\t{cmd}")
    submitted = subprocess.getoutput(cmd)
    print(submitted)
    return submitted.split(" ")[-1]


def genericJob(prevJob, job, scriptName, logs, scriptDir, *args):
    """Template for job cmds."""
    cmd = ""
    if prevJob and job:
        cmd = (basicOutPrev(prevJob, scriptName, logs, scriptDir) +
               " " + " ".join(args))
    elif job:
        cmd = (basicOut(scriptName, logs, scriptDir) +
               " " + " ".join(args))
    else:
        return prevJob

    return submitJob(cmd)
