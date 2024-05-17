"""
Fill NP information into a common JSON format.

Script started by Jay Suchardt, Niels Lange, Johanna Wrede in summer semester 2023 in the course "Korpuslinguistische Analyse der Nominalflextion im Deutschen"
edited by Ronja Laarmann-Quante
Last update: 2023_08_09
"""

import json
import ast
import re
import os
from pathlib import Path
import pprint

###############
# functions
###############

def build_np_dict() -> dict:
    """
    Function to build basic frame for a new NP.
    :return: basic dictionary frame for representing an NP
    """
    np_dict = {
                "file_ID": None,
                "sent_NP_ID": None,     # sentenceCount_NPcount
                "sentence": None,

                "metadata": {
                            "corpus" : None
                            },
               
                "NP_info": {
                            "len_np" : None,
                            "coordination": None,
                            },
               
                "HEAD_info": {
                                "head" : {},
                                "super_head" : {}
                            },

                "POST_info": {},
                
                "TOK_info": {},
               
                "relations": {}
               }

    return np_dict


def build_TOK_dict(tok: list) -> dict:
    """
    Function to build basic dictionary frame for a single TOK in an NP
    :param tok: list of information regarding a single token from an nps_pylist file
    :return: dictionary for token info
    """

    tok_dict = {"word_type": tok[3],
                "word_form": tok[1],
                "lemma": tok[2],
                "POS_STTS": tok[4],
                "index" : tok[0],
                "dep_rel": tok[7],
                "head_index": tok[6],
                "parser_morph_features": tok[5]
                }

    return tok_dict


def add_coordination(np_dict_list: list, extracted_nps_list: list) -> list:
    """
    :param np_dict_list: complete list of NP dictionaries for a single file
    :param extracted_nps_list: complete list of extracted NPs (_nps.pylist) for a file
    :return: if NP is coordinated with another NP, np_dict["NP_info"]["coordination"] is filled
    with list of IDs of coordinated NPs e.g. ["6_10","6_9"]
    """

    # collect tokens (their index) with deprel 'kon' or 'cj'
    collected_kons = []
    coordinated_nps = []

    for sentence in extracted_nps_list:

        # list of IDs of the current token and head of a coordinated NP
        sent_collected_kons = []
        # list of NP IDs that are coordinated
        sent_coordinated_nps = []

        for np in sentence:

            np_id = np[0]

            tokens = np[6]
            for tok in tokens:
                idx = tok[0]
                head = tok[6]
                deprel = tok[7]

                if deprel in ["kon", "cj"]:

                    #in order not to mix up multiple coordination chains in a sentence
                    #only add to the existing chain if the head of the kon is present there
                    if len(sent_collected_kons) > 0 and head in sent_collected_kons[-1]:
                        sent_collected_kons[-1].append(idx)
                        sent_collected_kons[-1].append(head)
                        sent_coordinated_nps[-1].append(np_id)

                    else:
                        sent_collected_kons.append([idx, head])
                        sent_coordinated_nps.append([np_id])

                    # get ID of the head NP of the coordination
                    for np2 in sentence:
                        for tok in np2[6]:
                            if tok[0] == head:
                                sent_coordinated_nps[-1].append(np2[0])

        collected_kons.extend(sent_collected_kons)
        coordinated_nps.extend(sent_coordinated_nps)

    # remove duplicates
    coordinated_nps = [set(chain) for chain in coordinated_nps]

    for np_dict in np_dict_list:
        for chain in coordinated_nps:
            #coordinations within the same NP (=chain length 1), e.g. of adjectives are not of interest
            if len(chain) > 1:
                if np_dict["sent_NP_ID"] in chain:
                    # sort makes an integer out of the NP number otherwise it's messed up because it's a string
                    np_dict["NP_info"]["coordination"] = sorted(list(chain), key=lambda x: int(x.split("_")[1]))

    return np_dict_list


def build_relations_dict():
    """
    Function to build basic dictionary frame for representing the relationship
    between two (or more) tokens from an NP
    :return: rel_dict basic dictionary frame
    """
    rel_dict = {
                "rel_type" : None,
                "involved": [],
                "ruler" : None,
                "possible_agreement": None
                 }

    return rel_dict
    

def add_TOK_info(np_dict: dict, np: list) -> dict:
    """
    Extract information about each token of an NP from input file (_nps.pylist)
    and add it to the NP dictionary under TOK_info
    :param np_dict: NP dictionary to add the info to
    :param np: extracted NP from input file
    :return: modified NP dictionary np_dict
    """


    #find ID of (first) noun so that all following can be treated as postnominal modifiers
    first_noun_idx = None
    for tok in np[6]:
        idx = int(tok[0])
        word_type = tok[3]
        if word_type == "N":
            if not first_noun_idx:
                first_noun_idx = idx
            if idx < first_noun_idx:
                first_noun_idx = idx

    i = 1
    p = 1
    for tok in np[6]:
        dep_rel = tok[7]


        # anything behind the first noun is collected under "postnominal_modifiers":
        idx = int(tok[0])
        if idx > first_noun_idx:

            #coordinations are is ignored because it's treated separately as coordination and not as part of NP
            if dep_rel in ["kon", "cj"]:
                continue

            np_dict["POST_info"]["P_TOK"+str(p)] = build_TOK_dict(tok)
            p += 1
            continue

        # get tok id name & build token dict
        tok_id = "TOK" + str(i)
        np_dict["TOK_info"][tok_id] = build_TOK_dict(tok)
        np_dict["TOK_info"][tok_id]["possible_morph_features"] =  []
        i += 1

    return np_dict


def add_HEAD_info(np_dict: dict, np: list) -> dict:
    """
    Extract information about each token of a *head* of an NP from input file (_nps.pylist)
    and add it to the NP dictionary under HEAD_info
    :param np_dict: NP dictionary to add the info to
    :param np: extracted NP from input file
    :return: modified NP dictionary np_dict
    """

    # super head (= head of head of NP)
    i = 1
    for tok in np[3]:

        # get tok id name & build token dict
        tok_id = "SH_TOK" + str(i)
        np_dict["HEAD_info"]["super_head"][tok_id] = build_TOK_dict(tok)
        i += 1

    # head (= head of NP)
    i = 1
    for tok in np[4]:

        # get tok id name & build token dict
        tok_id = "H_TOK" + str(i)
        np_dict["HEAD_info"]["head"][tok_id] = build_TOK_dict(tok)
        i += 1

    return np_dict



def add_must_agree_relations(np_dict: dict) -> dict:
    """
    Add relations of type "must_agree" to pairs of tokens from an NP
    :param np_dict: NP dictionary to add the info to
    :return: modified NP dictionary np_dict
    """

    rel_counter = 1

    #to keep track so that relations do not appear twice
    all_relations = []

    for token1 in np_dict["TOK_info"]:
        for token2 in np_dict["TOK_info"]:

            # relationship between Noun and Determiner/Adjective: noun is the "ruler" that determines the inflection
            if np_dict["TOK_info"][token1]["word_type"] == "N" and np_dict["TOK_info"][token2]["word_type"] in ["ART", "ADJA"]:

                    rel_dict = build_relations_dict()
                    rel_dict["rel_type"] = "must_agree"
                    rel_dict["involved"] = [token1, token2]
                    rel_dict["ruler"] = token1
                    np_dict["relations"]["rel_"+str(rel_counter)] = rel_dict
                    rel_counter += 1

            # relationship between Determiners/Adjectives: none is the "ruler" that determines the inflection
            if np_dict["TOK_info"][token1]["word_type"] in ["ART", "ADJA"] and np_dict["TOK_info"][token2]["word_type"] in ["ART", "ADJA"] and token1 != token2:

                if {token1, token2} not in all_relations:
                    rel_dict = build_relations_dict()
                    rel_dict["rel_type"] = "must_agree"
                    rel_dict["involved"] = [token1, token2]
                    rel_dict["ruler"] = None
                    np_dict["relations"]["rel_" + str(rel_counter)] = rel_dict
                    rel_counter += 1
                    all_relations.append({token1, token2})

        #relationship between APPRART (im, am, vom, ...) and tokens from NP
        for token2 in np_dict["HEAD_info"]["head"]:
            if np_dict["TOK_info"][token1]["word_type"] in ["N", "ART", "ADJA"] and np_dict["HEAD_info"]["head"][token2]["POS_STTS"] == "APPRART":

                rel_dict = build_relations_dict()
                rel_dict["rel_type"] = "must_agree"
                rel_dict["involved"] = [token1, token2]
                rel_dict["ruler"] = None
                if np_dict["TOK_info"][token1]["word_type"] == "N": rel_dict["ruler"] = token1
                np_dict["relations"]["rel_" + str(rel_counter)] = rel_dict
                rel_counter += 1
                all_relations.append({token1, token2})


    return np_dict


def add_split_verb_lemma(np_dict: dict) -> dict:
    """
    Add lemma_split_verb to a head if the verb has a verb particle
    :param np_dict: NP dictionary to add the info to
    :return: modified NP dictionary np_dict
    """

    for head in ["head", "super_head"]:
        for tok in np_dict["HEAD_info"][head]:
            if np_dict["HEAD_info"][head][tok]["POS_STTS"] == "PTKVZ":
                head_index = np_dict["HEAD_info"][head][tok]["head_index"]
                for tok2 in np_dict["HEAD_info"][head]:
                    if np_dict["HEAD_info"][head][tok2]["index"] == head_index:
                        np_dict["HEAD_info"][head][tok2]["lemma_split_verb"] = np_dict["HEAD_info"][head][tok]["lemma"]+np_dict["HEAD_info"][head][tok2]["lemma"]

    if np_dict["POST_info"]:
        for tok in np_dict["POST_info"]:
            if np_dict["POST_info"][tok]["POS_STTS"] == "PTKVZ":
                head_index = np_dict["POST_info"][tok]["head_index"]
                for tok2 in np_dict["POST_info"]:
                    if np_dict["POST_info"][tok2]["index"] == head_index:
                        np_dict["POST_info"][tok2]["lemma_split_verb"] = np_dict["POST_info"][tok]["lemma"] + \
                                                                               np_dict["POST_info"][tok2]["lemma"]

    return np_dict


def run_script(infile, outfile, corpusname):
    
    # read output file
    # open the file in read-mode
    try:
        with open(infile, 'r', encoding="utf-8") as f:
            # read in the lines of token
            text = ast.literal_eval(f.read().strip())
    except UnicodeDecodeError:
        with open(infile, 'r', encoding="utf-8-sig") as f: #utf-8-sig to avoid BOM error
            # read in the lines of token
            text = ast.literal_eval(f.read().strip())  #ast.literal_eval: interpret string as python list

    all_nps_infile = list()

    # iterate through sentences in output file
    for sent in text:

        # skip empty entries        
        if len(sent) > 0:

            # iterate through NPs in each sentence
            for np in sent:
            
                # initiate NP dict
                single_np_dict = build_np_dict()

                # get file & setence ID
                single_np_dict["file_ID"] = re.sub(".conll", "", np[1])
                single_np_dict["sent_NP_ID"] = np[0]
                single_np_dict["sentence"] = np[2]
                single_np_dict["metadata"]["corpus"] = corpusname


                # add token information, head information and must-agree-relations
                single_np_dict = add_TOK_info(single_np_dict, np)
                single_np_dict = add_HEAD_info(single_np_dict, np)
                single_np_dict = add_must_agree_relations(single_np_dict)
                single_np_dict = add_split_verb_lemma(single_np_dict)

                ### get len of NP/number of tokens (prenominal only) in NP
                single_np_dict["NP_info"]["len_np"] = len(single_np_dict["TOK_info"])

                # collect nps from single sentence
                all_nps_infile.append(single_np_dict)

    # add info about coordination
    all_nps_infile = add_coordination(all_nps_infile, text)

    # export to JSON
    json_format = json.dumps(all_nps_infile, indent=4, ensure_ascii=False)
    with open(outfile, mode="w", encoding="utf-8") as o:
        o.write(json_format)

    # output
    # pprint.pprint(all_nps_infile, sort_dicts=False)
                    


