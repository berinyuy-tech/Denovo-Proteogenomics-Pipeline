#!/usr/bin/Rscript
args <- commandArgs(TRUE)

bamstats = args[1]
bam_files = args[2]
bed_file = args[3]
output_dir = args[4]

setwd(output_dir)

#TCGA BAM file quantification

system(paste(sprintf("find %s -type f -name \\*.bam | parallel -j 8 'java -jar %s -B %s {} > {.}_coverage.txt'", bam_files, bamstats, bed_file))) # Quantification of peptide loci in each bam file  
system(paste("find ",bam_files," -type f -name \\*coverage.txt -exec cat {} + >mergedfile.txt"))  # merging all the coverage files.
system(paste("grep -vwE '(#chrom)' mergedfile.txt > merged_file_HEADER_REMOVED.txt")) # remove headers
r1<-read.delim("merged_file_HEADER_REMOVED.txt",header=FALSE)
r2<-r1[,c(5,8)] #extract average expression of each peptide
r2[r2==0]<-NA #converting 0 to NA
write.table(r2,"GPR56_PROTEOGENOMICS_mergedfile_header_removed_NA_added.txt",sep="\t",col.names=F)
system(paste("awk '1 {if (a[$2]) {a[$2] = a[$2]\" \"$3} else {a[$2] = $3}} END {for (i in a) { print i,a[i]}}' GPR56_PROTEOGENOMICS_mergedfile_header_removed_NA_added.txt >GPR56_PROTEOGENOMICS_ALL_TRANSPOSED.txt"))
r1<-read.delim("GPR56_PROTEOGENOMICS_ALL_TRANSPOSED.txt",header=FALSE,sep=" ")
rownames(r1)<-r1[,1]
r1<-r1[,-1]
colnames(r1)<-mat$id
r1[is.na(r1)] <- 0
r1$id<-rownames(r1)
write.csv(r1,"GPR56_PROTEOGENOMICS_all_transposed_with_na_header_added.csv")
r1$id <- substr(r1$id, 0, 16)
r3<-read.csv("gpr56_mapped_reads.csv") # Each Sample total mapped reads
m<-merge(r3,r1,by="id") 
m1<-m[!duplicated(m$id),]
rownames(m1)<-m1[,1]
m1<-m1[,-1]
m2<-(m1/(m1$readcount))*1000000 #CPM normalisation
m2$readcount<-NULL
write.csv(m2,"GPR56_GENE_PEPTIDE_FILE_NUMBER_OF_PEPTIDES_NORMALISED_COUNT.csv")
