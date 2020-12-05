from denoprolib import trinity

from configparser import ConfigParser
import argparse
import sys
import os
import pathlib 
import xml.etree.ElementTree as ET

class configReader():
    base_parser = argparse.ArgumentParser(add_help=False,
                                          formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    base_parser.add_argument('--config_file', '-c', metavar="<CONFIG_FILE>",
                             help='config file to use',
                             default=None)
    config = None

    def read_config(self, config_file):
        config = ConfigParser()
        config.read(config_file)
        return config
    
    def output_dir(self):
        if self.config.has_option('directory_locations', 'output_dir'):
            output_dir = self.config.get('directory_locations', 'output_dir')
        else:
            print("Please specify an output directory in the configuration file.")
        return output_dir
    
    def trinity_output_dir(self):
        if self.config.has_option('directory_locations', 'output_dir'):
            trinity_output = pathlib.PurePath(self.config.get('directory_locations', 'output_dir'), 'Trinity')
        else:
            print("Please specify an output directory in the configuration file.")
        return trinity_output

    def get_denopro_path(self):
        denopro_path = None
        if self.config.has_option('denopro_location', 'denopro_path'):
            path = self.config.get('denopro_location', 'denopro_path')
            if os.path.exists(path):
                denopro_path = path
            else:
                print("Please specify the path to where you originally"
                    " downloaded DeNoPro in the config file.")
        return denopro_path
    

class assemble(configReader):
    def __init__(self, **kwargs):
        if not kwargs:
            parser = argparse.ArgumentParser(
                description="Denovo assembly of RNAseq reads",
                parents=[self.base_parser],
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser.add_argument('--cpu', help="Maximum number of threads to be used by Trinity",
                                default = '30')
            parser.add_argument('--max_mem', help="Maximum amount of RAM (in Gs) that can be allocated",
                                default='50G')

            args = parser.parse_args(sys.argv[2:])

            self.cpu = args.cpu
            self.max_mem = args.max_mem
            config_file = args.config_file
        
        else:
            self.cpu = kwargs.get('cpu')
            self.max_mem = kwargs.get('max_mem')
            config_file = kwargs.get('config_file')
        
        self.config = self.read_config(config_file)

        self.output = self.trinity_output_dir()

        if self.config.has_option('directory_locations', 'fastq_for_trinity'):
            self.fastq = self.config.get('directory_locations', 'fastq_for_trinity')
        else:
            print("Please specify a directory containing FASTQ files")
        
        if self.config.has_option('dependency_locations', 'trinity'):
            self.trinity_path = self.config.get('dependency_locations', 'trinity')
        else:
            self.trinity_path = 'Trinity'

    def run(self):
        trinity.runTrinity(self.trinity_path, self.fastq, self.cpu, self.max_mem, self.output)

class searchguiPeptideshaker(configReader):
    def __init__(self, **kwargs):
        if not kwargs:
            parser = argparse.ArgumentParser(
                description="Custom peptide database from assembled transcripts",
                parents=[self.base_parser],
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            args = parser.parse_args(sys.argv[2:])

            config_file = args.config_file
        
        else:
            config_file = kwargs.get('config_file')
        
        self.config = self.read_config(config_file)

        self.trinity_out = self.trinity_output_dir()
        self.searchgui = self.config.get('dependency_locations', 'searchgui')
        self.peptideshaker = self.config.get('dependency_locations', 'peptideshaker')
        self.hg19 = self.config.get('dependency_locations', 'hg19')
        self.output = self.output_dir()
        self.denopropath = self.config.get('denopro_location', 'denopro_path')

        if self.config.has_option('directory_locations', 'spectra_files'):
            self.spectra = self.config.get('directory_locations', 'spectra_files')
        else:
            print("Please specify a directory containing MS/MS spectra files")

    def run(self):
        os.system(f"Rscript {self.denopropath}/denoprolib/Searchgui_peptideshaker_edit.R {self.spectra} {self.trinity_out} {self.searchgui} {self.peptideshaker} {self.hg19} {self.output}")

class novelPeptide(configReader):
    def __init__(self, **kwargs):
        if not kwargs:
            parser = argparse.ArgumentParser(
                description="identify confident novel peptides",
                parents=[self.base_parser],
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser.add_argument('--splice_graph','-s', help='Construct a variant splice graph')

            args = parser.parse_args(sys.argv[2:])

            self.splice_graph = args.splice_graph
            config_file = args.config_file

        else:
            self.splice_graph = kwargs.get('splice_graph')
            config_file = kwargs.get('config_file')
        
        self.config = self.read_config(config_file)
        self.output = self.output_dir()
        self.denopropath = self.config.get('denopro_location', 'denopro_path')

        if self.config.has_option('dependency_locations', 'actg'):
            self.actg = self.config.get('dependency_locations', 'actg')
        else:
            print("Please specify the directory containing ACTG.")

        if self.config.has_option('actg_options', 'transcriptome_gtf'):
            self.transcriptome_gtf = self.config.get('actg_options', 'transcriptome_gtf')

        if self.config.has_option('actg_options', 'mapping_method'):
            self.mapping_method = self.config.get('actg_options','mapping_method')
        else:
            print("Please specify a mapping method to use.")

        if self.config.has_option('actg_options', 'protein_database'):
            self.proteindb = self.config.get('actg_options','protein_database')
        else:
            print("Please specify a FASTA file containing protein database to be mapped.")

        if self.config.has_option('actg_options', 'serialization_file'):
            self.ser_file = self.config.get('actg_options','serialization_file')
        else:
            print("Please specify a path to the serialization file of variant splice graph.")

        if self.config.has_option('actg_options', 'ref_genome'):
            self.ref_genome = self.config.get('actg_options','ref_genome')
        else:
            print("Please specify a path to a reference genome.")

    def run(self):
        if self.splice_graph:
            tree = ET.parse(f"{self.actg}/const_params.xml")
            root = tree.getroot()
            
            root.find(".//Construction/Inputs/Input[@format='GTF']").text = self.transcriptome_gtf
            root.find(".//Construction/Inputs/Input[@format='FASTA']").text = self.ref_genome
            root.find(".//Construction/Outputs/Output").text = f"{self.output}/graph.ser"

            tree.write(f"{self.actg}/const_params.xml")
            os.system(f"java -Xmx8G -Xss2m -jar {self.actg}/ACTG_construction.jar const_params.xml")

            os.system(f"Rscript {self.denopropath}/denoprolib/novel_peptide_identification.R \
                {self.output} {self.actg} {self.mapping_method} {self.proteindb} {self.output}/graph.ser \
                    {self.ref_genome}")  
            os.system(f"Rscript {self.denopropath}/denoprolib/actg_summary.R {self.output}")          
        else: 
            os.system(f"Rscript {self.denopropath}/denoprolib/novel_peptide_identification.R \
                {self.output} {self.actg} {self.mapping_method} {self.proteindb} {self.ser_file} \
                    {self.ref_genome}")
            os.system(f"Rscript {self.denopropath}/denoprolib/actg_summary.R {self.output}")

class tcgaQuant(configReader):
    def __init__(self, **kwargs):
        if not kwargs:
            parser = argparse.ArgumentParser(
                description="Expression Level Quantification",
                parents=[self.base_parser],
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            
            args = parser.parse_args(sys.argv[2:])

            config_file = args.config_file
        else:
            config_file = kwargs.get('config_file')
        
        self.config = self.read_config(config_file)
        self.output = self.output_dir()
        self.denopropath = self.config.get('denopro_location', 'denopro_path')

        if self.config.has_option('quantification_options', 'bamstats'):
            self.bamstats = self.config.get('quantification_options','bamstats')
        else:
            print("Please specify a path to bamstats.")

        if self.config.has_option('quantification_options', 'bam_files'):
            self.bam_files = self.config.get('quantification_options','bam_files')
        else:
            print("Please specify a path to the BAM files to use.")

        if self.config.has_option('quantification_options', 'bed_file'):
            self.bed_file = self.config.get('quantification_options','bed_file')
        else:
            print("Please specify a path to the BED file to use.")

    def run(self):
        os.system(f"Rscript {self.denopropath}/denoprolib/bed_for_quant.R {self.output}")
        os.system(f"Rscript {self.denopropath}/denoprolib/TCGA_quantification.R {self.bamstats} \
            {self.bam_files} {self.bed_file} {self.output}")

class survivalAnalysis(configReader):
    def __init__(self, **kwargs):
        if not kwargs:
            parser = argparse.ArgumentParser(
                description="Survival Analysis",
                parents=[self.base_parser],
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            
            args = parser.parse_args(sys.argv[2:])

            config_file = args.config_file
        else:
            config_file = kwargs.get('config_file')
        
        self.config = self.read_config(config_file)
        self.output = self.output_dir()
        self.denopropath = self.config.get('denopro_location', 'denopro_path')

    def run(self):
        os.system(f"Rscript {self.denopropath}/denoprolib/Survival_analysis_novel_peptides.R {self.output}")

class potentialNovelORF(configReader):
    def __init__(self, **kwargs):
        if not kwargs:
            parser = argparse.ArgumentParser(
                description="Identify potential novel ORFsz",
                parents=[self.base_parser],
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            
            args = parser.parse_args(sys.argv[2:])

            config_file = args.config_file
        else:
            config_file = kwargs.get('config_file')
        
        self.config = self.read_config(config_file)
        self.output = self.output_dir()
        self.denopropath = self.config.get('denopro_location', 'denopro_path')

    def run(self):
        os.system(f"sh {self.denopropath}/denoprolib/Potential_novel_ORF.sh {self.output}")



