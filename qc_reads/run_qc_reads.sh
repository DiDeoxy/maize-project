## Analyse quality, trim, reanalyze quality

kind=untreated

for sample in `cat samples.txt`; 
do
    sbatch \
        --output=logs/${sample}_qc_and_trim_out.log \
        --error=logs/${sample}_qc_and_trim_err.log \
        scripts/qc_and_trim.py -d -t -f\
            ${kind} \
            /scratch/maxh/results/fastqc_reports \
            --read1 /scratch/maxh/data/${kind}_reads/raw_fastq
            --trim_dir /scratch/maxh/data/$kind/trimmed_fastq
done 

    

