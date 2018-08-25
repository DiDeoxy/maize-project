jid1=$(sbatch --output=test_out.log --error=test_err.log test.sbatch Max)
# echo $jid1