import configparser
import PySimpleGUIQt as sg
import subprocess
import sys
from os import path
from configparser import ConfigParser

# this dict will be updated and then saved to original conf file
conf_keys = {
    'output_dir': ['directory_locations','','-OUTDIR-'],
    'fastq_for_trinity': ['directory_locations','','-FASTQ-'],
    'spectra_files': ['directory_locations','','-SPECTRA-'],
    'trinity': ['dependency_locations','','-TRINITY-'],
    'hg19': ['dependency_locations','','-HG19-'],
    'searchgui': ['dependency_locations','','-SEARCHGUI-'],
    'peptideshaker': ['dependency_locations','','-PEPTIDE-'],
    'actg': ['dependency_locations','','-ACTG-'],
    'ref_genome': ['actg_options','','-REF-'],
    'transcriptome_gtf': ['actg_options','','-GTF-'],
    'mapping_method': ['actg_options','','-MAP-'],
    'protein_database': ['actg_options','','-DB-'],
    'serialization_file': ['actg_options','','-SER-'],
    'bamstats': ['quantification_options','','-BAMSTATS-'],
    'bam_files': ['quantification_options','','-BAM-'],
    'bed_file': ['quantification_options','','-BED-'],
    'denopro_path': ['denopro_location','','-DENOPRO-'],
    'theme': ['gui_settings','','-THEME-']
    }

default_conf = {
    'directory_locations': ['output_dir', 'fastq_for_trinity', 'spectra_files'],
    'dependency_locations': ['trinity', 'hg19', 'searchgui', 'peptideshaker', 'actg'],
    'actg_options': ['ref_genome','transcriptome_gtf', 'mapping_method', 'protein_database', 'serialization_file'],
    'quantification_options': ['bamstats', 'bam_files', 'bed_file'],
    'denopro_location': ['denopro_path'],
    'gui_settings': ['theme']
    }

############################################################    
#                     Functions
############################################################
def runCommand(cmd, timeout=None, window=None):
    p = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    output = ''
    for line in p.stdout:
        line = line.decode(errors='replace' if (sys.version_info) < (3, 5) else 'backslashreplace').rstrip()
        output += line
        print(line)
        window.refresh() if window else None
    
#    retval = p.wait(timeout)
#    return (retval,output)
    return output

def load_parser(config_file):
    parser = ConfigParser()
    parser.optionxform = str
    try:
        parser.read(config_file)
    except Exception as e:
        sg.popup(f'Exception {e}', 'No config file found... will create one for you', keep_on_top=True, background_color='red', text_color='white')
    return parser

def save_config(config_file,parser,values):
    if values:
        for k,v in conf_keys.items():
            try:
                if parser.has_section(v[0]):
                    if parser.has_option(v[0], k):
                        parser.set(v[0],k,values[v[2]])
            except Exception as e:
                print(f'Problem updating config from window values. Key = {k}')

    with open(config_file, 'w') as conf_file:
        parser.write(conf_file)
    
    sg.popup('Configuration saved!')

def create_parser(default):
    new_parser = configparser.ConfigParser()
    for section,keys in default.items():
        new_parser.add_section(section)
        for key in keys:
            new_parser.set(section,key,'')
    return new_parser    

############################################################    
#             Creating Configuration Window
############################################################

def create_conf_window(parser):
    sg.theme(parser.get('gui_settings','theme'))

    def TextLabel(text): return sg.Text(text+':', justification='r', size=(25,1))
    
    layout = [
        [sg.Text('Choose Configuration', font = 'Any 20', justification='c')],
        [sg.Text('')],
        [TextLabel('Output Directory'), sg.Input(key='-OUTDIR-'), sg.FolderBrowse(target='-OUTDIR-')],
        [TextLabel('FASTQ Files Directory'), sg.Input(key='-FASTQ-'), sg.FolderBrowse(target='-FASTQ-')],
        [TextLabel('Spectra Files Directory'), sg.Input(key='-SPECTRA-'), sg.FolderBrowse(target='-SPECTRA-')],
        [sg.Text('')],
        [TextLabel('Trinity'), sg.Input(key='-TRINITY-'), sg.FileBrowse(target='-TRINITY-')],
        [TextLabel('hg19'), sg.Input(key='-HG19-'), sg.FileBrowse(target='-HG19-')],
        [TextLabel('SearchGUI'), sg.Input(key='-SEARCHGUI-'), sg.FileBrowse(target='-SEARCHGUI-')],
        [TextLabel('PeptideShaker'), sg.Input(key='-PEPTIDE-'), sg.FileBrowse(target='-PEPTIDE-')],
        [TextLabel('ACTG'), sg.Input(key='-ACTG-'), sg.FolderBrowse(target='-ACTG-')],
        [sg.Text('')],
        [TextLabel('Transcriptome GTF'), sg.Input(key='-GTF-'), sg.FolderBrowse(target='-GTF-')],
        [TextLabel('Reference genome'), sg.Input(key='-REF-'), sg.FolderBrowse(target='-REF-')],
        [TextLabel('Mapping Method'), sg.Combo(['PV','PS','VO','SO'],key='-MAP-')],
        [TextLabel('Protein Database'), sg.Input(key='-DB-'), sg.FileBrowse(target='-DB-')],
        [TextLabel('Serialization File'), sg.Input(key='-SER-'), sg.FileBrowse(target='-SER-')],
        [sg.Text('')],
        [TextLabel('Bamstats'), sg.Input(key='-BAMSTATS-'), sg.FileBrowse(target='-BAMSTATS-')],
        [TextLabel('BAM Files'), sg.Input(key='-BAM-'), sg.FolderBrowse(target='-BAM-')],
        [TextLabel('BED File'), sg.Input(key='-BED-'), sg.FileBrowse(target='-BED-')],
        [sg.Text('')],
        [TextLabel('DeNoPro Location'), sg.Input(key='-DENOPRO-'), sg.FolderBrowse(target='-DENOPRO-')],
        [sg.Text('')],
        [TextLabel('Theme'), sg.Combo(sg.theme_list(), size=(17, 0.8), key='-THEME-')],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Button('Save'), 
            sg.InputText('', do_not_clear=False, visible=False, key='-filename-',enable_events=True),
            sg.FileSaveAs('Save As'),sg.Button('Exit')]
    ]

    window = sg.Window("Config", keep_on_top=True).Layout([[sg.Column(layout,size = (680,720),scrollable=True)]]).Finalize()

    for k,v in conf_keys.items():
        try:
            window[conf_keys[k][2]].update(value=parser.get(v[0],k))
        except Exception as e:
            print(f'Problem updating GUI window from config. Key = {k}')
    return window

############################################################    
#              Main Program and Event Loop 
############################################################
def main():
    sg.theme('SystemDefaultForReal')
    main_window = None

    command_to_run = 'denopro '
    layout = [
        [sg.Text('DeNoPro : de novo Proteogenomics Pipeline', justification='c', font=('Any',22))],
        
        [sg.Text('')],
        
        [sg.Text('Mode : ', size=(10,1), justification='r'), 
            sg.Combo(['assemble','searchdb','identify','novelorf', 'quantify'],key='mode'),
            sg.Text('CPU:', justification='r'), 
            sg.Input(key='cpu',font = 'Any 10', size=(5,0.8)), 
            sg.Text('Max mem:', size=(10,1), justification='r'), 
            sg.Input(key='max_mem', font = 'Any 10', size=(5,0.8))],
        
        [sg.Text('Config : ', size=(9,1), justification='r'), 
            sg.Input(key='-config-', enable_events=True),
            sg.FileBrowse('Select',target='-config-',size = (10,0.8),file_types=(('Config Files','*.conf'),('INI files','*.ini'))), 
            sg.Button('Change Configuration', size=(22,0.8))],
        
        [sg.Text('')],
        #output
        [sg.Text('Final Command:')], 
        
        [sg.Text(size=(90,3),key='command_line', text_color='red',font='Courier 8')],
        
        [sg.Output(size=(90,16), font='Courier 10', key='-ML-')],
        
        [sg.Button('Start', button_color=('white','green')), 
            sg.Button('Exit', button_color=('white','#8a2815'))]
    ]   

    main_window = sg.Window('DeNoGUI', layout, font = 'Helvetica 12', finalize=True)

    while True: 
        event,values = main_window.read()
        # define exit
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        # Config Loop
        if event == 'Change Configuration':
            # set the main config (if called)
            if values['-config-']:
                chosenConfig = values['-config-']
                parser = load_parser(chosenConfig)
                event,values = create_conf_window(parser).read(close=True)
                if event == 'Save':
                    save_config(chosenConfig,parser,values)
                elif event == '-filename-':
                    filename = values['-filename-']
                    save_config(filename,parser,values)
            else:
                sg.popup('No config file selected, will create one for you...')
                createdParser = create_parser(default_conf) 
                createdParser.set('gui_settings','theme','SystemDefaultForReal')
                event,values = create_conf_window(createdParser).read(close=True)
                if event == 'Save':
                    sg.popup('Please Save As a new file.')
                elif event == '-filename-':
                    filename = values['-filename-']
                    save_config(filename,createdParser,values)
        # Main Loop
        if event == 'Start':
            params = ''
            params += f"{values['mode']} -c {values['-config-']}" 
            if values['mode'] == 'assemble':
                params += f" --cpu {values['cpu']} --max_mem {values['max_mem']}G"
            command = command_to_run + params
            main_window['command_line'].update(command)
            runCommand(cmd = command, window=main_window)
        
    main_window.close()

if __name__ == '__main__':
    sg.theme('SystemDefaultForReal')
    main()