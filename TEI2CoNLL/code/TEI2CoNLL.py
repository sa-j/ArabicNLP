


from email.quoprimime import quote
from pydoc_data.topics import topics
from dataclasses import replace
import os
from shutil import copy
from typing import Counter
from unicodedata import name
import xml.etree.ElementTree as ET
from pathlib import Path
import re
import datetime
import random
import collections
import functools
import operator
from bs4 import BeautifulSoup
from glob import glob
from requests import head
from sympy import O


def add_names_str(string):
    '''
    This function reads in a string and puts the NER tags into the Bio-form 
    (for the beginning of a tag: B-[NER], I-[NER] for the continuation of a tag
    and O if no tag is defined).  
    '''
    content_1 = string.strip()
    content = content_1.split("\n")

    start_nerName_flag = 0
    list_to_write = []
    first_word_b_flag = 0
    
    for i in content:
        new_line_liste =[]
        i = i.replace("\n", "")

        if "MATN" in i:
            continue

        elif "subt" in i:
            list_to_write.append(i+"\n")

        elif "NERname" in i:
            start_nerName_flag = 1
            first_word_b_flag = 1
            nerName_liste = i.split(":")
            del nerName_liste[0]
            nerNames = "-".join(nerName_liste)
            # Tags are replaced. 
            nerNames = nerNames.replace("person", "PER")
            nerNames = nerNames.replace("time", "TME")
            nerNames = nerNames.replace("organization", "ORG")
            nerNames = nerNames.replace("location", "LOC")
            nerNames = nerNames.replace("other", "OTH")
            continue
        elif start_nerName_flag == 1 and "end_Ner" not in i:
            if first_word_b_flag == 1:
                new_nerNames = "B-"+nerNames
                first_word_b_flag = 0
            else:
                new_nerNames = "I-"+nerNames
            new_line_liste.append(i)
            new_line_liste.append(new_nerNames)
            new_line = "\t".join(new_line_liste)
            new_line = new_line + "\n"
            list_to_write.append(new_line)
        elif "end_Ner" in i:
            first_word_b_flag = 0
            nerName_liste = []
            start_nerName_flag = 0
            continue
        else:
            if "topic" in i:
                list_to_write.append(i + "\n")
            elif i == "":
                list_to_write.append(i + "\n")
            else:
                new_line_liste.append(i)
                new_line_liste.append("O")
                new_line = "\t".join(new_line_liste)
                new_line = new_line + "\n"
                list_to_write.append(new_line)
    
    print("Bio-form NER Tags done!")
   
   # Returns list list_to_write
    return list_to_write


def nerNames(file, topic_flag, subtopic_flag, isnad_flag, subtopic_filter):
    '''
    This function reads in an .xml file. Then certain tags are be marked for 
    extractation. These tags are selectable via the various flags. 
    NERs are always extracted, Topics, Subtopics and Insnade can be flexibly 
    switched on and off. To mark tags, before and after them keywords are 
    inserted. 
    '''

    # It is tested whether the data is already available for processing or must
    # first be read out. 
    # First of all, the NER tags are extracted.  
  
    try:
        with open(file, 'r') as input_file:
            data = input_file.read()
        soup = BeautifulSoup(data, 'xml')

        persons = soup.find_all("name", {'role':'person'})
        for i in persons: 
            i.insert_before(" NERname:person ")
            i.insert_after(" end_Ner ")
        time = soup.find_all("name", {'role':'time'})
        for i in time:
            i.insert_before(" NERname:time ")
            i.insert_after(" end_Ner ")
        organizations = soup.find_all("name", {'role':'organization'})
        for i in organizations:
            i.insert_before(" NERname:organization ")
            i.insert_after(" end_Ner ")
        locations = soup.find_all("name", {'role':'location'})
        for i in locations:
            i.insert_before(" NERname:location ")
            i.insert_after(" end_Ner ")
        others = soup.find_all("name", {'role':'other'})
        for i in others:
            i.insert_before(" NERname:other ")
            i.insert_after(" end_Ner ")
    except:
        soup = BeautifulSoup(file, 'xml')

        persons = soup.find_all("name", {'role':'person'})
        for i in persons: 
            i.insert_before(" NERname:person ")
            i.insert_after(" end_Ner ")
        time = soup.find_all("name", {'role':'time'})
        for i in time:
            i.insert_before(" NERname:time ")
            i.insert_after(" end_Ner ")
        organizations = soup.find_all("name", {'role':'organization'})
        for i in organizations:
            i.insert_before(" NERname:organization ")
            i.insert_after(" end_Ner ")
        locations = soup.find_all("name", {'role':'location'})
        for i in locations:
            i.insert_before(" NERname:location ")
            i.insert_after(" end_Ner ")
        others = soup.find_all("name", {'role':'other'})
        for i in others:
            i.insert_before(" NERname:other ")
            i.insert_after(" end_Ner ")

    # All "note> <note" tags are deleted. Otherwise unwanted data will 
    # remain in the final output. 
        quote = soup.find_all("note")
        for i in quote:
            i.clear()

    # The "head" tag will be marked with "nil". Since he does not have any topic.
    head = soup.find_all("head")
    for i in head:
         i.insert_before("#topic:,nil ")

   # If subtopic_flag == 1, subtopics are extracted.
    zaeh = 0
    if subtopic_flag == 1:
        subtopics = soup.find_all("seg")
        new_subtopics = []
        for i in subtopics:
            if i.find_parents("seg"):
                continue
            else:
                try:
                    i["ana"]
                    a = i["ana"].split(" ")
                    if a[0] == "yes":
                        zaeh += 1
                        continue 
                    else:
                        new_subtopics.append(i)
                except:
                    continue
        #print(new_subtopics)
        for i in new_subtopics:       
            subtopic_attributs = i["ana"].split(" ")
            sub_att_new = subtopic_attributs[0].strip()
            try:
                if subtopic_attributs[1] == "mansukha":
                    sub_att_new = subtopic_attributs[0] + "_" + subtopic_attributs[1]
                    print(sub_att_new)
            except:
                pass
        
            # If the subtopics should be grouped into categories, 
            # subtopic_filter == 1 must be set. 
            if subtopic_filter == 1: 
                fiq = ["fiqhterm","fihqterm", "Kaffarah", "kaffarah", "swam", "adabqazi", "buyu", "miras", "halalharam", "hajj", "jihadsiyar", "jinayat", "khunsa", "nikah", "otheribadat", \
                    "salat", "sawm", "tahara", "usulfiqh", "zakat", "sadaqa", "talaq", "idda", "lian", "zihar", "hudud", "atimaashriba", "kaffara", \
                        "riba", "ijara", "qard", "shahada", "qisas", "yamin", "itq", "tabanni", "khul", "ila", "dayn", "milkiyat", "miras", "nizamhukumt", "nizamhukumat",\
                            "otheribadat", "waqf" ]
                
                kalam = ["afaalibad", "aqlnaql", "falasifa", "firaq", "imankufr","imankufur", "kalamterm", "khairshar", "mojizat", "mutakalimun", "nubuwaimama", "qazaqadr", "samiyat", "sawabiqab", "sifatilahi", "zatilahi"]

                lugha = ["sarfnahaw", "sarfnahw", "lughawi", "istilahi", "murad", "amthal", "lahajat", "tabeer", "lughaterm"]

                asbab = ["aplace", "akafiyah", "areason", "areaction", "aquestion", "anonquranic", "atime", "aevent", "apersongroup", "atopic", "aboff", "aaoff" ]

                naskh = ["nn78:30", "mm4:20", "mm4:8", "mm4:8",  "mm4:15", "nn58:3", "nn5:13", "nn5:90", "nn5:42", "nn5:49", "nn2:237", "nn2:286", "nn2:234",  "nn2:285", "nn2:282", "nn2:283", "nn2:235", "nn2:221", "nn2:229", "nn2:234", "nn24", "mm24:61", "mm9:39", "mm9:36+5", "mm9:5", "mm9:113", "mm8:34", "mm8:75", "mm5:106", "mm5:2", "mm5:49","mm33:49", "mm2:283", "mm2:221", "mm2:234", "mm2:154", "nn9:113", "nn9:5", "nn9:1", "nn4:33","nn47:4", "nn4:20",  "nn4:15", "nn4:11", "nn9:73","nn9:29", "nn2","mml5", "mm9", "nn8", "nn78","nn9", "nn2", "nn4", "mm33", "mm4", "nn59", "nn8", "Nn78", "nn78", "mm24", "mm9", "nn5", "Mm5", "mm5", "nn24", "nn24:32","mm8", "Mm2", "mm2", "nn", "nn11", "nn11:11", "nnq", "nna", "nns", "nnk", "nnl", "nnw", "nn(11:11)", "nn(+11:11)", "ayah_mansukha", "ayah",\
                     "mm", "mm8", "nn4", "mm9", "nn2", "nn22", "mmk", "nn4", "mm8", "mm5", "mm11", "mm11:11", "mmq", "mma", "mms", "mml", "mmw", "mm(11:11)", "mm(+11:11)"]
                # "ayah" in naskh für Ayah Mansukha

                qiraat = ["Qrasmchange", "harakat", "otherqurra", "qlazim", "qrasmchange", "ibdal", "qahabaswab", "qahabsawab", "qamsar", "qari", "qbasra", "qghairjaiz", "qjaiz", \
                    "qhijaz", "qiraq", "qtherqurra", "qkufa", "qmakkah", "qmadina","qsham", "sarfi", "sawti", "taqdemtakheer", "zikrhazf", "taqdeemtakheer"]
                
                science = ["kwan", "scienceterm", "sceinceterm", "scieneceterm",  "arz", "haiwan", "insan", "kawn", "mojiza", "nujum", "qamar", "shams", "tib"]

                sirah = [ "lrajeh", "rajeh", "sirahterm", "karajeh", "srajeh", "krajeh", "irajeh", "Shijra", "shijra", "sbadar", "sjahilya", "swilada", "snubuwwa", "shijrah", "sbadr", "suhad", "skhandaq", "shudaibia",\
                     "sfathmakkah", "sgazwat", "sghazawat", "swafat", "sevent", "smakkah", "smakki", "smadani", "skhilafa", "sother", "smojiza", "szaati"]
                
                sufism = ["dua", "asbaq" , "adab", "fazail", "razail", "riqaq", "asghalamal","ashghalamal", "targhibtarhib", "awliya", "hub", "sufiterm"]

                #tareekh = ["abbasid", "khilafaabukakr", "khilafaali", "khilafaumar", "khilafauthman", "umayyad", "khawarij", "ahlkitab", "jahiliyah", "majusiya", "mushrikin", "nasraniya", "prejahiliya", "sabiun", "yahudiya"]

                #adyan = ["jahiliyah", "jahiliya", "adyanterm", "prejahiliya", "mushrikin", "ahlkitab", "kutub", "sabiun", "majusiya", "yahudiya", "yahudia",\
                #     "nasraniya", "adyanperson", "adyangroup", "adterm"]

                #other = [ "qlazim", "manqul" ]

                adyan = ["ktub", "jahiliyah", "jahiliya", "adyanterm", "prejahiliya", "mushrikin", "ahlkitab", "kutub", "sabiun", "majusiya", "yahudiya", "yahudia","abbasid", "khilafaabukakr", "khilafaali", "khilafaumar", "khilafauthman", "umayyad", "khawarij", "ahlkitab", "jahiliyah", "majusiya", "mushrikin", "nasraniya", "prejahiliya", "sabiun", "yahudiya",\
                     "nasraniya", "adyanperson", "adyangroup", "adterm"]

                # israeliyat -> stands on its own.

                if sub_att_new in fiq:
                    sub_att_new = "fiqh"
                elif sub_att_new in kalam:
                    sub_att_new = "kalam"
                elif sub_att_new in lugha:
                    sub_att_new = "lugha"
                elif sub_att_new in asbab:
                    sub_att_new = "asbab"
                elif sub_att_new in naskh:
                     sub_att_new = "naskh"
                elif sub_att_new in qiraat:
                     sub_att_new = "qiraat"
                elif sub_att_new in science:
                     sub_att_new = "science"
                elif sub_att_new in sirah:
                     sub_att_new = "sirah"
                elif sub_att_new in sufism:
                     sub_att_new = "sufism"
                #elif sub_att_new in tareekh:
                #     sub_att_new = "tareekh"
                elif sub_att_new in adyan:
                     sub_att_new = "adyan"
                #elif sub_att_new in other:
                #    sub_att_new = "other"

            start_tag = " subtopic:"+sub_att_new+" "
            i.insert_after( " end_subt ")
            i.insert_before( start_tag)

    
    # persName tags that occur mainly in Isnads, are included as PER.
    isnad_pers = soup.find_all("persName")
    for i in isnad_pers:
        i.insert_before(" NERname:person ")
        i.insert_after(" end_Ner ")
  
    # The Isnad is followed by the MATN. MATN is marked by the tag <said> in the
    # .xml file 
    if isnad_flag == 1:
        isnad_end = soup.find_all("said")
        for i in isnad_end:
            i.insert_before(" MATN ")           
    text = str(soup)
        
    # If topic_flag == 1 the topics of the paragraphs are extracted and written
    # in front of the paragraph in the file. This is done by the function 
    # parse_paragraph_ana_tags(text).
    if topic_flag == 1:
        text = parse_paragraph_ana_tags(text)
    
    soup = BeautifulSoup(text, "xml")
    soup = str(soup.get_text())
    soup = soup.replace('\t', '')
    soup = soup.replace('\n', ' ')
    soup = re.sub('\s+',' ',soup)
    soup = soup.strip()

    soup_new = soup.split(" ")    
  
    # The output is needed for the Isnad deletion as type() -> list.
    nerNames_output_list = []
    for element in soup_new:
        if "#topic" in element:
            new_element = element.split(",")
            del new_element[0]
            new_topic_element = ", ".join(new_element)
            new_topic_element = "# topic: "+ new_topic_element
            element = new_topic_element

            test_str = element.replace(" ", "")
            test_str = test_str.replace(",", "")
            test_str = test_str.replace(":", "")
            test_str = test_str.replace("#", "")
            if test_str.isalpha():                
                pass
            else:
                new_element = ""
                zaehler = 0
                for i in element:
                    if i.isalpha() or i == " " or i == "," or i == ":" or i == "#":
                        new_element = new_element + i
                    else:
                        new_element = new_element + "\n" + element[zaehler:]
                        element = new_element
                        break
                    zaehler += 1
            if "# topic" in element:
                element =  "\n" + element
        nerNames_output_list.append(element)
        nerNames_output_list.append("\n")

    # If isnad_flag == 1 the isnad will be deleted.
    if isnad_flag == 1:
        new_nerNames_output_liste_reverse = []
        new_nerNames_liste = nerNames_output_list[::-1]
        delet_flag = 0
        delete_empty_line_flag = 0
        for i in new_nerNames_liste:
            if i == "SANAD":
                delet_flag = 0
                delete_empty_line_flag = 1

            elif delet_flag == 1 or delete_empty_line_flag == 1:
                delete_empty_line_flag = 0
                continue

            elif i =="MATN":
                delet_flag = 1
                delete_empty_line_flag = 1
            else:
                new_nerNames_output_liste_reverse.append(i)
        new_nerNames_output_liste = new_nerNames_output_liste_reverse[::-1] 
        # Deleting incorrect tags eg.: pb ed="GK" edRef="59434" n="4675"/>.
        output_delete_char = []
        for i in new_nerNames_output_liste:
            a = i.lower()
            if "NER" in i or "topic" in i or "end" in i or "subt" in i or "name" in i:
                output_delete_char.append(i)
            elif a.islower():
                continue
            else:
                output_delete_char.append(i)
        new_nerNames_output_str = "".join(output_delete_char)
        nerNames_output_str = new_nerNames_output_str
    # If the Isnad is not to be deleted, only the word "SANAD" and 
    # incorrect tags will be deleted.
    else: 
        ner_outp = []
        delete_empty_line_flag = 0
        for i in nerNames_output_list:
            if i == "SANAD":
                delete_empty_line_flag = 1
                continue
            elif delete_empty_line_flag == 1:
                delete_empty_line_flag = 0
                continue
            else:
                ner_outp.append(i) 
        # Deleting incorrect tags eg.: pb ed="GK" edRef="59434" n="4675"/>.
        output_delete_char = []
        for i in ner_outp:
            a = i.lower()
            if "NER" in i or "topic" in i or "end" in i or "subt" in i or "name" in i:
                output_delete_char.append(i)
            elif a.islower():
                continue
            else:
                output_delete_char.append(i)
        nerNames_output_str = "".join(output_delete_char)
      
    print('nerNames done!')
    return nerNames_output_str
    

def join_files(path, isnad_flag):
    from natsort import natsorted
    '''
    This function reads in all .xml files in the defined input folder and merges 
    them into a single .xml file.
    '''

    result = glob(path+'/**/*.xml', recursive=True)
    result_liste_data = []
    for i in result:
        basename = os.path.basename(i)
        result_liste_data.append(basename)
    sorted_results = natsorted(result_liste_data, key=lambda x:(x[0].isdigit(), x))
    print(sorted_results)
    liste_lines = []
    liste_lines.append('<?xml version="1.0" encoding="UTF-8"?>\n<TEI xmlns=\
        "http://www.tei-c.org/ns/1.0">\n\t<teiHeader>\n\t\t<fileDesc>\n\t\t\t\
            <titleStmt>\n\t\t\t\t<title></title>\n\t\t\t</titleStmt>\n\t\t\t\
                <publicationStmt>\n\t\t\t\t<p></p>\n\t\t\t</publicationStmt>\
                    \n\t\t\t<sourceDesc>\n\t\t\t\t<p></p>\n\t\t\t</sourceDesc>\
                    \n\t\t</fileDesc>\n\t</teiHeader>\n<text xml:lang="ar">\n<body>\n') 
    for i in result:
        with open(i, 'r') as f: 
            data = f.readlines()
            for line in data:
                if '<?xml version="1.0" encoding="UTF-8"?><TEI xmlns=\
                    "http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc><titleStmt>\
                        <title>test</title></titleStmt><publicationStmt><p>test</p>\
                            </publicationStmt><sourceDesc><p>test</p></sourceDesc>\
                                </fileDesc></teiHeader><text xml:lang="ar">\
                                    <body>' in line and "div" in line:
                    liste_lines.append("<div>")
                    continue
                elif 'xmlns="http://www.tei-c.org/ns/1.0" ana="' in line:
                    continue
                elif '<?xml version="1.0" encoding="UTF-8"?>' in line or\
                    '<TEI xmlns="http://www.tei-c.org/ns/1.0">' in line or\
                        '<teiHeader>' in line or '<fileDesc>' in line or\
                            '<sourceDesc>' in line or ' <titleStmt>' in line or\
                                 '<title>test</title>' in line or\
                                     '<publicationStmt>' in line or\
                                         '<p>test</p>' in line or\
                                             '</sourceDesc>' in line or\
                                                 '</fileDesc>' in line or\
                                                     '</teiHeader>' in line or\
                                                         '</publicationStmt>' in line or\
                                                             '</titleStmt>' in line or\
                                                                 '<titleStmt>'  in line or\
                                                                     '<text xml:lang="ar">' in line or\
                                                                         '<body>' in line or\
                                                                             '</body>' in line or\
                                                                                 '</text>' in line or\
                                                                                     '</TEI>' in line:
                    continue
                else:
                    liste_lines.append(line)
    liste_lines.append('</body>\n</text>\n</TEI>')
    str_lines = "".join(liste_lines)

    str_lines = re.subn(r'<note>.*</note>', r'', str_lines)[0]
    str_lines = re.subn(r'/\d+', r'', str_lines)[0]
    
    print("Join files done!")

    # This function returns the entire files in a string. 
    return str_lines


def satztrenner(text, zaehler):
    # Sentence segmentation. 
    # Input: type(text) -> list

    # Sentence length:
    max_len = 40
    min_len = 10

    # Each stentence in one list.
    list_of_sentences = []
    sentence = []
    counter_ceck = 0
    
   
    if "\n" in text:
        for element in text:
            sentence.append(element)
            if element == "\n":
                list_of_sentences.append(sentence)
                sentence = []
    else:
        list_of_sentences = [text]
    
    segmentation_sentence_list = []

    # Each sentence is considered separately and, if it contains more words 
    # than the max. number of words, it is separated.
    for sentence in list_of_sentences:
        liste = []
        liste_same_ner_tags_in_row = []
        zaehler_2 = 0
        previous_element = ""
        element_number = 0
        for i in sentence:

            if "end" in i:
                liste.append(i)
                continue
            
            element_number += 1

            try:
                next_element = sentence[element_number+1]
            except:
                pass
            a = i
            
            # Characters that are not counted for sentence length.
            if '.' in a or '?' in a or '!' in a or ',' in a or ';' in a or ':' in a\
                or '؟' in a or '(' in a  or ')' in a or '[' in a or ']' in a\
                    or '{' in a or '}' in a or '،' in a or '"' in a or '»' in a\
                        or '«' in a or 'topic' in a or 'end' in a\
                            or any(chr.isdigit() for chr in a) == True:
                    zaehler += 0
            else:
                zaehler += 1 
   
            # If NERs occur in the sentences, the sentence should be separated 
            # in such a way, that the NER tags are not separated.
            if "LOC" in a and "LOC" in previous_element or "PER" in a\
                and "PER" in previous_element or "ORG" in a and "ORG" in previous_element\
                    or "OTH" in a and "OTH" in previous_element or "TME" in a\
                        and "TME" in previous_element:
                                    liste_same_ner_tags_in_row.append(i)
                                    zaehler_2 += 1
                                    zaehler -= 1 
                                    previous_element = a
                                    continue
            elif "LOC" in a and "LOC" in next_element or "PER" in a\
                and "PER" in next_element or "ORG" in a and "ORG" in next_element\
                    or "OTH" in a and "OTH" in next_element or "TME" in a\
                        and "TME" in next_element:
                                        liste_same_ner_tags_in_row.append(i)
                                        zaehler_2 += 1
                                        zaehler -= 1 #
                                        previous_element = a
                                        continue 
            # Sentence separation:  
            elif zaehler + zaehler_2 >= max_len:
                if zaehler >= min_len:
                    liste.append("\n")
                    zaehler = 0
                    for word in liste_same_ner_tags_in_row:
                        liste.append(word)
                        zaehler += 1
                    liste.append(i)
                    liste_same_ner_tags_in_row = []
                    zaehler_2 = 0
                elif zaehler <= min_len:
                    for word in liste_same_ner_tags_in_row:
                        liste.append(word)
                        zaehler += 1              
                    liste.append("\n")
                    liste.append(i)
                    liste_same_ner_tags_in_row = []
                    zaehler = 1
                    zaehler_2 = 0  
    
            # Separation options for word count of sentence < max and > min. 
            # Separate at existing punctuation if possible. 
            # Punctuation is hierarchically ordered. The hierarchy is reflected
            # in the algorithm from "." -> '،'.
            elif zaehler + zaehler_2 < max_len:
                for word in liste_same_ner_tags_in_row:
                    liste.append(word)
                    zaehler += 1
                if '.' in a and zaehler >= min_len:
                    liste.append(i)
                    liste.append("\n")
                    zaehler = 0
                elif '?' in a and zaehler >= min_len:
                    liste.append(i)
                    liste.append("\n")
                    zaehler = 0
                elif '؟' in a and zaehler >= min_len:
                    liste.append(i)
                    liste.append("\n")
                    zaehler = 0
                elif '!' in a and zaehler >= min_len:
                    liste.append(i)
                    liste.append("\n")
                    zaehler = 0
                elif ':' in a and zaehler >= min_len:
                    liste.append(i)
                    liste.append("\n")
                    zaehler = 0
                elif ';' in a and zaehler >= min_len:
                    liste.append(i)
                    liste.append("\n")
                    zaehler = 0
                elif ',' in a and zaehler >= min_len:
                    liste.append(i)
                    liste.append("\n")
                    zaehler = 0
                elif '،' in a and zaehler >= min_len:
                    liste.append(i)
                    liste.append("\n")
                    zaehler = 0
                else:
                    liste.append(i)
                    
                liste_same_ner_tags_in_row = []
                zaehler_2 = 0    
                          
            elif '.' in a and zaehler >= min_len:
                liste.append(i)
                liste.append("\n")
                zaehler = 0
            elif '?' in a and zaehler >= min_len:
                liste.append(i)
                liste.append("\n")
                zaehler = 0
            elif '؟' in a and zaehler >= min_len:
                liste.append(i)
                liste.append("\n")
                zaehler = 0
            elif '!' in a and zaehler >= min_len:
                liste.append(i)
                liste.append("\n")
                zaehler = 0
            elif ':' in a and zaehler >= min_len:
                liste.append(i)
                liste.append("\n")
                zaehler = 0
            elif ';' in a and zaehler >= min_len:
                liste.append(i)
                liste.append("\n")
                zaehler = 0
            elif ',' in a and zaehler >= min_len:
                liste.append(i)
                liste.append("\n")
                zaehler = 0
            elif '،' in a and zaehler >= min_len:
                liste.append(i)
                liste.append("\n")
                zaehler = 0
            elif zaehler == max_len:
                liste.append(i)
                liste.append("\n")
                zaehler = 0
            elif zaehler > max_len:
                liste.append("\n")
                liste.append(i)
                zaehler = 0
            else:
                liste.append(i)

            previous_element = a
        flag = True
        
        if len(liste) <= max_len and "\n" in liste:
            counter_ceck += 1
            while flag == True:
                if "\n" in liste:
                    liste.remove("\n")
                else:
                    liste.append("\n")
                    flag = False
            
        segmentation_sentence_list = segmentation_sentence_list + liste
    
    # List of lists of separated sentences is returned.
    return segmentation_sentence_list  


def segmentation_of_sentences(data):
    ''' Function passes on data for sentence segmentation. '''

    #type(data) - > list
    content_new = satztrenner(data, 0)
    
    print("Sentence segmentation done!")
    return content_new # retruns list


def parse_paragraph_ana_tags(xml_file_as_string: str):
    '''
    This function parses the XML file for all paragraphs that have the attribute
    "ana" defined and returns the attributes as #topic:, attributs SANAD . 
    Afterwards the data will be inserted in the file.

    Args:
        xml_file_as_string (str): XML Datei as string.

    Returns:
        str: XML file as string, with inserted data.
    '''
    ET.register_namespace("", "http://www.tei-c.org/ns/1.0")
    xml_root = ET.fromstring(xml_file_as_string)
    ns = xml_root.tag
    ns = ns[:ns.rfind('}') + 1]
    ana_tags_statistics = dict()
    # text/body/div/p/ana
    for paragraph_node in xml_root.find(ns+"text").find(ns+"body").iter(ns+"p"):
        #for div_node in paragraph_node.findall(ns+"p"):
        paragraph_ana_attrib = paragraph_node.get("ana")
        if paragraph_ana_attrib == None:
            paragraph_ana_attrib = "nil yes"
        if paragraph_ana_attrib is not None:
            paragraph_ana_attrib = paragraph_ana_attrib[:paragraph_ana_attrib.rfind(
                " yes")+1].strip()
            if paragraph_ana_attrib != "":
                ana_attributes = paragraph_ana_attrib.split(" ")
                for ana_attribute in ana_attributes:
                    if ana_attribute in ana_tags_statistics:
                        topic_count = ana_tags_statistics[ana_attribute]
                        topic_count += 1
                        ana_tags_statistics[ana_attribute] = topic_count
                    else:
                        ana_tags_statistics[ana_attribute] = 1
                ana_text = "#topic:," + ",".join(ana_attributes) + " SANAD "
                paragraph_node.text = ana_text + \
                    (paragraph_node.text if paragraph_node.text is not None else "")
        else:
            paragraph_node.text = "#topic:" + \
            (paragraph_node.text if paragraph_node.text is not None else "")

    return ET.tostring(xml_root, encoding='unicode')


def insert_topic(liste):
    ''' 
    Function adds topic to the pararaph, if it is missing.
    If a pararaph does not have a topic it gets the attribut "nil".
    '''          
    input_data = liste
    output_data = []
    counter = 0
    liste_topic =[]
    flag = 0
    flag_2 = 0
    content = input_data
    if "# topic:" not in content[0] and content[0] != '\n' :
            output_data.append("# topic: nil\n")
    for line in content:
        if flag ==1 and line == "\n":
            continue    
        if flag == 1 and liste_topic != [] and "# topic:" not in line and line != '\n':
            output_data.append(liste_topic[0])
        if "# topic:" in line:
            if liste_topic != []:
                liste_topic.pop()
            liste_topic.append(line)
        if line == "\n":
            flag = 1
        if line != "\n":
            flag = 0
        output_data.append(line)
    print("Insert Topic done!")
    return output_data

def delete_topic_nosentence(liste):
    ''' Function deletes topic tags, with no following sentences. '''

    output_liste = []
    output_liste_end = []
    zaehler = 0
    for i in liste:
        try:
            next_element = liste[zaehler+1]
        except:
            next_element = ""
        zaehler += 1
        if "# topic:" in i and next_element == "\n":
            continue
        else:
            output_liste.append(i)
    for i in output_liste:
        try:
            next_element = output_liste[zaehler+1]
        except:
            pass
        if "\n" in i and next_element == "\n":
            continue
        else:
            output_liste_end.append(i)
    print("Delete topic without sentence done!")
    return output_liste_end


def bio_form_subtopics_str(liste):
    ''' 
    The function puts the subtopics in the text into the Bio-form. 
    B-[Subtopic] for the start of a subtopic.
    I-[Subtopic] for the continuation of a subtopic.
    O if no subtopic is defined.
    '''
    content = liste       
    previous_element = ""
    next_element = ""
    element_number = 0
    start_subtopic_flag = 0
    list_to_write = []
    liste_output = []

    for i in content:
        
        new_line_liste =[]
        i = i.replace("\n", "")

        if "subtopic" in i:
            start_subtopic_flag = 1
            i = i.replace(",", ":")
            suptopic_liste = i.split(":")
            del suptopic_liste[0]
            suptopics = suptopic_liste[0]
            continue
        elif i == "":
            list_to_write.append("\n") 
        elif "# topic:" in i:
            new = i+"\n"
            list_to_write.append(new)
        elif start_subtopic_flag == 1 and "end_subt" not in i:
            new_line_liste = i.split("\t")
            new_line_liste.append(suptopics)
            new_line = "\t".join(new_line_liste)
            new_line = new_line + "\n"
            list_to_write.append(new_line)
        elif "end_subt" in i:
            i = i.replace("end_subt", "")
            new_line_liste = i.split("\t")
            new_line_liste.append(suptopics)
            new_line = "\t".join(new_line_liste)
            new_line = new_line + "\n"
            if new_line_liste[0] != "":
                list_to_write.append(new_line)
            suptopic_liste = []
            start_subtopic_flag = 0
        else:
            if i == "":
                list_to_write.append("\n")
            elif "# topic:" in i:
                i = i + "\n"
                list_to_write.append(i)
            else:
                new_line_liste = i.split("\t")
                new_line_liste.append("O")
                if len(new_line_liste) <= 2:
                    while len(new_line_liste) < 3:
                        new_line_liste.append("O")
                new_line = "\t".join(new_line_liste)
                new_line = new_line + "\n"
                list_to_write.append(new_line)

    continue_flag = 0
    element_number = 0
    for i in list_to_write:
        liste_line = i.split("\t")
        if len(liste_line) == 2 and liste_line[0] != "":
            liste_line.insert(1, "O")
            i = "\t".join(liste_line)
        try:
            subtopic =  liste_line[2]
        except:
            subtopic = ""
            continue_flag = 1
            
        try:
            previous_element = list_to_write[element_number-1]
        except:
            pass
        try:
            next_element = list_to_write[element_number+1]
        except:
            pass
        element_number += 1

        new_line_liste =[]

        if subtopic in i and "# topic:" in previous_element and\
        subtopic != "O\n" and continue_flag == 0:
            new_line_liste = i.split("\t")
            del new_line_liste[2]
            new_line_liste.append("B-"+ subtopic)
            new_line = "\t".join(new_line_liste)
            liste_output.append(new_line)
        elif subtopic in i and subtopic not in previous_element and\
            subtopic not in next_element and subtopic != "O\n" and\
                continue_flag == 0:
            new_line_liste = i.split("\t")
            del new_line_liste[2]
            new_line_liste.append("B-"+ subtopic)
            new_line = "\t".join(new_line_liste)
            liste_output.append(new_line)
        elif subtopic in i and subtopic not in previous_element and\
            subtopic in next_element and subtopic != "O\n" and continue_flag == 0:
            new_line_liste = i.split("\t")
            del new_line_liste[2]
            new_line_liste.append("B-"+ subtopic )
            new_line = "\t".join(new_line_liste)
            liste_output.append(new_line)
        elif subtopic in i and subtopic in previous_element and\
            subtopic in next_element and subtopic != "O\n" and continue_flag == 0:
            new_line_liste = i.split("\t")
            del new_line_liste[2]
            new_line_liste.append("I-"+ subtopic)
            new_line = "\t".join(new_line_liste)
            liste_output.append(new_line)
        elif subtopic in i and subtopic in previous_element and\
            subtopic not in next_element and subtopic != "O\n" and\
                continue_flag == 0:
            new_line_liste = i.split("\t")
            del new_line_liste[2]
            new_line_liste.append("I-"+ subtopic )
            new_line = "\t".join(new_line_liste)
            liste_output.append(new_line)       
        else:
            liste_output.append(i)
            continue_flag = 0
    print("Bio form subtopics done!")
    # The data is returned as type() -> list.
    return liste_output

def delete_sentence_without_ner(liste):
    ''' Function deletes sentences without NER tags. '''
    sentences = []
    sentences_new = []
    sentence = []
    liste_output = []
    
    content = liste
    for i in content:
        sentence.append(i)
        if i == "\n":
            sentences.append(sentence)
            sentence = []
    for sen in sentences:
        sentence = "".join(sen)
        # If you also want to consider sentences that have a subtopic but no 
        # NER tags, then change if to:
        # if "I" in sentence or "B" in sentence
        if "PER" in sentence or "LOC" in sentence or "ORG" in sentence or\
            "TME" in sentence or "OTH" in sentence:
            sentences_new.append(sen)
        else:
            continue
    for sentence in sentences_new:
        liste_output = liste_output + sentence
    print("Delete sentence without ner done!")

    # The return of the data is in the form of a list.
    return liste_output

def write_output_to_three_files(liste, path_output):
    ''' 
    Function splits liste in 3 files: "train_LOT.conll", "dev_LOT.conll",
     "test_LOT.conll"
    ''' 
     
    counter = 0
    content = liste
    sentences = []
    sentence = []
    flag = 0
    counter_for_seg = 0
    outputfiles_liste = []
    for line in content:
        if "# topic" in line or flag == 1:
            sentence.append(line)
            flag = 1
            if "# topic" in line:
                counter_for_seg += 1
        if  line == "\n":
            flag = 0
            sentences.append(sentence)
            sentence = []   

    # If the records are to be sorted randomly, the following must be activated:         
    #random.shuffle(sentences)  # Shuffles the list.

    print("Number of blocks: ", counter_for_seg)
    train_LOT_1 = sentences[:int(counter_for_seg*0.8)]
    dev_LOT_1 = sentences[int(counter_for_seg*0.8):int(counter_for_seg*0.9)]
    test_LOT_1 = sentences[int(counter_for_seg*0.9):]

    train_LOT = []
    dev_LOT = []
    test_LOT = []
    new_lists = [train_LOT, dev_LOT, test_LOT]
    counter = 0
    for i in [train_LOT_1, dev_LOT_1, test_LOT_1]:
        for liste in i:
            new_lists[counter] += liste
        counter += 1
        
    file_names = ["train_LOT_1.conll", "dev_LOT_1.conll", "test_LOT_1.conll"]
    counter = 0
    for i in [train_LOT, dev_LOT, test_LOT]:
        file_output = path_output+ "/" + file_names[counter]
        with open( file_output, 'w') as target_device:
            for sentence in i:
                sentence = sentence
                target_device.write(sentence) 
        target_device.close()
        outputfiles_liste.append(file_output)
        counter += 1
    print("Splitting data to 3 files done!")

    # Function returns ["train_LOT_1.conll", "dev_LOT_1.conll", "test_LOT_1.conll"].
    return  outputfiles_liste


def replace_topic_style(liste):
    ''' Function relpaces old topics with new topics. '''
    file_names = liste
    output_files = ["train_LOT.conll", "dev_LOT.conll", "test_LOT.conll"]
    counter = 0 
    for file in file_names:
        input_file = file
        output = file_path_to_write + "/" + output_files[counter]
        with open( input_file, 'r') as content_file:
            content = content_file.readlines()
            with open( output, 'w') as target_device:
                for line in content:
                    adyan = 0
                    asbab = 0
                    fiqh = 0
                    kalam = 0
                    lugha = 0
                    mushkilat = 0
                    mutashabih = 0
                    naskh = 0
                    qiraat = 0
                    science = 0
                    sirah = 0
                    sufism = 0
                    takhsis = 0
                    tikrar = 0
                    israeliyat = 0  

                    if "nil" in line:
                        target_device.write("# adyan: " + str(adyan) + "\n")
                        target_device.write("# asbab: " + str(asbab) + "\n")
                        target_device.write("# fiqh: " + str(fiqh) + "\n")
                        target_device.write("# kalam: " + str(kalam) + "\n")
                        target_device.write("# lugha: " + str(lugha) + "\n")
                        target_device.write("# mushkilat: " + str(mushkilat) + "\n")
                        target_device.write("# mutashabih: " + str(mutashabih) + "\n")
                        target_device.write("# naskh: " + str(naskh) + "\n")
                        target_device.write("# qiraat: " + str(qiraat) + "\n")
                        target_device.write("# science: " + str(science) + "\n")
                        target_device.write("# sirah: " + str(sirah) + "\n")
                        target_device.write("# sufism: " + str(sufism) + "\n")
                        target_device.write("# takhsis: " + str(takhsis) + "\n")
                        target_device.write("# tikrar: " + str(tikrar) + "\n")
                        target_device.write("# israeliyat: " + str(israeliyat) + "\n")
                        #target_device.write("# other: " + "0" + "\n")

                    elif "topic" in line:
                        if "adyan" in line:
                            adyan = 1
                        if "asbab" in line:
                            asbab = 1
                        if "fiqh" in line:
                            fiqh = 1
                        if "kalam" in line:
                            kalam = 1
                        if "lugha" in line:
                            lugha = 1
                        if "mushkilat" in line:
                            mushkilat = 1
                        if "mutashabih" in line:
                            mutashabih = 1
                        if "naskh" in line:
                            naskh = 1
                        if "qiraat" in line:
                            qiraat = 1
                        if "science" in line:
                            science = 1
                        if "sirah" in line: 
                            sirah = 1
                        if "sufism" in line:
                            sufism = 1
                        if "takhsis" in line:
                            takhsis = 1
                        if "tikrar" in line:
                            tikrar = 1
                        if "israeliyat" in line:
                            israeliyat = 1
                        target_device.write("# adyan: " + str(adyan) + "\n")
                        target_device.write("# asbab: " + str(asbab) + "\n")
                        target_device.write("# fiqh: " + str(fiqh) + "\n")
                        target_device.write("# kalam: " + str(kalam) + "\n")
                        target_device.write("# lugha: " + str(lugha) + "\n")
                        target_device.write("# mushkilat: " + str(mushkilat) + "\n")
                        target_device.write("# mutashabih: " + str(mutashabih) + "\n")
                        target_device.write("# naskh: " + str(naskh) + "\n")
                        target_device.write("# qiraat: " + str(qiraat) + "\n")
                        target_device.write("# science: " + str(science) + "\n")
                        target_device.write("# sirah: " + str(sirah) + "\n")
                        target_device.write("# sufism: " + str(sufism) + "\n")
                        target_device.write("# takhsis: " + str(takhsis) + "\n")
                        target_device.write("# tikrar: " + str(tikrar) + "\n")
                        target_device.write("# israeliyat: " + str(israeliyat) + "\n")
                        #if mushkilat == 1 or mutashabih == 1 or takhsis == 1 or
                        #  tikrar == 1 or sirah == 1:
                        #   target_device.write("# other: " + "1" + "\n")
                        #else: 
                        #    target_device.write("# other: " + "0" + "\n")
                    else:
                        target_device.write(line)
            counter += 1
            target_device.close()
            os.remove(input_file)          

    print('Process finished')

if __name__ == "__main__":
    import shutil
    #path = "Full PATH of input folder with XML files"
    path ="../TEI2CoNLL/Input-TEI2CoNLL/input"

    # Creating output folder.
    datetime_str = datetime.datetime.now().strftime(format="%Y-%m-%d_%H-%M-%S")
    output_directory = os.path.join(os.getcwd(), "output")
    if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            file_path_to_write = output_directory
    else:
        file_path_to_write = os.path.join(os.getcwd(), datetime_str)
        os.mkdir(file_path_to_write)
    
    copy('TEI2CoNLL.py', os.path.join(file_path_to_write, 'TEI2CoNLL.py'))

    # isnad_flag -> 1 No ISNAD , 0 ISNAD 
    # NER, ISNAD YES, Topics, Subtopics
    # subtopic_filter -> 1 filter on, 0 filter off

    # Sentence segmentation on:
    replace_topic_style(write_output_to_three_files(delete_sentence_without_ner(bio_form_subtopics_str(delete_topic_nosentence(insert_topic(segmentation_of_sentences(add_names_str(nerNames(join_files(path, isnad_flag = 0), topic_flag = 1, subtopic_flag = 1, isnad_flag = 0, subtopic_filter = 1))))))), file_path_to_write))

    # Sentence segmentation off:
    #replace_topic_style(write_output_to_three_files(delete_sentence_without_ner(bio_form_subtopics_str(delete_topic_nosentence(insert_topic(add_names_str(nerNames(join_files(path, isnad_flag = 0), topic_flag = 1, subtopic_flag = 1, isnad_flag = 0, subtopic_filter = 1)))))), file_path_to_write))

  
 
