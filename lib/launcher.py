import argparse
import sys
import time
import os

from lib.tasks import assemble, searchguiPeptideshaker, novelPeptide, tcgaQuant, survivalAnalysis, potentialNovelORF
from lib import denoprogui

class launchGUI(argparse.Action):
    def __call__(self, parser, values, namespace, option_string):
        print("Launching GUI")
        time.sleep(1)
        denoprogui.main()
        parser.exit()

def launch():
    parser = argparse.ArgumentParser(
        description = 'DeNoPro: Denovo Proteogenomics Pipeline to identify clinically relevant novel variants from RNAseq and Proteomics data',
        usage = """ 
        
             # # # # # # # # # # # # # # # # # # # # # # # # # # 
            #    __            _              ___                #
            #   |  \          | \    |       |   \               #
            #   |   \     _   |  |   |   _   |    \   __    _    #
            #   |    \   / \  |  \   |  / \  |    /  /  \  / \   #
            #   |     | | _/  |   |  | |   | |___/  |     |   |  #
            #   |    /   \__/ |   \  |  \_/  |      |      \_/   #
            #   |   /         |    | |       |                   #
            #   |__/          |    \_|       |                   #
            #                                                    #
             # # # # # # # # # # # # # # # # # # # # # # # # # # 
        
                        denopro <mode> [<args>]
                                  OR
                            denopro -g/--gui

        Modes are:

            - assemble: de novo assembly of transcript sequences using Trinity
            - searchdb: produces custom peptide database from assembled transcripts 
                         which are mapped against proteomics data
            - identify: maps potential novel peptides from searchdb to a reference 
                         tracriptome, outputting a list of confident novel peptides
            - novelorf: finds novel ORFs in identified novel peptides
            - quantify: evaluates expression levels of identified novel peptides in a sample
            

        denopro <mode> -h for specific help
        """)
    parser.add_argument('mode', metavar = "<MODE>", help = 'denopro mode (assemble, customdb, findnovel, survival or novelorf)',
                        choices = ['assemble', 'searchdb', 'identify', 'novelorf', 'quantify'])
    parser.add_argument('-g','--gui', help = 'Launches the GUI functionality',nargs = 0, action=launchGUI)
    args = parser.parse_args(sys.argv[1:2])

    modes = {
        'assemble': assemble,
        'searchdb': searchguiPeptideshaker,
        'identify': novelPeptide,
        'quantify': tcgaQuant,
        #'survival': survivalAnalysis,
        'novelorf': potentialNovelORF
    }

    print(parser.usage)
    time.sleep(1)

    if args.mode not in modes:
        print("Unsupported mode")
        parser.print_help()
        exit(1)

    Mode = modes[args.mode]
    Mode().run()

    