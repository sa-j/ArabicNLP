"""Converts GK-bin-files into TEI XML.

Copy files to convert into the program-folder and write file names in the list files_to_convert. The program generates
for each file, which it was able to open, a new file with the same name except that it is have xml-ending.

4me:
@ l 22489 ein @ zu viel, gefunden mit regex: (?<!\d )@(?! \d)
1. Zeile anderer line break
l. 30548 fehler in gk bei versauszeichnung

"""

import re
import codecs
import sys


def gk_pages_to_tei(file_as_list):
    """Gets the file as list and removes all code errors corresponding to the E-problem.
    The letter E indicates the page division in the GK edition and is followed by the page number. This function
    converts the GK format to TEI format. The letter E is preceded by bytes that are not compatible with utf-8 format.
    This function finds these code errors. There can be up to three bytes between the code error and the letter E, not
    all of which are necessarily defective. From the first byte to the letter E, all bytes are converted into a number
    so that these values are not lost. The target format of the tag is ' <pb type="GK-pages" subtype="DEFECTCODE"
    n="PAGENUMBER"/>'."""
    print("gk_pages_to_tei started.")

    file_as_list_new = []
    i = 0
    while i < len(file_as_list):
        if file_as_list[i] < 128:  # 0xxxxxx. Can stand alone.
            file_as_list_new.append(file_as_list[i])
            i += 1

        elif file_as_list[i] < 192:  # 10xxxxxx. Can't stand alone.
            i = utf_error(file_as_list, file_as_list_new, i)

        elif file_as_list[i] < 224:  # 110xxxxx 10xxxxxx.
            if file_as_list[i + 1] < 128 or file_as_list[i + 1] >= 192:
                i = utf_error(file_as_list, file_as_list_new, i)
            else:
                file_as_list_new.append(file_as_list[i])
                file_as_list_new.append(file_as_list[i + 1])
                i += 2

        elif file_as_list[i] < 240:  # 1110xxxx 10xxxxxx 10xxxxxx.
            if file_as_list[i + 1] < 128 or file_as_list[i + 1] >= 192 or file_as_list[i + 2] < 128 \
                    or file_as_list[i + 2] >= 192:
                i = utf_error(file_as_list, file_as_list_new, i)
            else:
                file_as_list_new.append(file_as_list[i])
                file_as_list_new.append(file_as_list[i + 1])
                file_as_list_new.append(file_as_list[i + 2])
                i += 3
        elif file_as_list[i] < 248:  # 1110xxxx 10xxxxxx 10xxxxxx.
            if file_as_list[i + 1] < 128 or file_as_list[i + 1] >= 192 or file_as_list[i + 2] < 128 \
                    or file_as_list[i + 2] >= 192 or file_as_list[i + 3] < 128 \
                    or file_as_list[i + 3] >= 192:
                i = utf_error(file_as_list, file_as_list_new, i)
            else:
                file_as_list_new.append(file_as_list[i])
                file_as_list_new.append(file_as_list[i + 1])
                file_as_list_new.append(file_as_list[i + 2])
                file_as_list_new.append(file_as_list[i + 3])
                i += 4

        else:  # Does not exist.
            i = utf_error(file_as_list, file_as_list_new, i)

    print("gk_pages_to_tei finished.\n")
    return file_as_list_new


def utf_error(old_list, new_list, i):
    """Help function for gk_pages_to_tei: Gets index of false coded byte, changes this bytes and all following until the
    letter E into integer and returns the new index."""
    # Components for the new tag:
    tag_begin = '''<pb ed="GK" edRef="'''
    tag_middle = '''" n="'''
    tag_end = '''"/>'''

    # Sums the values before the letter E:
    mysterious_number = 0b0
    while old_list[i] != ord('E'):
        mysterious_number = (mysterious_number << 8) + old_list[i]
        i += 1

    i += 1  # Skips the letter E.

    # Gets the number after E:
    page_number = ''
    while old_list[i] != ord(' '):
        page_number += chr(old_list[i])
        i += 1

    # Inserts the string into the list:
    str_to_insert = tag_begin + str(mysterious_number) + tag_middle + str(page_number) + tag_end
    insert_str_to_list(new_list, str_to_insert)

    return i


def insert_str_to_list(new_list, str_to_insert):
    """Appends string to list."""
    j = 0
    while j < len(str_to_insert):
        new_list.append(ord(str_to_insert[j]))
        j += 1


def remove_unnecessary_tags(file_as_string):
    """"""
    print("remove_unnecessary_tags started.")

    file_as_string = re.sub(r' /(0|9|(15)|(55)|(64)) ',
                            r' ', file_as_string)
    print('\t/0, /9, /15, /55, /64 removed.')

    print("remove_unnecessary_tags finished.\n")
    return file_as_string


def gk_lines_to_tei(file_as_list):
    """Inserts lb-tags for GK-lines."""
    print("gk_lines_to_tei started.")

    file_as_list_new = []
    n = 1  # Counts line numbers.
    insert_str_to_list(file_as_list_new, '''<lb ed="GK" n="''' + str(n) + '''"/> ''')
    n += 1
    i = 0
    while i < len(file_as_list):
        if file_as_list[i] == 0xd and i < len(file_as_list)-2:  # \x0d = CARRIAGE RETURN (CR) / '\r', \x0a = LINE FEED
            # (LF) / '\n'
            file_as_list_new.append(0xd)
            file_as_list_new.append(0xa)
            insert_str_to_list(file_as_list_new, '''<lb n="''' + str(n) + '''"/> ''')
            n += 1
            i += 2
        else:
            file_as_list_new.append(file_as_list[i])
            i += 1

    print("gk_lines_to_tei finished.\n")
    return file_as_list_new


def remove_unnecessary_line_breaks(file_as_string):
    """Inserts lb-tags for GK-lines."""
    print("gk_lines_to_tei started.")

    file_as_string = re.sub(r'(?P<copy>(<lb[^>]+?>(<pb[^>]+?>)+))\r\n',
                            r'\g<copy>', file_as_string)

    print("gk_lines_to_tei finished.\n")
    return file_as_string


def remove_unnecessary_blanks(file_as_string):
    """XXXX"""
    print("\tremove_unnecessary_blanks started.")

    file_as_string = re.sub(r'(  +)', r' ', file_as_string)
    file_as_string = re.sub(r'> <', r'><', file_as_string)
    #file_as_string = re.sub(r'> \r', r'>\r', file_as_string)

    print("\tremove_unnecessary_blanks finished.\n")
    return file_as_string


def pages_to_tei(file_as_string):
    """Converts the pagereferences in GK from the Turki edition into TEI. In GK they are saved in the following format:
    @ VOLUME : PAGE @"""
    print("pages_to_tei finished started.")

    # Finds all displaced at-symbols and prints them.
    matches = re.findall(r'(?<=<lb n=.)\d+(?=.*\D @ \D.*\r\n)', file_as_string)
    if matches:
        print('\tAttention: @-symbol out of context, see line:')
        i = 1
        for match in matches:
            print('\t' + str(i) + '. ' + match)
            i += 1

    # Transforms the gk-format to TEI.
    file_as_string = re.sub(r"@ (?P<copy1>\d+) : (?P<copy2>\d+) @",
                            r'<pb type="turki" n="\g<1>:\g<2>"/>', file_as_string)

    print("pages_to_tei finished.\n")
    return file_as_string


def paragraphs_to_tei(file_as_string):
    """"""
    print("paragraphs_to_tei started.")

    number_of_hadith = re.findall(r'(?<=\$)\d+', file_as_string)  # For finding mistakes.

    # Puts the numbers after the $-symbol between note-tags.
    result_note = re.subn(r'\$(?P<copy>[ \d/]+(?=[^\d/]))',
                            r'<note>\g<copy></note>', file_as_string)
    file_as_string = result_note[0]
    print('\tNote tags inserted.')

    #################### 4LOT ##########################################################################################
#    # Creates p-nothadith tags.
#    result_nothadith = re.subn(r'\r\n(?P<copy1>[^*\r\n]+)( )?(?P<copy2>([A-Z\d:]+( )?)+)( )?\r\n',
#                            r'\r\n<p n="nothadith" ana="\g<copy2>">\g<copy1></p>\r\n', file_as_string)
#    file_as_string = result_nothadith[0]
#    print('\tNothadith tags inserted.')
#
#    # Creates p-hadith tags.
#    result_hadith = re.subn(r'\r\n(?P<copy1>[^\r\n]*) \*( )?(?P<copy2>([A-Z\d:]+( )?)+)( )?\r\n',
#                            r'\r\n<p n="hadith" ana="\g<copy2>">\g<copy1></p>\r\n', file_as_string)
#    file_as_string = result_hadith[0]
#    print('\tHadith tags inserted.')
    ####################################################################################################################

    # Creates p-nothadith tags.
    result_nothadith = re.subn(r'(?P<copy1>[^*\r\n]+)( \r\n)',
                            r'<p n="nothadith">\g<copy1></p>\r\n', file_as_string)
    file_as_string = result_nothadith[0]
    print('\tNothadith tags inserted.')

    # Creates p-hadith tags.
    result_hadith = re.subn(r'(?P<copy1>[^\r\n]*) \* \r\n',
                            r'<p n="hadith">\g<copy1></p>\r\n', file_as_string)
    file_as_string = result_hadith[0]
    print('\tHadith tags inserted.')

    # Puts numbers to hadith.
    result_numbers = re.subn(r'<p n="hadith">(?P<copy1><lb n="\d+"/>[^\r]*<note>)(?P<copy2>\d+)',
                            r'<p n="hadith" xml:id="h\g<copy2>">\g<copy1>', file_as_string)
    print(str(result_numbers[1]) + 'numbers copied')
    file_as_string = result_numbers[0]

    # For finding mistakes.
    print('\t' + str(result_nothadith[1]) + ' nothadith tags inserted.')
    print('\t' + str(result_hadith[1]) + ' hadith tags inserted.')
    print('\t' + str(result_note[1]) + ' note tags inserted.')
    print('\t' + str(len(number_of_hadith)) + ' $\d+ found.')
    print('\t' + str(max(number_of_hadith, key=int)) + ' max number after $ found.')
    print('\t' + str(len(re.findall(r'\r\n', file_as_string))) + ' number of lines.')

#    if (len(number_of_hadith) != max(number_of_hadith, key=int) or len(number_of_hadith) != result_hadith[1] \
#            or result_hadith[1] != result_note[1] \
#            or result_hadith[1] + result_nothadith[1] != len(re.findall(r'\r\n', file_as_string))):
#        print('\tAttention: deviating numbers.')

    print("paragraphs_to_tei finished.\n")
    return file_as_string


def quran_to_tei(file_as_string):
    """/23 einschübe
    ln 45974
    ln 10729
    ln 34983 fehler im code"""
    print("quran_to_tei started.")

    # wenn vor einschub suren name
    file_as_string = re.sub(r'/4 (?P<copy1>[^/]*? )سورة (?P<copy2>[ ء-٩]+?) آية (?P<copy3>[_\d -]+?)/23(?P<copy4>.*?)/23(?P<copy5>.*?)سورة (?P<copy6>[ ء-٩]+?) آية (?P<copy7>[_\d -]+?) ?/4[^40]',  # Check for other files /4[^40 ] # <------------- fragezeichen nach blank file 3 $1959
                            r'<quote type="quran" n="\g<copy2>:\g<copy3>">\g<copy1></quote><add type="parenthesis" subtype="quran">\g<copy4></add><quote type="quran" n="\g<copy6>:\g<copy7>">\g<copy5></quote> ', file_as_string)

    # Creates quran tags.
    file_as_string = re.sub(r'/4 (?P<copy1>.*?) ?/4[^40]',  # Check for other files /4[^40 ]
                            r'<quote type="quran">\g<1> </quote> ', file_as_string)

    #
    file_as_string = re.sub(r'<quote type="quran">(?P<copy1>[^q]* )سورة (?P<copy2>[ ء-٩]*?) آية (?P<copy3>[_\d -]+?) </quote>',
                            r'<quote type="quran" n="\g<2>:\g<3>">\g<1></quote> ', file_as_string)

    file_as_string = re.sub(r'<quote type="quran">(?P<copy1>[^q]*? )آية (?P<copy2>[_\d -]+?) سورة (?P<copy3>[ ء-٩]*?) </quote>',
                            r'<quote type="quran" n="\g<3>:\g<2>">\g<1></quote> ', file_as_string)

    file_as_string = re.sub(r'<quote type="quran">(?P<copy1>[^q]*? )سورة (?P<copy2>[^q]*?) آية (?P<copy3>[^q]*?) </quote>',
                            r'<quote type="quran" n="\g<2>:\g<3>">\g<1></quote> ', file_as_string)

    #file_as_string = re.sub(r'qurXn', r'quran', file_as_string)


    # Format vereinheitlichen
    file_as_string = re.sub(r'(?P<copy1>:\d+) [-_] (?P<copy2>\d+)',
                            r'\g<1>-\g<2>', file_as_string)

    # Lesarten Tag.
    file_as_string = re.sub(r'/90 (?P<copy1>.*? )/90',  # Check for other files /4[^40 ]
                            r'<quote type="qiraat">\g<1></quote> ', file_as_string)

    # Kurzes Koranziat
    file_as_string = re.sub(r'/44 (?P<copy1>.*? )/44',  # Check for other files /4[^40 ]
                            r'<quote type="quran" subtype="short">\g<1></quote> ', file_as_string)
# Hiermit hatte es geklappt
#    # Creates quran tags.
#    file_as_string = re.sub(r'/4 (?P<copy1>.*?)/4[^40]',  # Check for other files /4[^40 ]
#                            r'<quote type="quran">\g<1></quote> ', file_as_string)
#
#    file_as_string = re.sub(r'<quote type="quran">(?P<copy1>.*?) سورة (?P<copy2>[ ء-٩]*?) آية (?P<copy3>[_\d -]+?) </quote>',
#                            r'<quote type="quran" n="\g<2>:\g<3>">\g<1></quote> ', file_as_string)
#
#    #
#    file_as_string = re.sub(r'/90 (?P<copy1>.*?) /90',  # Check for other files /4[^40 ]
#                            r'<quote type="qiraat">\g<1></quote> ', file_as_string)

    # Wandelt die Surennamen in Zahlen um.
    list_of_suras = [['الفاتحة', 1], ['الحمد', 1], ['سبع المثاني', 1], ['البقرة', 2], ['آل عمران', 3], ['آل', 3],
                     ['النساء', 4], ['النّساء', 4], ['المائدة', 5], ['الأنعام', 6], ['الأعراف', 7], ['الأنفال', 8],
                     ['التوبة', 9], ['البراءة', 9], ['يونس', 10], ['هود', 11], ['يوسف', 12], ['الرعد', 13],
                     ['إبراهيم', 14], ['الحجر', 15], ['النحل', 16], ['الإسراء', 17], ['بني إسرائيل', 17], ['الكهف', 18],
                     ['مريم', 19], ['طه', 20], ['الأنبياء', 21], ['الحج', 22], ['المؤمنون', 23], ['النور', 24],
                     ['الفرقان', 25], ['الشعراء', 26], ['النمل', 27], ['القصص', 28], ['العنكبوت', 29], ['الروم', 30],
                     ['لقمان', 31], ['السجدة', 32], ['الأحزاب', 33], ['سبأ', 34], ['الملائكة', 35], ['فاطر', 35],
                     ['يس', 36], ['الصافات', 37], ['ص', 38], ['الزمر', 39], ['غافر', 40], ['المؤمن', 40], ['فصلت', 41],
                     ['حم', 41], ['الشورى', 42], ['الزخرف', 43], ['الدخان', 44], ['الجاثية', 45], ['الأحقاف', 46],
                     ['محمد', 47], ['القتال', 47], ['الفتح', 48], ['الحجرات', 49], ['ق', 50], ['الذاريات', 51],
                     ['الطور', 52], ['النجم', 53], ['القمر', 54], ['الرحمن', 55], ['الواقعة', 56], ['الحديد', 57],
                     ['المجادلة', 58], ['الحشر', 59], ['الممتحنة', 60], ['الصف', 61], ['الجمعة', 62], ['المنافقون', 63],
                     ['التغابن', 64], ['الطلاق', 65], ['التحريم', 66], ['الملك', 67], ['القلم', 68], ['ن', 68],
                     ['الحاقة', 69], ['المعارج', 70], ['نوح', 71], ['الجن', 72], ['المزمل', 73], ['المدثر', 74],
                     ['القيامة', 75], ['الْقِيَامَة', 75], ['الإنسان', 76], ['الْإِنْسَان', 76], ['الدهر', 76],
                     ['المرسلات', 77], ['النبأ', 78], ['النازعات', 79], ['عبس', 80], ['التكوير', 81], ['الانفطار', 82],
                     ['المطففين', 83], ['الانشقاق', 84], ['البروج', 85], ['الطارق', 86], ['الأعلى', 87],
                     ['الغاشية', 88], ['الفجر', 89], ['البلد', 90], ['الشمس', 91], ['الليل', 92], ['الضحى', 93],
                     ['الشرح', 94], ['التين', 95], ['العلق', 96], ['إقرا', 96], ['القدر', 97], ['البينة', 98],
                     ['الزلزلة', 99], ['العاديات', 100], ['القارعة', 101], ['التكاثر', 102], ['العصر', 103],
                     ['الهمزة', 104], ['الهمزة', 104], ['الهُمَزَة', 104], ['الفيل', 105], ['قريش', 106],
                     ['الماعون', 107], ['الكوثر', 108], ['الكافرون', 109], ['النصر', 110], ['المسد', 111],
                     ['أبو لهب', 111], ['الإخلاص', 112], ['الفلق', 113], ['الناس', 114]]

    for i in list_of_suras:
        name = i[0]
        number_as_string = str(i[1])
        file_as_string = re.sub('<quote type="quran" n="' + name,
                                '<quote type="quran" n="' + number_as_string, file_as_string)

    # Error finding: Suranames.
    matches = re.findall(r'(?<=<lb n=")\d+?(?="/>[^\r]*<quote type="quran" n="[ء-٩][^\r]*)', file_as_string)
    if matches:
        print('\tAttention: unknown sura names, see line:')
        i = 1
        for match in matches:
            print('\t' + str(i) + '. ' + match)
            i += 1

    # Versseqarators: Vers { number } Vers ...
    file_as_string = re.sub(r'(?P<copy1>[^<>{}\r]+? ){ (?P<copy2>\d+) }',
                            r'<l n="\g<2>">\g<1></l>', file_as_string)

    # Error finding: Suranames.
    matches = re.findall(r'(?<=<lb n=")(\d+?)(?="/>[^\r]*?((/4 )|(/44 )|(/90 )|({ )|(} ))[^\r]*?\r\n)', file_as_string)
    if matches:
        print('\tThere may be problems, see line:')
        i = 1
        for match in matches:
            print('\t' + str(i) + '. ' + match[0])
            i += 1

    print("quran_to_tei finished.\n")
    return file_as_string


def parentheses_to_tei(file_as_string):
    """  """
    print("parentheses_to_tei started.")

    file_as_string = re.sub(r'/23 (?P<copy1>.*?)/23 ',  # überprüfen, ob leerzeichen hinter ?
                            r'<add type="parenthesis">\g<1></add> ', file_as_string)

    print("parentheses_to_tei finished.\n")
    return file_as_string


def poetry_to_tei(file_as_string):
    """zu viele fehler in der kodierung manchmal 51 statt 50 und umgekehrt
    Achtung: pb kann in die quere kommen."""
    print("poetry_to_tei started.")

    # An einigen Stellen zumindest in Tabari befinden sich in Überlieferungen die schließende Elemente in der
    # nächsten Zeile. Hier werden sie nach vorne gezogen.
    file_as_string = re.sub(r' \* \r\n(?P<copy1><lb n="\d+"/>) /51 /50',
                            r' /51 /50 * \r\n\g<1>', file_as_string)

    # Umschließt "gesunde" Gruppen mit quote.
    file_as_string = re.sub(r'(?<!/51 )(?P<copy1>(/50 (?=/51)[^\r]*?(?<=/51) /50 )+)',
                            r'<quote type="poetry">\g<1></quote> ', file_as_string)

    # Kennezeichnet half-lines, die jedoch als ganze gekennzeichnet sind.
    file_as_string = re.sub(r'/50 /51(?P<copy1> [^5\r]*? )/51 /50',
                            r'<l n="halfline_50-51_51-50">\g<1></l> ', file_as_string)

    #  Bearbeitet "gesunde" Verse.
    file_as_string = re.sub(r'/50(?P<copy1> (/51 [^5\r]*? /51 ){2})/50',
                            r'<lg type="line">\g<1></lg> ', file_as_string)
    file_as_string = remove_unnecessary_blanks(file_as_string)
    file_as_string = re.sub(r'(?<=<lg type="line"> )/51 (?P<copy1>[^5\r]*? )/51 /51 (?P<copy2>[^5\r]*? )/51(?= </lg>)',
                            r'<l n="half-line">\g<1></l><l n="half-line">\g<2></l>', file_as_string)
    file_as_string = remove_unnecessary_blanks(file_as_string)


    # Beabreitet 50er Gruppen.
    file_as_string = re.sub(r'(?P<copy1>(?<!try">)((?<!51 )/50(?! /5[0|1])) [^:l\r]+(/50 /50 [^:l\r])* '
                            r'(?<!/quote>)((?<!51 )/50(?! /5[0|1])))',
                            r'<quote type="poetry" subtype="50_50">\g<1></quote> ', file_as_string)
    result = [0, 1]
    while result[1]:
        result = re.subn(r'(?P<copy1>subtype="50_50">) ?/50(?P<copy2>[^/\r]*? )/50',
                         r'\g<1><l n="line_50_50">\g<2></l><l n="line_50_50">',
                         file_as_string)
        file_as_string = result[0]
    file_as_string = re.sub(r'(?<=subtype="50_50">)(?P<copy1>[^/\r]*? )/50',
                            r'\g<1></l>',
                            file_as_string)
    file_as_string = re.sub(r'<l n="line_50_50"><l n="line_50_50">',
                            r'<l n="line_50_50">',
                            file_as_string)
    file_as_string = re.sub(r'<l n="line_50_50"></quote>',
                            r'</quote>',
                            file_as_string)

    # löschen
    file_as_string = re.sub(r'(( n="line_50_50")|( subtype="50_50")|( n="halfline_50-51_51-50")|( n="halfline")|( type="line")|( n="half-line"))',
                            r'',
                            file_as_string)

    # For finding mistakes.
    matches = re.findall(r'(?<=<lb n=")(\d+?)(?="/>[^\r]*?((/50 )|(/51 ))[^\r]*?\r\n)', file_as_string)
    if matches:
        print('\tAttention: mistakes in line:')
        i = 1
        for match in matches:
            print('\t' + str(i) + '. ' + match[0])
            i += 1

    print("poetry_to_tei finished.\n")
    return file_as_string


def heads_to_tei(file_as_string):
    """  """
    print("heads_to_tei started.")
#    file_as_string = re.sub(r'/1 (?P<copy1>([^\r]*? ))/1 ?',
#                            r'<head type="1">\g<1></head>', file_as_string)
#    file_as_string = re.sub(r'/30 (?P<copy1>([^\r]*? ))/30 ?',
#                            r'<head type="30">\g<1></head>', file_as_string)
#    file_as_string = re.sub(r'/7 (?P<copy1>([^\r]*? ))/7 ?',
#                            r'<head type="7">\g<1></head>', file_as_string)

#    file_as_string = re.sub(r'/1 (?P<copy1>([^\r]*? ))/1 ?',
#                            r'</p>\r\n</div>\r\n<div type="chapter">\r\n<head type="1">\g<1></head>\r\n<p n="nothadith">', file_as_string)
#    file_as_string = re.sub(r'/30 (?P<copy1>([^\r]*? ))/30 ?',
#                            r'</p>\r\n</div>\r\n<div type="section">\r\n<head type="30">\g<1></head>\r\n<p n="nothadith">', file_as_string)
#    file_as_string = re.sub(r'/7 (?P<copy1>([^\r]*? ))/7 ?',
#                            r'</p>\r\n</div>\r\n<div type="subsection">\r\n<head type="7">\g<1></head>\r\n<p n="nothadith">', file_as_string)

#    file_as_string = re.sub(r'/30 (?P<copy1>([^\r]*? ))/30 ?',
#                            r'</p>\r\n<div type="section">\r\n<head type="30">\g<1></head>\r\n<p n="nothadith">', file_as_string)
#    file_as_string = re.sub(r'/7 (?P<copy1>([^\r]*? ))/7 ?',
#                            r'</p>\r\n<div type="subsection">\r\n<head type="7">\g<1></head>\r\n<p n="nothadith">', file_as_string)

    file_as_string = re.sub(r'/1 (?P<copy1>([^\r]*? ))/1 ?',
                            r'</p>\r\n<div type="chapter">\r\n<head type="1">\g<1></head>\r\n<p n="nothadith">',
                            file_as_string)

    file_as_string = re.sub(r'(?P<copy1><lb n="\d+"/>(<pb [a-zA-Z0-9"=: ]+ />)*)/30 (?P<copy2>([^\r]*? ))/30 ?',
                            r'</p>\r\n<div type="section">\r\n<head type="30">\g<1>\g<2></head>\r\n<p n="nothadith">',
                         file_as_string)
    file_as_string = re.sub(r'(?P<copy1><lb n="\d+"/>(<pb [a-zA-Z0-9"=: ]+ />)*)/7 (?P<copy2>([^\r]*? ))/7 ?',
                            r'</p>\r\n<div type="subsection">\r\n<head type="7">\g<1>\g<2></head>\r\n<p n="nothadith">',
                         file_as_string)

    file_as_string = re.sub(r'/30 (?P<copy1>([^\r]*? ))/30 ?',
                            r'</p>\r\n<div type="section">\r\n<head type="30">\g<1></head>\r\n<p n="nothadith">',
                         file_as_string)
    file_as_string = re.sub(r'/7 (?P<copy1>([^\r]*? ))/7 ?',
                            r'</p>\r\n<div type="subsection">\r\n<head type="7">\g<1></head>\r\n<p n="nothadith">',
                        file_as_string)

    file_as_string = re.sub(r'<p n="nothadith"> *?</p>\r\n', r'', file_as_string)

    i = 0  # Chapter
    j = 1  # Section
    k = 1  # Subsection
    n = 0
    section = False
    subsection = False
    string_list = []
    string = '<div type="chapter" n="' + str(i) + '">\r\n'

    while True:
        if n > len(file_as_string):
            break

        elif file_as_string[n:n + 20] == '<div type="chapter">':
            string += file_as_string[:n] + '</div>\r\n'
            file_as_string = file_as_string[n + 20:]
            n = 0
            if section:
                string += '</div>\r\n'
                section = False
            if subsection:
                string += '</div>\r\n'
                subsection = False
            # string_list.append(string)  # <--
            i += 1
            j = 1
            k = 1
            string += '<div type="chapter" n="' + str(i) + '" xml:lang="ar">'

        elif file_as_string[n:n + 20] == '<div type="section">':
            string += file_as_string[:n]
            file_as_string = file_as_string[n + 20:]
            n = 0
            if section:
                string += '</div>\r\n'
            if subsection:
                string += '</div>\r\n'
                subsection = False
            string += '<div type="section" n="' + str(i) + '.' + str(j) + '">'
            j += 1
            k = 1
            section = True

        elif file_as_string[n:n + 23] == '<div type="subsection">':
            string += file_as_string[:n]
            file_as_string = file_as_string[n + 23:]
            n = 0
            if subsection:
                string += '</div>\r\n'
            string += '<div type="subsection" n="' + str(i) + '.' + str(j-1) + '.' + str(k) + '">'
            k += 1
            subsection = True

        else:
            n += 1
    if section:
        string += '</div>\r\n'
    if subsection:
        string += '</div>\r\n'
    string += file_as_string + '</div>\r\n'

    print("heads_to_tei finished.\n")
    return string


def rawis_to_tei(file_as_string):
    """  """
    print("rawis_to_tei started.")

# r' حَدَّثَنِي /94 الْمُثَنَّى L41892 /94 ، قَالَ : ثنا /26 الْحِمَّانِيُّ L8287 /26 ، قَالَ : ثنا /26 قَيْسٌ L6514 /26 ، عَنِ /26 الأَعْمَشِ L3629 /26 ، عَنْ /26 أَبِي صَالِحٍ L2840 /26 ، /27 عَنْ /93 أَبِي هُرَيْرَةَ L4396 /93 ، قَالَ : قَالَ رَسُولُ اللَّهِ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ : " /20 مَا مِنْ مَوْلُودٍ يُولَدُ إِلا وَقَدْ عَصَرَهُ الشَّيْطَانُ عَصْرَةً أَوْ عَصْرَتَيْنِ ، إِلا عِيسَى ابْنَ مَرْيَمَ ، وَمَرْيَمَ " ، ثُمَّ قَرَأَ رَسُولُ اللَّهِ صَلَّى اللَّهُ عَلَيْهِ وَسَلَّمَ : <quote type="quran" n="3:36">وَإِنِّي أُعِيذُهَا بِكَ وَذُرِّيَّتَهَا مِنَ الشَّيْطَانِ الرَّجِيمِ </quote> /27 *'
    file_as_string = re.sub(r'/18 /94 (?P<copy1>[^/،,]+?) (?P<copy2>L\d+?) /94 /18',
                            r'<persName ana="unknown_shaykh" n="\g<2>">\g<1></persName> ', file_as_string)
    file_as_string = re.sub(r'/18 /94 (?P<copy1>[^،/,]+?) /94 /18',
                            r'<persName ana="unknown_shaykh">\g<1></persName> ', file_as_string)

    file_as_string = re.sub(r'/94 (?P<copy1>[^/،,]+?) (?P<copy2>L\d+?) /94',
                            r'<persName ana="shaykh" n="\g<2>">\g<1></persName> ', file_as_string)
    file_as_string = re.sub(r'/94 (?P<copy1>[^/،,]+?) /94',
                            r'<persName ana="shaykh">\g<1></persName> ', file_as_string)

    file_as_string = re.sub(r'/18 /26 (?P<copy1>[^/،,]+?) (?P<copy2>L\d+?) /26 /18',
                            r'<persName ana="unknown_rawi" n="\g<2>">\g<1></persName> ', file_as_string)
    file_as_string = re.sub(r'/18 /26 (?P<copy1>[^/،,]+?) /26 /18',
                            r'<persName ana="unknown_rawi">\g<1></persName> ', file_as_string)

    file_as_string = re.sub(r'/26 (?P<copy1>[^/،,]+?) (?P<copy2>L\d+?) /26',
                            r'<persName ana="rawi" n="\g<2>">\g<1></persName> ', file_as_string)
    file_as_string = re.sub(r'/26 (?P<copy1>[^/،،,]+?) /26',
                            r'<persName ana="rawi">\g<1></persName> ', file_as_string)

    file_as_string = re.sub(r'/18 /93 (?P<copy1>[^/،,]+?) (?P<copy2>L\d+?) /93 /18',
                            r'<persName ana="unknown_sahabi" n="\g<2>">\g<1></persName> ', file_as_string)
    file_as_string = re.sub(r'/18 /93 (?P<copy1>[^/،,]+?) /93 /18',
                            r'<persName ana="unknown_sahabi">\g<1></persName> ', file_as_string)

    file_as_string = re.sub(r'/93 (?P<copy1>[^/،,]+?) (?P<copy2>L\d+?) /93',
                            r'<persName ana="sahabi" n="\g<2>">\g<1></persName> ', file_as_string)
    file_as_string = re.sub(r'/93 (?P<copy1>[^/،,]+?) /93',
                            r'<persName ana="sahabi">\g<1></persName> ', file_as_string)

    ## zweite runde
    #file_as_string = re.sub(r'/18 /94 (?P<copy1>[^<>/]+?) (?P<copy2>L\d+?) /94 /18',
    #                        r'<persName ana="unknown_shaykh" n="\g<2>">\g<1></persName> ', file_as_string)
    #file_as_string = re.sub(r'/18 /94 (?P<copy1>[^<>/]+?) /94 /18',
    #                        r'<persName ana="unknown_shaykh">\g<1></persName> ', file_as_string)
    #
    #file_as_string = re.sub(r'/94 (?P<copy1>[^<>/]+?) (?P<copy2>L\d+?) /94',
    #                        r'<persName ana="shaykh" n="\g<2>">\g<1></persName> ', file_as_string)
    #file_as_string = re.sub(r'/94 (?P<copy1>[^<>/]+?) /94',
    #                        r'<persName ana="shaykh">\g<1></persName> ', file_as_string)
    #
    #file_as_string = re.sub(r'/18 /26 (?P<copy1>[^<>/]+?) (?P<copy2>L\d+?) /26 /18',
    #                        r'<persName ana="unknown_rawi" n="\g<2>">\g<1></persName> ', file_as_string)
    #file_as_string = re.sub(r'/18 /26 (?P<copy1>[^<>/]+?) /26 /18',
    #                        r'<persName ana="unknown_rawi">\g<1></persName> ', file_as_string)
    #
    #file_as_string = re.sub(r'/26 (?P<copy1>[^<>/]+?) (?P<copy2>L\d+?) /26',
    #                        r'<persName ana="rawi" n="\g<2>">\g<1></persName> ', file_as_string)
    #file_as_string = re.sub(r'/26 (?P<copy1>[^<>/]+?) /26',
    #                        r'<persName ana="rawi">\g<1></persName> ', file_as_string)
    #
    #file_as_string = re.sub(r'/18 /93 (?P<copy1>[^<>/]+?) (?P<copy2>L\d+?) /93 /18',
    #                        r'<persName ana="unknown_sahabi" n="\g<2>">\g<1></persName> ', file_as_string)
    #file_as_string = re.sub(r'/18 /93 (?P<copy1>[^<>/]+?) /93 /18',
    #                        r'<persName ana="unknown_sahabi">\g<1></persName> ', file_as_string)
    #
    #file_as_string = re.sub(r'/93 (?P<copy1>[^<>/]+?) (?P<copy2>L\d+?) /93',
    #                        r'<persName ana="sahabi" n="\g<2>">\g<1></persName> ', file_as_string)
    #file_as_string = re.sub(r'/93 (?P<copy1>[^<>/]+?) /93',
    #                        r'<persName ana="sahabi">\g<1></persName> ', file_as_string)




    # For finding mistakes.
    matches = re.findall(r'(?<=<lb n=")(\d+?)(?="/>[^\r]*?((/93)|(/94)|(/26)|(/18))[^\r]*?\r\n)', file_as_string)
    if matches:
        print('\tThere may be problems, see line:')
        i = 1
        for match in matches:
            print('\t' + str(i) + '. ' + match[0])
            i += 1

    print("rawis_to_tei finished.\n")
    return file_as_string


def names_to_tei(file_as_string):
    """  """
    print("names_to_tei started.")

    file_as_string = re.sub(r'/57 (?P<copy1>[^/،,]+?)/57 ',  # überprüfen, ob leerzeichen hinter ?
                            r'<persName type="angel">\g<1></persName> ', file_as_string)

    file_as_string = re.sub(r'/60 (?P<copy1>[^/،,]+?)/60 ',  # überprüfen, ob leerzeichen hinter ?
                            r'<placeName type="60">\g<1></placeName> ', file_as_string)

    file_as_string = re.sub(r'/65 (?P<copy1>[^/،,]+?)/65 ',  # überprüfen, ob leerzeichen hinter ?
                            r'<name type="sura">\g<1></name> ', file_as_string)

    # For finding mistakes.
    matches = re.findall(r'(?<=<lb n=")(\d+?)(?="/>[^\r]*?((/57)|(/60)|(/65))[^\r]*?\r\n)', file_as_string)
    if matches:
        print('\tThere may be problems, see line:')
        i = 1
        for match in matches:
            print('\t' + str(i) + '. ' + match[0])
            i += 1

    print("names_to_tei finished.\n")
    return file_as_string


def matn_to_tei(file_as_string):
    """  """
    print("matn_to_tei started.")

    file_as_string = re.sub(r'/27(?P<copy1>.*?)/20 (?P<copy2>.+? )/27 ',  # überprüfen, ob leerzeichen hinter ?
                            r'\g<1><said>\g<2></said> ', file_as_string)

    # For finding mistakes.
    matches = re.findall(r'(?<=<lb n=")(\d+?)(?="/>[^\r]*?((/20 )|(/27 ))[^\r]*?\r\n)', file_as_string)
    if matches:
        print('\tThere may be problems, see line:')
        i = 1
        for match in matches:
            print('\t' + str(i) + '. ' + match[0])
            i += 1

    print("matn_to_tei finished.\n")
    return file_as_string


def main():
    """..."""
    files_to_convert = ['0338.bin']  # List of files.['Turki_Bd8-10_AnnotiertMR.bin'] #
    # 'Turki_Bd6-7_AnnotiertMR.bin'

    while files_to_convert:  # Processes all elements of the list.
        current_filename = files_to_convert.pop()

        # Opens the file and reads it:
        try:  # In case file to open does not exist.
            with open(current_filename, mode='rb', encoding=None) as f:  # Opens file in read-binary-modus.
                file_as_bytearray = f.read()
        except OSError:
            # 'File not found' error message.
            print("File '" + current_filename + "' not found")

        # Converts bytearray to list, every byte gets an element:
        file_as_list = []
        for byte in file_as_bytearray:
            file_as_list.append(byte)

        file_as_list = gk_pages_to_tei(file_as_list)  # Converts the GK-pages into TEI and removes the utf-8 errors.
        file_as_list = gk_lines_to_tei(file_as_list)  # Inserts newline tags.

        file_as_string = bytearray(file_as_list).decode()  # Converts list to string.
        file_as_string = remove_unnecessary_tags(file_as_string)
        file_as_string = remove_unnecessary_blanks(file_as_string)  # Removes double blanks.

        results = re.subn(r'(?P<copy1>((>)|(\n)))([^E <>/]+?)(?P<copy2>E\d+)',
                          r'\g<copy1><pb ed="GK" edRef="error" n="\g<copy2>"/>', file_as_string)
        file_as_string = results[0]
        print(str(results[1]) + ' GK-pages not correctly inserted')

        file_as_string = names_to_tei(file_as_string)
        file_as_string = pages_to_tei(file_as_string)  # Converts the printed edition pages into TEI.
        file_as_string = remove_unnecessary_blanks(file_as_string)  # Removes double blanks.
        file_as_string = remove_unnecessary_line_breaks(file_as_string)  # Removes line breaks before the GK-pages tags.

        file_as_string = quran_to_tei(file_as_string)
        file_as_string = parentheses_to_tei(file_as_string)
        file_as_string = remove_unnecessary_blanks(file_as_string)  # Removes double blanks.
        file_as_string = poetry_to_tei(file_as_string)

        file_as_string = rawis_to_tei(file_as_string)
        file_as_string = matn_to_tei(file_as_string)

        file_as_string = remove_unnecessary_blanks(file_as_string)
        file_as_string = paragraphs_to_tei(file_as_string)  # Converts XXXXXXXXX into TEI.

        ########################
        with codecs.open("test_vor.bin", mode='wb', errors='strict') as f_new:
            f_new.write(file_as_string.encode(encoding="utf-8"))
        file_as_string = heads_to_tei(file_as_string)
        with codecs.open("test_nach.bin", mode='wb', errors='strict') as f_new:
            f_new.write(file_as_string.encode(encoding="utf-8"))
        ########################

        file_as_string = remove_unnecessary_blanks(file_as_string)

        file_as_string = re.sub(r'\r\n(?!<p )(?P<copy1>([^\r]*?))(?=</p>\r\n)',
                                r'\r\n<p n="nothadith">\g<copy1>',
                                file_as_string)
        file_as_string = re.sub(r'(?<=\r\n<p )(?P<copy1>([^\r]*?))(?<!</p>)\r\n',
                                r'\g<copy1></p>\r\n',
                                file_as_string)
        file_as_string = re.sub(r'> \r', r'>\r', file_as_string)

        n = 12
        string_list = []
        while True:
            if n > len(file_as_string):
                break
            elif file_as_string[n:n+12] == r'<div type="c':
                string_list.append(file_as_string[:n])
                file_as_string = file_as_string[n:]
                n = 12
            else:
                n += 1
        string_list.append(file_as_string)

        # Saves string in new file.
        n = 0
        for element in string_list:
            with codecs.open(current_filename[:-4] + '_' + str(n) + '.' + 'xml', mode='wb', errors='strict') as f_new:
                f_new.write('<?xml version="1.0" encoding="UTF-8"?><TEI xmlns="http://www.tei-c.org/ns/1.0">'
                            '<teiHeader><fileDesc><titleStmt><title>test</title></titleStmt>'
                            '<publicationStmt><p>test</p></publicationStmt>'
                            '<sourceDesc><p>test</p></sourceDesc></fileDesc></teiHeader>'
                            '<text xml:lang="ar"><body>'.encode(encoding="utf-8"))
                f_new.write(element.encode(encoding="utf-8"))
                f_new.write('</body></text></TEI>'.encode(encoding="utf-8"))
            n += 1

# So funktionierts.
#        with codecs.open(current_filename[:-3] + '.' + 'xml', mode='wb', errors='strict') as f_new:
#            f_new.write('<?xml version="1.0" encoding="UTF-8"?>\r\n'
#                        '<TEI xmlns="http://www.tei-c.org/ns/1.0">\r\n\t<teiHeader>\r\n\t\t<fileDesc>\r\n\t\t\t<titleStmt><title>'
#                        'test</title></titleStmt>\r\n\t\t\t'
#                        '<publicationStmt><p>test</p></publicationStmt>'
#                        '\r\n\t\t\t<sourceDesc><p>test</p></sourceDesc>\r\n\t\t</fileDesc>\r\n\t'
#                        '</teiHeader>\r\n'
#                        '\t<text xml:lang="ar">\r\n\t\t<body>\r\n<div type="chapter">'.encode(encoding="utf-8"))
#            f_new.write(file_as_string.encode(encoding="utf-8"))
#            f_new.write('</div>\r\n</div>\r\n</div>\r\n\t\t</body>\r\n\t</text>\r\n</TEI>'.encode(encoding="utf-8"))


if __name__ == "__main__":
    main()
