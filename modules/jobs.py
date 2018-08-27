"""Job submitting functions."""

import os
import subprocess
import pathlib


def baseDirs(logs, prefix, path):
    """Create the logs (for the given prefix) and script dirs."""
    pathlib.Path(logs).mkdir(parents=True, exist_ok=True)
    return (os.path.join(logs, prefix),
            (os.path.join(os.path.dirname(path))))


def basicOut(scriptName, logs, scriptDir, prefix):
    """Produce the base of the cmds not depending on the previous job."""
    return (f"sbatch " +
            f"--output={logs}_{scriptName}_out.log " +
            f"--error={logs}_{scriptName}_err.log " +
            f"--job-name={prefix}_{scriptName}" +
            os.path.join(scriptDir, f"{scriptName}.sbatch") + " ")


def basicOutPrev(prevJob, scriptName, logs, scriptDir, prefix):
    """Produce the base of the cmds depending on the previous job."""
    return (f"sbatch --dependency=afterany:{prevJob}" +
            f"--output={logs}_{scriptName}_out.log " +
            f"--error={logs}_{scriptName}_err.log " +
            f"--job-name={prefix}_{scriptName}" +
            os.path.join(scriptDir, f"{scriptName}.sbatch") + " ")


def submitJob(cmd):
    """Submit the job, print the output, return job number."""
    print(f"Creating job with command:\n\t{cmd}")
    submitted = subprocess.getoutput(cmd)
    print(submitted)
    return submitted.split(" ")[-1]


def genericJob(prevJob, job, scriptName, logs, scriptDir, prefix, *args):
    """Template for job cmds."""
    cmd = ""
    if prevJob and job:
        cmd = (basicOutPrev(prevJob, scriptName, logs, scriptDir, prefix) +
               " " + " ".join(args))
    elif job:
        cmd = (basicOut(scriptName, logs, scriptDir, prefix) +
               " " + " ".join(args))
    else:
        return prevJob

    return submitJob(cmd)
