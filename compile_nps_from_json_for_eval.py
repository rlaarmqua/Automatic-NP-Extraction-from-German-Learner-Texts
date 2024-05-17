"""
Extract NPs and heads from JSON file for evaluation.
"""

import json
import os
from pathlib import Path


def run_script(infile, outfile):
    """
    Extract NPs and heads from JSON file for evaluation.
    """
    
    # load data
    infilename = infile.name.rstrip(".json")
    with open(infile, mode="r", encoding="utf-8") as j:
        content = j.read()
    nps = json.loads(content)
    
    # extract wordforms of NP and head
    for np in nps:
        with open(outfile, mode="w", encoding="utf-8") as o:
            for np in nps:
                extracted_np_strings = []
                head = ""
                for tok in np["TOK_info"]:
                    extracted_np_strings.append(np["TOK_info"][tok]["word_form"])
                for tok in np["HEAD_info"]["head"]:
                    
                    # ignore verb particles
                    if np["HEAD_info"]["head"][tok]["POS_STTS"] != "PTKVZ":
                        head = np["HEAD_info"]["head"][tok]["word_form"]
                
                print(infilename, np["sentence"], " ".join(extracted_np_strings), head, sep="\t", file=o)
                #print(infilename, np["sentence"], " ".join(extracted_np_strings), head, sep="\t")


