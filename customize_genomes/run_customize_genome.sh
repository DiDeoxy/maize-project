sbatch \
    --output=logs/customize_genome_out.log \
    --error=logs/customize_genome_err.log \
    scripts/customize_genome.py -d \
        /scratch/maxh/data/v4_B73_genome/Zea_mays.AGPv4.dna.toplevel.fa \
        /scratch/maxh/data/v4_B73_genome/zea_mays_sorted2.vcf \
        EF09B \
        EF09B_one_pass \
        /scratch/maxh/data/untreated_reads/trimmed_fastq/EF09B_R1_paired.fq.gz
        /scratch/maxh/data/untreated_reads/trimmed_fastq/EF09B_R2_paired.fq.gz
        