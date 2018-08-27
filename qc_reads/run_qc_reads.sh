## Analyse quality, trim, reanalyze quality

kind=untreated

for sample in `cat samples.txt`; 
do
    python scripts/qc_and_trim.py \
        $kind \
        $sample \
        --fastqc_raw \
        --fastqc_out /scratch/maxh/results/fastqc_reports/ \
        --forward /scratch/maxh/data/${kind}_reads/raw_fastq/${sample}_R1_subset.fq.gz \
        --reverse /scratch/maxh/data/${kind}_reads/raw_fastq/${sample}_R2_subset.fq.gz \
        --unpaired /scratch/maxh/data/${kind}_reads/raw_fastq/${sample}_unpaired_subset.fq.gz
done 

python scripts/qc_and_trim.py \
        $kind \
        $sample \
        --fastqc_raw \
        --fastqc_out /scratch/maxh/results/fastqc_reports/ \
        --forward /scratch/maxh/data/${kind}_reads/raw_fastq/${sample}_R1_subset.fq.gz \
        --reverse /scratch/maxh/data/${kind}_reads/raw_fastq/${sample}_R2_subset.fq.gz \
        --unpaired /scratch/maxh/data/${kind}_reads/raw_fastq/${sample}_unpaired_subset.fq.gz