## Decompress the filltags useful for genome customization
kind=untreated

for sample in `cat samples.txt`; 
do
    mkdir -p logs/${sample}
    sbatch \
        --output=logs/$sample/${sample}_decompress_out.log \
        --error=logs/$sample/${sample}_decompress_err.log \
        --job-name=${sample}_decompress \
        scripts/decompress.sbatch \
            /scratch/maxh/data/${kind}_reads/filltag/${sample}_filltags.txt.gz;
    sbatch \
        --dependency=afterany:$SLURM_JOB_ID
        --output=logs/$sample/${sample}_filltag_to_fastq_out.log \
        --error=logs/$sample/${sample}_filltag_to_fastq_err.log \
        --job-name=${sample}_filltag_to_fastq \
        scripts/filltag_to_fastq.sbatch \
            /scratch/maxh/data/${kind}_reads/filltag/${sample}_filltags.txt \
            /scratch/maxh/data/${kind}_reads/raw_fastq \
            ${sample}
done

kind=bisulfite

for sample in `cat samples.txt`; 
do
    mkdir -p logs/${sample}
    sbatch \
        --output=logs/$sample/${sample}_decompress_out.log \
        --error=logs/$sample/${sample}_decompress_err.log \
        --job-name=${sample}_decompress \
        scripts/decompress.sbatch \
            /scratch/maxh/data/${kind}_reads/filltag/${sample}_filltags.txt.gz;
    sbatch \
        --dependency=afterany:$SLURM_JOB_ID
        --output=logs/$sample/${sample}_filltag_to_fastq_out.log \
        --error=logs/$sample/${sample}_filltag_to_fastq_err.log \
        --job-name=${sample}_filltag_to_fastq \
        scripts/filltag_to_fastq.sbatch \
            /scratch/maxh/data/${kind}_reads/filltag/${sample}_filltags.txt \
            /scratch/maxh/data/${kind}_reads/raw_fastq \
            ${sample}
done