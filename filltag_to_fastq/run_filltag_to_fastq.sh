## Decompress the filltags 
# sbatch \
#     --output=logs/EF09B_decompress_out.log \
#     --error=logs/EF09B_decompress_err.log \
#     scripts/decompress.sbatch \
#         /scratch/maxh/data/untreated_reads/filltag/EF09B_filltags.txt.gz
sbatch \
    --output=logs/GR581_decompress_out.log \
    --error=logs/GR581_decompress_err.log \
    scripts/decompress.sbatch \
        /scratch/maxh/data/untreated_reads/filltag/GR581_filltags.txt.gz
sbatch \
    --output=logs/HG11_decompress_out.log \
    --error=logs/HG11_decompress_err.log \
    scripts/decompress.sbatch \
        /scratch/maxh/data/untreated_reads/filltag/HG11_filltags.txt.gz
sbatch \
    --output=logs/EF09Bmop1_decompress_out.log \
    --error=logs/EF09Bmop1_decompress_err.log \
    scripts/decompress.sbatch \
        /scratch/maxh/data/untreated_reads/filltag/EF09Bmop1_filltags.txt.gz
sbatch \
    --output=logs/GR581mop1_decompress_out.log \
    --error=logs/GR581mop1_decompress_err.log \
    scripts/decompress.sbatch \
        /scratch/maxh/data/untreated_reads/filltag/GR581mop1_filltags.txt.gz
sbatch \
    --output=logs/HG11mop1_decompress_out.log \
    --error=logs/HG11mop1_decompress_err.log \
    scripts/decompress.sbatch \
        /scratch/maxh/data/untreated_reads/filltag/HG11mop1_filltags.txt.gz
#
# ## Convert filltags to fastq
# sbatch \
#     --output=logs/EF09B_filltag_to_fastq_out.log \
#     --error=logs/EF09B_filltag_to_fastq_err.log \
#     scripts/filltag_to_fastq.sbatch \
#         /scratch/maxh/data/untreated_reads/filltag \
#         /scratch/maxh/data/untreated_reads/raw_fastq \
#         EF09B