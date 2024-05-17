"""
Parse txt files with ParZu and store in CoNLL format.

Script produced by Imge Yüzüncüoglu, Raha Musavi in summer semester 2023 in the course "Korpuslinguistische Analyse der Nominalflextion im Deutschen"

Prerequisites: ParZu has to be installed via Docker, see https://github.com/rsennrich/ParZu
"""

import os
import re
import sys
from pathlib import Path

"""
command for parsing
type 1023_0001416.txt | docker run -i rsennrich/parzu /ParZu/parzu > 1023_0001416_output.txt
"""

def run_script(infile, outfile, linewise=False):

    linewise_flag = ""
    if linewise:
        linewise_flag = "--linewise "

    # parsing on Windows platform
    if sys.platform.startswith("win"):
        command_for_parsing = "type " + str(infile.resolve()) + " | docker run -i rsennrich/parzu /ParZu/parzu " + linewise_flag + "> " + str(outfile.resolve())
        command = 'cmd /c "' +  command_for_parsing + '"'
        os.system(command)

    # parsing on Unix platform
    else:
        command_for_parsing = "cat " + str(infile.resolve()) + " | docker run -i rsennrich/parzu /ParZu/parzu " + linewise_flag + " > " + str(outfile.resolve())
        os.system(command_for_parsing)
