#!/usr/bin/Rscript
args <- commandArgs(TRUE)

library(plyr)
library(dplyr)
library(tidyr)
library(data.table)
library(XML)

output_dir = args[1]
actg_dir = args[2]
mapping_method = args[3]
proteindb = args[4]
ser_file = args[5]
ref_genome = args[6]

setwd(output_dir)

peptide_report<-list.files(pattern="*Peptide_Report.txt",recursive=TRUE)
psm_report<-list.files(pattern="*PSM_Report.txt",recursive=TRUE)

for (k in 1:length(peptide_report)){
	r1<-read.delim(peptide_report[k])
	print(peptide_report[k])
	r2<-subset(r1, !grepl("^NP_", r1$Protein.s.))
	r3<-r2[!duplicated(r2$Sequence),]
	r3<-subset(r3,Validation=="Confident")
	r4<-read.delim(psm_report[k])
	print(psm_report[k])

	m<-merge(r4,r3,by="Sequence")
	m1<-m[,c("Sequence","Protein.s..x","Modified.Sequence.x","Variable.Modifications.x","Fixed.Modifications.x","Spectrum.Title","Confidence.....x","Validation.x")]
	m2<-subset(m1,Validation.x=="Confident")
	
    list <- strsplit(as.character(peptide_report[k]), split="/")
	df <- ldply(list)
	write.csv(m2,file=paste("Novel_Confident_Peptides_PSMs",df$V1,'csv',sep='.'))
	}

conf_peptide_psm<-list.files(pattern="^Novel_Confident_Peptides_PSMs",recursive=TRUE)

for (k in 1:length(conf_peptide_psm)) {
	r1<-read.csv(conf_peptide_psm[k])
	print(conf_peptide_psm[k])
	r2<-r1[!duplicated(r1$Sequence),]
	list <- strsplit(as.character(conf_peptide_psm[k]), split="/")
	df1 <- ldply(list)
	r3<-r2$Sequence
	r3<-as.data.frame(r3)
	write.table(r3,row.names=F,col.names = F,quote=FALSE,file=paste("novel_peptides_for_ACTG",df1$V1,'txt',sep='.'))
	}

peptide_for_actg<-list.files(pattern="^novel_peptides_for_ACTG",recursive=TRUE)

# Edit and prepare ACTG's mapping_params.xml
mapping <- xmlParse(file.path(actg_dir,"mapping_params.xml"))

invisible(replaceNodes(mapping[["//Environment/MappingMethod/text()"]], newXMLTextNode(mapping_method)))
invisible(replaceNodes(mapping[["//Environment/Output/text()"]], newXMLTextNode(output_dir)))
invisible(replaceNodes(mapping[["//ProteinDB/Input/text()"]], newXMLTextNode(proteindb)))
invisible(replaceNodes(mapping[["//VariantSpliceGraph/Input[@type='graphFile']/text()"]], newXMLTextNode(ser_file)))
invisible(replaceNodes(mapping[["//SixFrameTranslation/Input/text()"]], newXMLTextNode(ref_genome)))
saveXML(mapping, file = file.path(actg_dir,'mapping_params.xml'))

for (k in 1:length(peptide_for_actg)) {
#	data <- xmlParse(actg_dir,"/mapping_params.xml")
	invisible(replaceNodes(mapping[["//Input/text()"]], newXMLTextNode(peptide_for_actg[k])))
	list <- strsplit(as.character(peptide_for_actg[k]), split="/")
	df1 <- ldply(list)
	saveXML(mapping,file=paste(df1$V1,'xml',sep='.'))
	}


xml_out<-list.files(pattern="*txt.xml",recursive=TRUE)
for (k in 1:length(xml_out)) {
	i<-xml_out[k]
	print(i)
	cmd<-paste("java -Xmx8G -Xss2m -jar ",file.path(actg_dir,'ACTG_mapping.jar')," ",i)
	system(cmd)
	}
