"""Job submitting functions."""

import os
import subprocess
import pathlib


def baseDirs(logs, sample, path):
    """Create the logs (for the given sample) and script dirs."""
    pathlib.Path(logs).mkdir(parents=True, exist_ok=True)
    return (os.path.join(logs, sample),
            (os.path.join(os.path.dirname(path))))


def out(prevJob, scriptName, logs, scriptDir, sample, optional):
    """Produce the base of the cmds not depending on the previous job."""
    if prevJob and optional:
        return ("sbatch --dependency=afterany:%s" % ":".join(prevJob) +
                f"--output={logs}_{scriptName}_out.log " +
                f"--error={logs}_{scriptName}_err.log " +
                f"--job-name={sample}_{scriptName} " +
                f"{optional} " +
                os.path.join(scriptDir, f"{scriptName}") + " ")
    elif prevJob:
        return ("sbatch --dependency=afterany:%s" % ":".join(prevJob) +
                f"--output={logs}_{scriptName}_out.log " +
                f"--error={logs}_{scriptName}_err.log " +
                f"--job-name={sample}_{scriptName} " +
                os.path.join(scriptDir, f"{scriptName}") + " ")
    elif optional:
        return (f"sbatch " +
                f"--output={logs}_{scriptName}_out.log " +
                f"--error={logs}_{scriptName}_err.log " +
                f"--job-name={sample}_{scriptName} " +
                f"{optional} " +
                os.path.join(scriptDir, f"{scriptName}") + " ")
    else:
        return (f"sbatch " +
                f"--output={logs}_{scriptName}_out.log " +
                f"--error={logs}_{scriptName}_err.log " +
                f"--job-name={sample}_{scriptName} " +
                os.path.join(scriptDir, f"{scriptName}") + " ")


def submitJob(cmd):
    """Submit the job, print the output, return job number."""
    print(f"Creating job with command:\n\t{cmd}")
    submitted = subprocess.getoutput(cmd)
    print(submitted)
    return submitted.split(" ")[-1]


def job(prevJob, job, scriptName, logs, scriptDir, sample,
        optional, *args):
    """Template for job cmds."""
    # print(" ".join(args))
    cmd = ""
    if prevJob and job:
        cmd = (out(
            prevJob, scriptName, logs, scriptDir, sample, optional) +
            " " + " ".join(args))
    elif job:
        cmd = (out(0, scriptName, logs, scriptDir, sample, optional) +
               " " + " ".join(args))
    else:
        return prevJob

    return submitJob(cmd)
