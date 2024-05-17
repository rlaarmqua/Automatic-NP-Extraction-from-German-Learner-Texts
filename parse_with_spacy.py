"""
Parse a txt file with spacy and store in CoNLL format.
"""

from pathlib import Path
import spacy


def run_script(infile, outfile):

    nlp = spacy.load("de_core_news_sm")
    nlp.add_pipe("conll_formatter", last=True)

    with open(infile, mode="r", encoding="utf-8") as f:
        text = f.readlines()

    with open(outfile, mode="w", encoding="utf-8") as o:
        for line in text:
            doc = nlp(line)

            print(doc._.conll_str, file=o)