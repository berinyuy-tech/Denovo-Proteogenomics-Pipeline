#!/usr/bin/Rscript
args <- commandArgs(TRUE)

output_dir = args[1]

setwd(output_dir)

r1<-read.csv("GENE_PEPTIDE_FILE_NUMBER_OF_PSMs_PEPTIDE_ALL.csv") #PEPTIDE PSM FILE AFTER ACTG
r2<-r1[,c(2,3,8,11,12)]
r2$id<-paste(r2$V1,r2$V4,r2$V5,r2$GeneID,r2$Sequence,sep="_") #Extract chromosomal locations
r3<-r2[!duplicated(r2$id),]
mat<-r3
r3$id<-NULL
r3$GeneID<-NULL
r3$Sequence<-NULL
write.table(r3,row.names=F,col.names = F,quote=FALSE,file=paste("Novel_peptides_chromosomal_locations.bed"),sep="\t")
