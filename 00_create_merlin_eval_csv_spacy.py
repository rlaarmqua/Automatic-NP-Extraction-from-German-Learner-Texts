"""
Pipeline for extracting NPs from MERLIN based on SpaCy and store in a csv file for evaluation.
"""

from pathlib import Path
import os
import re

import compile_nps_from_json_for_eval
import extract_nps_from_conll_spacy
import initialize_np_json_spacy
import parse_with_spacy

txt_path = "data/merlin_input/"

evaluation_files = ["MERLIN_A1.txt",
                    "MERLIN_A2.txt",
                    "MERLIN_B1.txt",
                    "MERLIN_B2.txt",
                    "MERLIN_C1.txt",
                    "MERLIN_C2.txt"
                    ]

conll_path = "data/merlin_eval/spacy/conll/"
nps_path = "data/merlin_eval/spacy/nps/"
json_path = "data/merlin_eval/spacy/json/"
eval_csv_path = "data/merlin_eval/spacy/eval_csv/"

# Create directories if necessary
Path(conll_path).mkdir(parents=True, exist_ok=True)
Path(nps_path).mkdir(parents=True, exist_ok=True)
Path(json_path).mkdir(parents=True, exist_ok=True)
Path(eval_csv_path).mkdir(parents=True, exist_ok=True)

corpusname = "MERLIN_DE"

# Parse evaluation files with spacy

for file in evaluation_files:
    infile = txt_path + file
    outfilename = re.sub("\.txt", ".conll", file)
    outfile = conll_path + outfilename

    infile = Path(infile)
    outfile = Path(outfile)
    parse_with_spacy.run_script(infile, outfile)


# Extract NPs from CoNLL
for file in os.listdir(conll_path):
    if not file.endswith(".conll"): continue
    infile = conll_path + file
    outfilename = re.sub("\.conll", "_nps.pylist", file)
    outfile = nps_path + outfilename

    infile = Path(infile)
    outfile = Path(outfile)
    extract_nps_from_conll_spacy.run_script(infile, outfile)

# Initialize JSON
for file in os.listdir(nps_path):
    infile = nps_path + file
    outfilename = re.sub("_nps.pylist", ".json", file)
    outfile = json_path + outfilename

    infile = Path(infile)
    outfile = Path(outfile)
    initialize_np_json_spacy.run_script(infile, outfile, corpusname)

# Create evaluation file
for file in os.listdir(json_path):
    infile = json_path + file
    outfilename = re.sub(".json", "_spacy.csv", file)
    outfile = eval_csv_path + outfilename

    infile = Path(infile)
    outfile = Path(outfile)
    compile_nps_from_json_for_eval.run_script(infile, outfile)