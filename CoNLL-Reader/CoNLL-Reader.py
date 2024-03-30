""".

...

"""

import os
from shutil import copy
import xml.etree.ElementTree as ET
import re
import datetime
import random
from rasmipy import rasmify
from camel_tools.tokenizers.word import simple_word_tokenize
from camel_tools.tokenizers.morphological import MorphologicalTokenizer
from camel_tools.disambig.mle import MLEDisambiguator
mle = MLEDisambiguator.pretrained('calima-msa-r13')

# import codecs
# import sys


def delete_lines(inputfile, outputfile):
    #Zeilen mit ' O' werden entfernt.
    os.system(f"sed '/^ O/d' {inputfile}>{outputfile}")

def main():
    """..."""

    print('Process started')

    list_of_files = []

    # Creates new folder for output's and
    datetime_str = datetime.datetime.now().strftime(format="%Y-%m-%d_%H-%M-%S")
    file_path_to_write = os.path.join(os.getcwd(), datetime_str)
    os.mkdir(file_path_to_write)

    # Copies python file to output-files. DOC.
    copy('CoNLL-Reader-4.py', os.path.join(file_path_to_write, 'CoNLL-Reader-4.py'))

    # Gets all xml files from input folder.
    files_to_convert = [f for f in os.listdir(os.path.join(os.getcwd(), 'input')) if f.endswith('.conll')]

    for file in files_to_convert:  # Processes all elements of the list.
        current_filename = file
        path = os.path.join(os.getcwd(), 'input', current_filename)

        # Opens the file and reads it:
        with open(path, mode='r', encoding='utf-8') as f:
            print(current_filename + ' started.')
            #file_as_string = f.read()
            
            # Diacritization
            file_as_string = f.readlines()
            new_lines = []
            for line in file_as_string:
                if ('\u0600' <= line <= '\u06FF' or '\u0750' <= line <= '\u077F' or '\u08A0' <= line <= '\u08FF' or '\uFB50' <= line <= '\uFDFF' or '\uFE70' <= line <= '\uFEFF' or '\U00010E60' <= line <= '\U00010E7F' or '\U0001EE00' <= line <= '\U0001EEFF'):
                    sentence = simple_word_tokenize(line)
                    tokenizer = MorphologicalTokenizer(mle, scheme='d1seg', split=False, diac=True)
                    tokens = tokenizer.tokenize(sentence)
                    #print(tokens)
                    content = " ".join(tokens)
                    #print(content)
                    content = content.replace("_", "")
                    content = content.replace("+", "")
                    content = content.replace(" - ", "-")
                    content = content.replace("الل ه", "الله")
                    new_lines.append(content)
                else:
                    line = line.replace("\n", "")
                    new_lines.append(line)
                    #print(line)
                #new_lines.append("\n")
            #for i in new_lines:
            #    print(i)
            new_lines_filter = []
            for i in new_lines:
                i = i.replace(" O", "##O")
                i = i.replace(" ", "")
                i = i.replace("##O" , " O")
                i = i.replace("B-" , " B-")
                i = i.replace("I-" , " I-")
                new_lines_filter.append(i)
                
            file_as_string = "\n".join(new_lines_filter)
            #print(file_as_string)
            




            # REGEX manuell auf INPUT-CoNLL-dateien angewandt um alle fehlerhaften zeilen mit nur einem element zu löschen
            # ^\s*[^\s]*\s*$
            
            # file_as_string = re.subn(r'\n\n(.+\n)*\s+[^\s]*\s*\n(.+\n)*\n', r'', file_as_string)[0] # Löscht fehlerhafte Sätze. <-- nicht angwandt

            # Splits CoNLL-files [[[word, tag],[word, tag],[word, tag],...],[sentence],...]
            file_as_list = file_as_string.split('\n\n')
            #print(file_as_list)

            '''
            # Diacritization
            for s in range(len(file_as_list)):
                i = file_as_list[s]
                content = simple_word_tokenize(i)
                tokenizer = MorphologicalTokenizer(mle, scheme='d1seg', split=False, diac=True)     # We can output diacritized tokens by setting `diac=True`
                content = tokenizer.tokenize(content)
                print(content)
                content_new = []
                for i in content:
                    #print(i)
                    if i == "\n":
                        continue 
                    content_new.append(i.strip())
                    if i == "O" or i == "ORG" or i == "PER" or i == "OTH" or i == "TME" or i == "LOC":
                        content_new.append("\n")
                #print(content_new)
                content = "\t".join(content_new)
                
                content = content.replace("_", "")
                content = content.replace("+", "")
                content = content.replace(" - ", "-")
                content = content.replace("الل ه", "الله")
                content = content.strip()

      
                file_as_list[s] = content
            '''
        
            
            #for s in range(len(file_as_list)):
             #   i = file_as_list[s]
              #  liste_i = i.split()
             
             #çç   print(liste_i)


                
            file_as_list = list(map(lambda y: list(map(lambda x: x.split(' '), y.split('\n'))), file_as_list))


            '''
            for s in range(len(file_as_list)):
                for w in range(len(file_as_list[s])):
                    ################################ Hier Funktionen zum Überarbeiten der Wörter eintragen
                    # file_as_list[s][w][0] = re.subn(r'[ًٌٍَُِّْ]', r'', file_as_list[s][w][0])[0] # Beispiel 1:  entfernt taškīl
                    # file_as_list[s][w][0] = re.subn(r'[إأآ]', r'ا', file_as_list[s][w][0])[0]  # Beispiel 2:  vereinheitlicht alifs
                    file_as_list[s][w][0] = rasmify(file_as_list[s][w][0])
            '''
                 

            for s in range(len(file_as_list)):
                for w in range(len(file_as_list[s])):
                    file_as_list[s][w] = ' '.join(file_as_list[s][w])
                file_as_list[s] = '\n'.join(file_as_list[s])
            new_string = '\n\n'.join(file_as_list)

            
            with open(os.path.join(file_path_to_write, current_filename), 'wb') as f_new:
                f_new.write(new_string.encode('utf-8'))

            print(current_filename + ' finished.')
            list_of_files.append(current_filename) 

    for txt_file in list_of_files:
        delete_lines(file_path_to_write+"/"+txt_file, file_path_to_write+"/1"+txt_file )
        new_name = file_path_to_write+"/"+txt_file
        os.rename(file_path_to_write+"/"+txt_file,'Output.txt')
        os.rename(file_path_to_write+"/1"+txt_file, new_name)
        os.remove('Output.txt')

    print('Process finished')


if __name__ == "__main__":
    main()
