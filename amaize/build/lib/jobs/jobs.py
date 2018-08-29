"""Job submitting functions."""

import os
import subprocess
import pathlib
import tempfile


def baseDirs(logs, sample, path):
    """Create the logs (for the given sample) and script dirs."""
    pathlib.Path(logs).mkdir(parents=True, exist_ok=True)
    return (os.path.join(logs, sample),
            (os.path.join(os.path.dirname(path))))


def out(prevJob, logs, task, scriptName, scriptDir, sample, optional):
    """Produce the base of the cmds not depending on the previous job."""
    same = (f"--output={logs}_{task}_out.log "
            f"--error={logs}_{task}_err.log "
            f"--job-name={sample}_{task} ")
    if prevJob and optional:
        return ("sbatch --dependency=afterany:%s" % ":".join(prevJob) +
                same +
                f"{optional} " +
                os.path.join(scriptDir, f"{scriptName}") + " ")
    elif prevJob:
        return ("sbatch --dependency=afterany:%s" % ":".join(prevJob) +
                same +
                os.path.join(scriptDir, f"{scriptName}") + " ")
    elif optional:
        return (f"sbatch " +
                same +
                f"{optional} " +
                os.path.join(scriptDir, f"{scriptName}") + " ")
    else:
        return (f"sbatch " +
                same +
                os.path.join(scriptDir, f"{scriptName}") + " ")


def submitJob(cmd):
    """Submit the job, print the output, return job number."""
    print(f"Creating job with command:\n\n{cmd}\n")
    submitted = subprocess.getoutput(cmd)
    print(submitted)
    return submitted.split(" ")[-1]


def job(prevJob, job, logs, task, scriptName, scriptDir, sample,
        optional, *files):
    """Template for job cmds."""
    cmd = ""
    if prevJob and job:
        cmd = (out(
            prevJob, logs, task, scriptName, scriptDir, sample, optional) +
            " " + " ".join(files))
    elif job:
        cmd = (out(0, logs, task, scriptName, scriptDir, sample, optional) +
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
