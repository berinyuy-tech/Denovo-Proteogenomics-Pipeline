cd $1
cat *_txFinder.fasta >all_txfinder.fasta # combine trinity fasta files of all experiments
awk '/^>/ {printf("\n%s\n",$0);next; } { printf("%s",$0);}  END {printf("\n");}' <all_txfinder.fasta> all_txfinder_linearlised.fasta #linearise the fasta file
blastp -query all_txfinder_linearlised.fasta -db Homo_sapiens.GRCh38.pep.all.fa -num_threads 8 -max_target_seqs 1 -outfmt 6 -evalue 1e-5 > blastp.outfmt6 # blastp protein search trinity fasta file against Homo_sapiens GRCh38
cat unix |sed 's/\|/ /'|awk '{print $1}' blastp_all_ntx.outfmt6 non_potential_ORF_sequence_ids.txt # Get sequence id column of blastp.outfmt6
seqtk subseq all_txfinder_linearlised.fasta non_potential_ORF_sequence_ids.txt >all_txfinder_linearlised_subseq.fasta # subselect Non potential ORF sequences
while read l; do grep "$l" all_txfinder_linearlised_subseq.fasta | wc -l ;done < all_novel_peptides.txt>ORF_peptides.txt # 0 count for a peptide indicates they are part of novel ORF sequences.
