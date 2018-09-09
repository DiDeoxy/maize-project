"""Job submitting functions."""

import os
import subprocess
import pathlib
import tempfile


def out(prevJob, logs, task, scriptName, sample, optional):
    """Produce the base of the cmds not depending on the previous job."""
    same = (f"--output=%s " % os.path.join(logs, f"{sample}_{task}_out.log") +
            f"--error=%s " % os.path.join(logs, f"{sample}_{task}_err.log") +
            f"--job-name={sample}_{task} "
            "%s" + scriptName)
    if prevJob and optional:
        return ("sbatch --dependency=afterany:%s" %
                ":".join(prevJob) if len(prevJob) > 1 else prevJob +
                same % optional)
    elif prevJob:
        return ("sbatch --dependency=afterany:%s" %
                ":".join(prevJob) if len(prevJob) > 1 else prevJob +
                same % "")
    elif optional:
        return (f"sbatch " + same % optional)
    else:
        return (f"sbatch " + same % "")


def submitJob(cmd):
    """Submit the job, print the output, return job number."""
    print(f"Creating job with command:\n\n{cmd}\n")
    submitted = subprocess.getoutput(cmd)
    print(submitted)
    return submitted.split(" ")[-1]


def job(prevJob, job, logs, task, scriptName, sample, optional, *files):
    """Template for job cmds."""
    cmd = ""
    if prevJob and job:
        cmd = (out(
            prevJob, logs, task, scriptName, sample, optional) +
            " " + " ".join(files))
    elif job:
        cmd = (out(0, logs, task, scriptName, sample, optional) +
               " " + " ".join(files))
    else:
        return prevJob

    return submitJob(cmd)


def tempScript(script):
    """Write a string as a temp bash file."""
    scriptfile = tempfile.NamedTemporaryFile(delete=False, mode='w')
    scriptfile.write(script)
    scriptfile.close()
    return scriptfile


def outDir(*components):
    """Create a directory path and make it if it doesnt exist."""
    od = os.path.join(*components)
    pathlib.Path(od).mkdir(parents=True, exist_ok=True)
    return od
