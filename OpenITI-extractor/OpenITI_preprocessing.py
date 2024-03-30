'''
Preprocessing File for Open ITI.
'''


import os
import glob



def read_out_directories_txt_data_list(path_input, file_extension):
    # Directories are saved in a list,
    # then the list is sorted in ascending order.

    txt_file_liste_ara1 = glob.glob(f'{path_input}/**/*{file_extension}', recursive=True)
    #txt_file_liste_ara2 = glob.glob(f'{path_input}/**/*ara2', recursive=True)
    #txt_file_liste_completed = glob.glob(f'{path_input}/**/*completed', recursive=True)
 
    txt_file_liste = txt_file_liste_ara1 #+ txt_file_liste_ara2 + txt_file_liste_completed

    # If the individual file names are to be displayed:
    #for file in txt_file_liste:
    #    basename = os.path.basename(file)
    #    print(basename)
  
    # list of files txt_file_liste
    return txt_file_liste


def add_files1(file_liste,new_path, name, file_extension, path_intermediate):
    # Function merges the files of the list file_list 
    # Applies the filter function

    from camel_tools.utils.normalize import normalize_alef_maksura_ar
    from camel_tools.utils.normalize import normalize_alef_ar
    from camel_tools.utils.normalize import normalize_teh_marbuta_ar
    from camel_tools.utils.dediac import dediac_ar
    from camel_tools.tokenizers.word import simple_word_tokenize
    from camel_tools.disambig.mle import MLEDisambiguator
    from camel_tools.tokenizers.morphological import MorphologicalTokenizer
    mle = MLEDisambiguator.pretrained('calima-msa-r13')
    import re
    import datetime


    # Timestamp for file
    datetime_str = datetime.datetime.now().strftime(format="%Y-%m-%d_%H-%M-%S")

    # adds files in one file. Datei_unbearbeitet.txt unprocessed file. 
    output_file = path_intermediate + "/" +name[:6]+ "_"+ datetime_str+ "_"+"Datei_X_raw.txt"
    #print(name)
    #print("Die Anzahl an Dateien beträgt: ", len(file_liste))
    #counter = 0
    '''
    for txt_file in file_liste:
        #print(counter)
        #counter += 1
        with open( txt_file, 'r') as content_file:
            content = content_file.read()
        with open(output_file, 'a') as target_device:
            target_device.write(content)
        target_device.close()
    
    print(name)
    print ("Add raw files done.")
    '''

    # starts filter 
    if len(file_liste) == 0:
        print("Es sind keine "+ file_extension +  " Dateien vorhanden.") 
    else:
        output_file = new_path+ "/"+name+"_"+"datei.txt"
        #print(output_file)
        #print(file_liste)

        splitter = "#META#Header#End#"
    
        print("Die Anzahl an Dateien beträgt: ", len(file_liste))

        counter = 0
        for txt_file in file_liste:
            #print(txt_file)
            #print(counter)
            counter += 1
            with open(txt_file, "r", encoding="utf8") as tempIn:
                mdText = tempIn.read()
                text = mdText.split(splitter)[1]
                text = re.sub("Pagew+", "", text) # remove page numbers
                text = re.sub("~~", " ", text) # aggregate paragraphs
                text = re.sub("# ", "", text) # add an empty line between paragraphs
                #text = re.sub("### (|+|$+) ?", "", text) # remove header tags
                text = re.sub("msd+", "", text) # remove milestone tags
                text = re.sub("%~%", "", text) # remove hemistich dividers
                text = re.sub(" +", " ", text) # remove excessive spaces
                content = re.sub("¶", " ", text) # remove ¶ 
                content = content.replace('\u060c',' \u060c ') # ،
                content = content.replace('\u061F', ' \u061F ') # ؟  U+061F
                content = content.replace('\u061b', ' \u061b ') # ؛
                content = content.replace('»',' » ')
                content = content.replace('«',' « ')
                content = content.replace('?',' ? ')
                content = content.replace('.',' . ')
                content = content.replace('(',' ( ')
                content = content.replace(')',' ) ')
                content = content.replace('[',' [ ')
                content = content.replace(']',' ] ')
                content = content.replace('{',' { ')
                content = content.replace('}',' } ')
                content = content.replace('"',' " ') 
                content = content.replace(',',' , ')
                content = content.replace('!', ' ! ')
    
                content = content.replace('§','')
                content = content.replace('#','')
                content = content.replace('%','')
                content = content.replace('$','')
                content = content.replace('&','')
                content = content.replace('/','')
                content = content.replace('*','')
                content = content.replace('_',' ')
                content = content.replace(':',' : ')

                content=re.sub("[A-Za-z]","",content) # remove latin letters
                #content=re.sub("[0-9]","",content) # remove numbers
                #text= content.translate(str.maketrans('', '', string.punctuation)) # remove any punctations
                text = normalize_alef_ar(content) # Normalize alef variants to 'ا'
                text = normalize_alef_maksura_ar(text) # Normalize alef maksura 'ى' to yeh 'ي'
                text = normalize_teh_marbuta_ar(text) # # Normalize teh marbuta 'ة' to heh 'ه'
                text = dediac_ar(text) # delete taskil

                diac_flag = 0 #diac() -> to Diacritization set  diac_flag = 1
                if diac_flag == 1:
                    new_lines = []
                    n_text = text.split("\n")
                    for i in n_text:
                        sentence = simple_word_tokenize(i)
                        tokenizer = MorphologicalTokenizer(mle, scheme='d1seg', split=False, diac=True) #['d2seg', 'd1seg', 'atbtok', 'd1tok', 'atbseg', 'd3seg', 'd2tok', 'd3tok', 'bwtok']
                        tokens = tokenizer.tokenize(sentence)
                        #print(tokens)
                        content = " ".join(tokens)
                        content = content.replace("_", "")
                        content = content.replace("+", "")
                        content = content.replace(" - ", "-")
                        content = content.replace("الل ه", "الله")
                        new_lines.append(content)
                        new_lines.append("\n")
                    text = "".join(new_lines)


            with open(output_file, "a", encoding="utf8") as tempOut:
                tempOut.write(text)
            tempOut.close()

        output_delet_empty_lines = new_path+ "/"+name+"_"+"without_space.txt"
        os.system(f"sed -e '/^[ ]*$/d' {output_file}> {output_delet_empty_lines}")
        os.remove(output_file)

    
        print ("Filter done.")
        return output_delet_empty_lines 



def satztrenner(text, zaehler):
    # sentence segmentation 

    # define max and min of sentence length
    max_len = 40
    min_len = 10 

    # satz is the list of words os text.
    satz = text.split()
    liste = []
    priority_punctations = ['.', '?', '؟', '!' ]

    for i in satz:
        a = i
        i = i+' '
        liste.append(i)

        # if a is one of subsequent characters: the following characters are not taken into account in the record length
        if a == '.' or a=='?' or a=='!' or a ==',' or a ==';' or a == ':' or a == '؟' or \
            a == '(' or a == ')' or a =='[' or a == ']' or a == '{' or i =='}' or a =='،' or\
               a == '"' or a =='»' or a =='«' or any(chr.isdigit() for chr in a) == True:
            zaehler += 0
        else:
            zaehler += 1 
        
        if a in priority_punctations and zaehler >= min_len:
            liste.append("\n")
            zaehler = 0
        elif a == ':' and zaehler >= min_len:
            liste.append("\n")
            zaehler = 0
        elif a == ';' and zaehler >= min_len:
            liste.append("\n")
            zaehler = 0
        elif a == ',' and zaehler >= min_len:
            liste.append("\n")
            zaehler = 0
        elif a == '،' and zaehler >= min_len:
            liste.append("\n")
            zaehler = 0
        elif zaehler == max_len:
            liste.append("\n")
            zaehler = 0
    if zaehler >= min_len:
        zaehler = 0
        liste.append("\n")
    ergbenis = ' '.join(liste)
    
    # returns ergebis, type(ergebnis) is string
    # returns zaehler for word number
    return ergbenis, zaehler  

def datei_einlesen(file):
    # Main function for sentence segmentation 
    from pathlib import Path
    import os

    file_path = os.path.splitext(file)[0]
    output_file = file_path + "_" + "Outputfile_1.txt"
    zaehler = 0

    with open( file, 'r') as content_file:
        content = content_file.readlines()
        #print(content)
        # content is list of lines of the file
        for i in content:
            # Empty lines are not taken into account
            if i == [] or i == '\n':
                continue
            else:
                i = i.strip()
                # sentence is passed to the sentence separator function: satztrenner(i, zaehler)
                content_new = satztrenner(i, zaehler)
                zaehler = content_new[1]
                with open(output_file, 'a+') as target_device:
                    # The sentence is written to the new file after the split
                    target_device.write(content_new[0])
                target_device.close()

    file_path = os.path.splitext(output_file)[0]
    output_delet_delete_blanks = file_path+ "__open_iti_sentenceSegmentation.txt"
    # Superfluous spaces are deleted
    content = Path(output_file).read_text().replace('  ',' ')
    with open(output_delet_delete_blanks, 'a') as target_device:
        target_device.write(content)
    target_device.close()
    os.remove(output_file)
    print ("Sentence Segmentation: Done.")

     # return output_delet_delete_blanks = file_path+ "__kasucca_sentenceSegmentation.txt"
    return output_delet_delete_blanks


def datei_split(input):
    import multiprocessing as mp    
    import os
    import math

    with open( input, 'r') as content_file:
        content = content_file.readlines()
    lines = len(content)

    # Numbers of Processors 
    n = mp.cpu_count()    
    print("Number of processors: ", n)

    # Create new data files for output after split
    file_path = os.path.splitext(input)[0]
    output_files = []
    for i in range(n):
        number = str(i)
        output = file_path + "_" + "file_split_"+number+".txt"
        output_files.append(output)
    #print(output_files)
    print("Create empty output files. Done.")

    # prepare lists / Sepearte input as list in n lists, depending of the processors.
    lenght_of_lists = math.ceil(lines/n) 
    print("lines per file without rest:", lenght_of_lists)
    output_liste=[content[i:i + lenght_of_lists] for i in range(0, lines, lenght_of_lists )]

    # print lists in the differnt outputfiles
    zaehler = 0
    for file in output_files:
        with open(file, 'w+') as file_output:
            for line in output_liste[zaehler]:
                file_output.write(line)
        zaehler += 1
    print("Output ready for sentence segmentation.")

    os.remove(input)

    return output_files


def parallelize_tasks(input, path_output_data, name):
    from pathlib import Path
    import os
    import threading
    import datetime

    threads = []
    # Starting all threads
    for i in input:
        print(i)
        t = threading.Thread(target=datei_einlesen, args=(i,))
        threads.append(t)
        t.daemon = False
        t.start()    
    # Waiting for all threads
    print("Sentence segmentation in progress.")
    for i in threads:
        i.join()

    # Timestamp for file
    datetime_str = datetime.datetime.now().strftime(format="%Y-%m-%d_%H-%M-%S")

    # After finishing threads, add all files to one outputfile
    output_file_end = path_output_data +"/"+name+"_"+ datetime_str + "_open_iti_preprocessing_endfile.txt"
    # input = list of files for file paths
    for i in input:
        file_path = os.path.splitext(i)[0]
        # outputfile paths of files (datei_einlesen())
        output_file = file_path + "_Outputfile_1__open_iti_sentenceSegmentation.txt"
        with open( output_file, 'r') as content_file:
            content = content_file.read()
        with open(output_file_end, 'a+') as target_device:
            target_device.write(content)
        os.remove(i)
        os.remove(output_file)
        target_device.close()
    print ("Add files Done. End. \n")

    return input


def verzeichnisse_einer_ebene(path):
    dirs = os.listdir( path )
    try:
        dirs.remove('.DS_Store')
    except:
        pass
    #print(dirs)
    return dirs

def verzeichnisse_uebergeben(path_input, file_extension, path_output_data, path_intermediate) :
    liste = verzeichnisse_einer_ebene(path_input) # List directories of one level

    zaehler = 1
    for verzeichnis in liste:
        name = verzeichnis+'_file_'
        #print("Verzeichnis Nr:", zaehler)
        new_path = path_input + "/" + verzeichnis
        list_directories = read_out_directories_txt_data_list(path_input + "/" + verzeichnis, file_extension)
        if list_directories != []:
            parallelize_tasks(datei_split(add_files1(list_directories,new_path, name, file_extension, path_intermediate)), path_output_data, name)
            zaehler += 1
        else:
            continue



def main():


    file_extension = 'ara1'

    #input files path
    path_input =  "INPUT-raw"

    # outputfiles path
    path_output_data = "OUTPUT"

    # input-intermediate path
    path_intermediate = "INPUT-Intermediate"


    #Automatic creation of the individual files
    # creates one for every directory: Datei_unbearbeitet.txt unprocessed file and one processed file with the name of the directoy + open_iti_preprocessing_endfile.txt
    verzeichnisse_uebergeben(path_input, file_extension, path_output_data, path_intermediate) 
    #add_files1(file_liste,new_path, name, file_extension, path_intermediate)

def diac():
    # 1 diacritization on
    # 2 diacritization off
    return 1 

if __name__ == "__main__":
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
