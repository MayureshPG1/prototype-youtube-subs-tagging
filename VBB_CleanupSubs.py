import os
import re

def cleanupSubsFromFolder(foldername):
    """opens all files with *.vtt extension cleans them and saves temparary *.tmp.txt files"""
    foldername = foldername + '/'
    files = os.listdir(foldername)
    files_vtt = [f for f in files if f.endswith('.vtt')]

    for file in files_vtt:
        cleanupFile(foldername + file)

def cleanupFile(filename):
    """opens individual with *.vtt extension cleans them and saves temparary *.tmp.txt files"""
    # open text file
    text = open(filename).read()

    # remove html tags out of file
    remove_html_regex = re.compile('<.*?>')
    text_no_html = re.sub(remove_html_regex, '',text)

    # remove timecodes containing '-->' and other sub info
    lines = text_no_html.splitlines()
    lines_no_timecodes = [line for line in lines if '-->' not in line if 'Style:' not in line if '::cue' not in line]
    # first 3 lines is metadata
    lines_no_timecodes = lines_no_timecodes[3:]

    # convert lines to text
    text_no_html_timecodes = "\n".join(lines_no_timecodes)

    # remove other chars
    text_no_html_timecodes_dashes = text_no_html_timecodes.replace('-', ' ').replace('#','').replace('}','')

    # write cleaned up temparoty text file
    file = open(filename.replace('vtt', 'tmp.txt'),"w")
    file.write(text_no_html_timecodes_dashes)
    file.close()
