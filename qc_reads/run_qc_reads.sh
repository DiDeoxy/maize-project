sbatch \
    --output=logs/qc_and_trim_out.log \
    --error=logs/qc_and_trim_err.log \
    scripts/qc_and_trim.py -d \
        untreated \
        /scratch/maxh/results/fastqc_reports \
        --read1 /scratch/maxh/data/untreated_reads/raw_fastq
        --trim_dir /scratch/maxh/data/untreated/trimmed_fastq
    

