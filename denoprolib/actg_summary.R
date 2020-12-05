#!/usr/bin/Rscript
args <- commandArgs(TRUE)

library(plyr)
library(dplyr)
library(tidyr)
library(data.table)

output_dir = args[1]

setwd(output_dir)

flat_out<-list.files(pattern="*.flat$",recursive=TRUE)
flat_out
gff_out<-list.files(pattern="*.gff$",recursive=TRUE)
gff_out

for (k in 1:length(flat_out)) {
	r1<-read.delim(flat_out[k])
	print(flat_out[k])
	single<-names(which(table(r1$Peptide)==1))
	r2<-r1[r1$Peptide %in% single,]
	write.csv(r2,file=paste(flat_out[k],'csv',sep='.'))
	r3<-read.delim(gff_out[k],header=F)
	list <- strsplit(as.character(r3$V9), split="=")
	df <- ldply(list)
	library(plyr)
	df <- ldply(list)
	r3$GFFID<-df$V2
	r5<-merge(r2,r3,by="GFFID")
	write.csv(r5,paste(flat_out[k],"ACTG_peptides_gff_combined",'csv',sep='.'))
	}

nov_conf_pep_psm<-list.files(pattern="^Novel_Confident_Peptides_PSMs(.*)txt.csv$",recursive=TRUE)
actg_pep_gff<-list.files(pattern="*ACTG_peptides_gff_combined.csv",recursive=TRUE)
for(k in 1:length(nov_conf_pep_psm)) {
	r1<-read.csv(nov_conf_pep_psm[k])
	r2<-read.csv(paste(actg_pep_gff[k],sep=''))
	colnames(r2)[which(names(r2) == "Peptide")] <- "Sequence"
	m<-merge(r2,r1,by="Sequence")
	write.csv(m,paste(nov_conf_pep_psm[k],"combined_ACTG_peptides_PSMs",'csv',sep='.'))
	}

system(paste("find . -name '*.combined_ACTG_peptides_PSMs.csv' -exec cat {} \\;> ALL_NOVEL_PEPTIDES_ATCG.csv"))

r1<-read.csv("ALL_NOVEL_PEPTIDES_ATCG.csv")
r2<-r1[!duplicated(r1$Spectrum.Title),]
r3<-count(r2,Sequence)
m<-merge(r3,r1,by='Sequence')
r4<-r2[!duplicated(r2$Sequence),]
r5<-count(r4,GeneID)
m1<-merge(m,r5,by="GeneID")
write.csv(m1,"GENE_PEPTIDE_FILE_NUMBER_OF_PSMs_PEPTIDE_All.csv")
