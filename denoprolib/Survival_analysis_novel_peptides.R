#!/usr/bin/Rscript
args <- commandArgs(TRUE)

library("data.table")
library("reshape2")
library("survival")
library("survminer")

working_dir = args[1]
setwd(working_dir)

T1<-read.csv("GENE_PEPTIDE_FILE_NUMBER_OF_PEPTIDES_NORMALISED_COUNT.csv",header=TRUE)
colnames(T1)[1]<-"id"
DT1 = melt(T1,variable.name = "id")
colnames(DT1)<-c("id","gene","value")
OS<-read.csv("OS_breast_cancer.csv")
m<-merge(DT1,OS,by="id")
subtypes<-read.csv("subgroups_BRCA_pam.csv")
m1<-merge(m,subtypes,by="id")

#Survival Analysis overall BRCA cohort

m1 <-as.data.table(m1)
m1[, expr := ifelse(findInterval(value, mean(value)) == 1, "high", "low"), by = gene]
m<-as.data.frame(m)
m1$group <- paste(m1$gene,m1$expr,sep="_")
dfs = split(m1,f=m1$gene)
fit<-lapply(seq_along(dfs) ,function(x) surv_fit(Surv(OS.time, OS) ~ group,data = dfs[[x]]))
p <- ggsurvplot_list(fit,
  data = dfs,
  risk.table = FALSE,
  pval = TRUE) 
pdf("survival_plots_overall.pdf",width=20)
p
dev.off()
f1<-surv_pvalue(fit)
f1.df <- do.call("rbind", lapply(f1, as.data.frame))
write.csv(f1.df,"Survival_p-value_novel_peptides_BRCA_overall.csv")

#Survival Analysis Luminal Subtype of BRCA

m2<-subset(m1,PAM50Call_RNAseq=="LumA" | PAM50Call_RNAseq=="LumB")
m2 <-as.data.table(m2)
m2[, expr := ifelse(findInterval(value, mean(value)) == 1, "high", "low"), by = gene]
m2<-as.data.frame(m2)
m2$group <- paste(m2$gene,m2$expr,sep="_")
dfs = split(m2,f=m2$gene)
fit<-lapply(seq_along(dfs) ,function(x) surv_fit(Surv(OS.time, OS) ~ group,data = dfs[[x]]))
p <- ggsurvplot_list(fit,
  data = dfs,
  risk.table = FALSE,
  pval = TRUE) 
pdf("survival_plot_luminal.pdf",width=20)
p
dev.off()
f1<-surv_pvalue(fit)
f1.df <- do.call("rbind", lapply(f1, as.data.frame))
write.csv(f1.df,"Survival_p-value_novel_peptides_BRCA_Luminal.csv")

#Survival Analysis Basal Subtype of BRCA

m2<-subset(m1,PAM50Call_RNAseq=="Basal")
m2 <-as.data.table(m2)
m2[, expr := ifelse(findInterval(value, mean(value)) == 1, "high", "low"), by = gene]
m2<-as.data.frame(m2)
m2$group <- paste(m2$gene,m2$expr,sep="_")
dfs = split(m2,f=m2$gene)
fit<-lapply(seq_along(dfs) ,function(x) surv_fit(Surv(OS.time, OS) ~ group,data = dfs[[x]]))
p <- ggsurvplot_list(fit,
  data = dfs,
  risk.table = FALSE,
  pval = TRUE) 
pdf("survival_plots_basal.pdf",width=20)
p
dev.off()
f1<-surv_pvalue(fit)
f1.df <- do.call("rbind", lapply(f1, as.data.frame))
write.csv(f1.df,"Survival_p-value_novel_peptides_BRCA_Basal.csv")

#Survival Analysis Her2 Subtype of BRCA

m2<-subset(m1,PAM50Call_RNAseq=="Basal")
m2 <-as.data.table(m2)
m2[, expr := ifelse(findInterval(value, mean(value)) == 1, "high", "low"), by = gene]
m2<-as.data.frame(m2)
m2$group <- paste(m2$gene,m2$expr,sep="_")
dfs = split(m2,f=m2$gene)
fit<-lapply(seq_along(dfs) ,function(x) surv_fit(Surv(OS.time, OS) ~ group,data = dfs[[x]]))
p <- ggsurvplot_list(fit,
  data = dfs,
  risk.table = FALSE,
  pval = TRUE) 
pdf("survival_plots_her2.pdf",width=20)
p
dev.off()
f1<-surv_pvalue(fit)
f1.df <- do.call("rbind", lapply(f1, as.data.frame))
write.csv(f1.df,"Survival_p-value_novel_peptides_BRCA_her2.csv")

