import os, json, statistics, glob, tqdm
from tqdm.contrib.concurrent import process_map
from functools import partial
import pandas as pd
from collections import Counter

# function to convert a conllu-formatted file to countable lists
def convert_conllu(bibfile, misc="gloss=", trans=False):
    """
    bibfile: the path of the conllu-formatted file (Bible verses)
    misc: any miscellaneous information in field #10 that you wish to extract
    """
    # open the file and strip newlines
    with open(bibfile) as f:
        conllufile = f.readlines()
    conllufile = [x.strip() for x in conllufile]

    alines = [] # a list of all the lines
    tagged = [] # a list for tagging
    if trans==True:
        engtrans = {}
    # go through each line in the file
    for line in conllufile:
        # if this is the start of a new sentence, append the tagging list to the list of lines and reset the tagging list
        if "# sent_id" in line and tagged != []:
            alines.append(tagged)
            sentid = line.split(" = ")[-1]
            tagged = [sentid, []]
        elif "# sent_id" in line:
            sentid = line.split(" = ")[-1]
            tagged = [sentid, []]
        elif "# eng_text" in line and trans == True:
            engtrans[sentid] = line.split(" = ")[-1]
        # otherwise, if this is an annotated word line in a sentence, get the following info
        elif not "# " in line and line != '':
            linelist = line.split("\t") # split the line on tabs
            word = linelist[1] # the headword is at index 1
            pos = linelist[3] # the part of speech is at index 3
            deprel = linelist[7] # the dependency relation is at index 7
            # there is automated English glossing at index 9
            # (experimental) as well as some other stuff
            # in the "MISC" field - here we only get the info if it
            # has the tag matching what we set in the arguments above
            gloss = ""
            if len(linelist) > 9:
                gl = linelist[9].split("|")
                for anno in gl:
                    if misc in anno:
                        gloss = anno.replace(misc, "")
            
            tagged[1].append((word, pos, deprel, gloss)) # append this word-level info to the tagging list
    if trans==True:
        return alines, engtrans
    else:
        return alines

# function to get lengths of unique items
def get_ulen(nlist):
    lenslst = [len(n) for n in list(set(nlist))]
    return lenslst

# function to get lengths of all items (preserves freq)
def get_flen(llist):
    lenslist = [len(n) for n in llist]
    return lenslist

# function to get average of unique numbers in a list
def get_uavg(klist):
    try:
        average = statistics.mean(get_ulen(klist))
        return average
    except:
        return 0

# function to get average of numbers in a list (preserves freq)
def get_favg(ilist):
    try:
        avg = statistics.mean(get_flen(ilist))
        return avg
    except:
        return 0

# a function to get transitive word order information from a list of dependency-tagged text
def get_wordorders(iso, taggedbib, isodict, verses=False):
    """
    iso: the 3-letter code of the language (ISO 639-3)
    taggedbib: the list of dependency-tagged text for this language, derived from the `convert_conllu()` function
    isodict: a dictionary of word orders with iso codes as keys
    """

    # here we instantiate various dicts and lists to count things
    # one dict to store raw orders
    ordersdict = {"SOV": 0, "SVO": 0, "OSV": 0, "OVS": 0, "VOS": 0, "VSO": 0, "SO": 0, "OS": 0, "VS": 0, "SV": 0, "VO": 0, "OV": 0, 'errors': 0}
    # one dict to store N-initial/V-initial counts
    n1dict = {"N1": 0, "V1": 0, "N1_only": 0, "V1_only": 0}
    # track the actual verses with these orders
    vtracker = {"SOV": [], "SVO": [], "OSV": [], "OVS": [], "VOS": [], "VSO": [], "SO": [], "OS": [], "VS": [], "SV": [], "VO": [], "OV": [], 'errors': []}
    # errors = 0
    preds = ["VERB", "AUX"] # the set of POS tags to consider for predicates
    args = ["NOUN", "PRON", "PROPN"] # the set of POS tags to consider for arguments

    # instantiate lists for tracking items
    nouns, prons, propns, verbs, auxs, arguments, predicates = [], [], [], [], [], [], []

    # first we go through the tagged bible and count arguments/predicates
    # also appending them to lists to track their orders
    wordorders = []
    for sent in taggedbib:
        sentord = []
        # search through each word in each verse
        for words in sent[1]:
            # check if the word is tagged with a Noun/Argument POS tag
            if any(x in words[1] for x in args):
                sentord.append("N") # if so, append the token "N" to our word order list
                arguments.append(words[0]) # also add the word to our list of arguments
            # check if the word is tagged with a Verb/Predicate POS tag
            elif any(x in words[1] for x in preds):
                sentord.append("V") # if so, append the token "N" to our word order list
                predicates.append(words[0]) # also add the word to our list of predicates
        # add the order of N/Vs in the verse to our word order tracking list
        wordorders.append("_".join(sentord))
        # print(wordorders)

    # then we go through the list of lists and id the orders
    newordorders = [] # list to store orders
    for nv in wordorders:
        # check whether both N and V occur in the verse, only count orders for those that do
        if all(x in nv for x in ["N", "V"]):
            nvx = nv.strip()
            # if so, check which one occurs first
            if nvx[0] == "N":
                newordorders.append("N1")
            elif nvx[0] == "V":
                newordorders.append("V1")
            else:
                print(nvx)
                exit() # sanity check

    wordordercounts = Counter(newordorders) # count the number of N-first and V-first
    # print(f"Word orders for {iso}:", wordordercounts)
    for order, val in wordordercounts.items():
        n1dict[order] = val # add the counts to the dictionary

    # now go through each sentence in the tagged corpus again to track subject/object relations
    for sentence in taggedbib:
        # set each of these indices to None at the start
        subjind, objind, vind, argind, nind, vindo = None, None, None, None, None, None

        # for each of these conditions, update the relevant index
        # to reflect the first match
        for num, word in enumerate(sentence[1]):
            # check for subject dependencies
            if "subj" in word[2]:
                if not subjind:
                    subjind = num
            # check for object dependencies
            elif "obj" in word[2]:
                if not objind:
                    objind = num

        for num, word in enumerate(sentence[1]):
            # check for arguments
            if any(x in word[1] for x in args):
                # arguments.append(word[0])
                if not argind:
                    argind = num
                # track the actual items with noun/pron/propn pos
                if "NOUN" == word[1]:
                    nouns.append(word[0]) # add the item to our list of nouns
                    if not nind:
                        nind = num
                if "PRON" == word[1]:
                    prons.append(word[0]) # add the item to our list of pronouns
                if "PROPN" == word[1]:
                    propns.append(word[0]) # add the item to our list of proper nouns
            # check for predicates
            if any(x in word[1] for x in preds):
                # predicates.append(word[0])
                if not vind:
                    vind = num
                # track the actual items with verb/aux pos
                if "VERB" == word[1]:
                    if not vindo:
                        vindo = num
                    verbs.append(word[0]) # add the item to our list of verbs
                if "AUX" == word[1]:
                    auxs.append(word[0]) # add the item to our list of auxiliaries
        
        # now go through indices for subject, object, and verb for this sentence
        # if all three indices have been updated, add to the respective
        # order in our dictionary of counts
        if all(v is not None for v in [subjind, objind, vind]):
            if subjind < objind < vind:
                ordersdict["SOV"] += 1
                vtracker["SOV"].append(sentence[0])
            elif subjind < vind < objind:
                ordersdict["SVO"] += 1
                vtracker["SVO"].append(sentence[0])
            elif objind < subjind < vind:
                ordersdict["OSV"] += 1
                vtracker["OSV"].append(sentence[0])
            elif objind < vind < subjind:
                ordersdict["OVS"] += 1
                vtracker["OVS"].append(sentence[0])
            elif vind < subjind < objind:
                ordersdict["VSO"] += 1
                vtracker["VSO"].append(sentence[0])
            elif vind < objind < subjind:
                ordersdict["VOS"] += 1
                vtracker["VOS"].append(sentence[0])

        # if only two indices have been updated, make the relevant
        # dictionary updates
        else:
            if all(v is not None for v in [subjind, objind]):
                if subjind < objind:
                    ordersdict["SO"] += 1
                    vtracker["SO"].append(sentence[0])
                elif objind < subjind:
                    ordersdict["OS"] += 1
                    vtracker["OS"].append(sentence[0])
            elif all(v is not None for v in [subjind, vind]):
                if subjind < vind:
                    ordersdict["SV"] += 1
                    vtracker["SV"].append(sentence[0])
                elif vind < subjind:
                    ordersdict["VS"] += 1
                    vtracker["VS"].append(sentence[0])
            elif all(v is not None for v in [objind, vind]):
                if objind < vind:
                    ordersdict["OV"] += 1
                    vtracker["OV"].append(sentence[0])
                elif vind < objind:
                    ordersdict["VO"] += 1
                    vtracker["VO"].append(sentence[0])
            # if there's only one index updated, don't count it
            else:
                ordersdict["errors"] += 1
                vtracker["errors"].append(sentence[0])

        # now see if the POS tag indices were updated, and
        # if so, check which one occurs first and count it
        # in our N1 dictionary
        if all(v is not None for v in [vindo, nind]):
            if vindo < nind:
                n1dict["V1_only"] += 1
            elif nind < vindo:
                n1dict["N1_only"] += 1

    # here we count various things and store values in a dict
    lengthsdict = {"Verse_counts": len(taggedbib), "Ns_count": len(get_ulen(nouns)), 
                    "Vs_count": len(get_ulen(verbs)), "Prons_count": len(get_ulen(prons)), 
                    "Propns_count": len(get_ulen(propns)), "Auxs_count": len(get_ulen(auxs)), 
                    "Args_count": len(get_ulen(arguments)), "Preds_count": len(get_ulen(predicates)), 
                    "Nlen": get_uavg(nouns), "Pronlen": get_uavg(prons), "Propnlen": get_uavg(propns), 
                    "Vlen": get_uavg(verbs), "Auxlen": get_uavg(auxs), "Arglen": get_uavg(arguments), 
                    "Predlen": get_uavg(predicates), "Nlen_freq": get_favg(nouns), 
                    "Pronlen_freq": get_favg(prons), "Propnlen_freq": get_favg(propns), 
                    "Vlen_freq": get_favg(verbs), "Auxlen_freq": get_favg(auxs), 
                    "Arglen_freq": get_favg(arguments), "Predlen_freq": get_favg(predicates)}

    # here we get the totals for all verses with 3 elements (the 6 transitive word orders)
    sums3 = sum([v for k, v in ordersdict.items() if len(k) > 2 if "V" in k])
    # here we get the totals for all verses with 2 elements that contain a V (intransitive word orders)
    sums2 = sum([v for k, v in ordersdict.items() if len(k) < 3 if "V" in k])
    # now create proportions based on these values and add them to new dicts
    vecdict = {k+"_prop": v/sums3 for k, v in ordersdict.items() if len(k) > 2 if "V" in k}
    vecdict2 = {k+"_prop": v/sums2 for k, v in ordersdict.items() if len(k) < 3 if "V" in k}
    # and add these key: value pairs to our main dict
    for k, v in vecdict.items():
        ordersdict[k] = v
    for k, v in vecdict2.items():
        ordersdict[k] = v
    
    # now add VI, VM, VF
    n1dict["VI"] = sum([ordersdict["VOS"], ordersdict["VSO"]])
    n1dict["VM"] = sum([ordersdict["SVO"], ordersdict["OVS"]])
    n1dict["VF"] = sum([ordersdict["SOV"], ordersdict["OSV"]])
    # now add the N1 ratio
    n1dict["N1_ratio"] = n1dict["N1"]/n1dict["V1"]
    n1dict["N1ratio-ArgsPreds"] = n1dict["N1"]/n1dict["V1"]
    n1dict["N1ratio-NsVs"] = n1dict["N1_only"]/n1dict["V1_only"]
    # and add ratios for the 3 verb positions (verbpos/others)
    n1dict["VI_ratio"] = n1dict["VI"]/sum([n1dict["VM"], n1dict["VF"]])
    n1dict["VM_ratio"] = n1dict["VM"]/sum([n1dict["VI"], n1dict["VF"]])
    n1dict["VF_ratio"] = n1dict["VF"]/sum([n1dict["VI"], n1dict["VM"]])
    # and add proportions for the 3 verb positions
    n1dict["VI_prop"] = n1dict["VI"]/sums3
    n1dict["VM_prop"] = n1dict["VM"]/sums3
    n1dict["VF_prop"] = n1dict["VF"]/sums3

    # now add all the counted items, ratios, and proportions to our main isodict
    for k, v in lengthsdict.items():
        isodict[iso][k] = v
    for k, v in ordersdict.items():
        isodict[iso][k] = v
    for k, v in n1dict.items():
        isodict[iso][k] = v

    if verses == True:
        isodict[iso]['tracked_sents'] = {}
        for k, v in vtracker.items():
            isodict[iso]['tracked_sents'][k] = v

    return isodict

# function to get the iso and counts from the corpora as a list
# to pass through the processor
def get_isodict(bibfile):
    """
    bibfile: CoNLL-U formatted file with the first 3 characters being the ISO 639-3 code
    """
    isodict = {}
    iso = bibfile.split("/")[-1].split("-")[0] # get the iso code

    isodict[iso] = {} # make a new embedded dictionary in our main file

    taggedbib = convert_conllu(bibfile) # run the function to get our list of tagged data

    isodict = get_wordorders(iso, taggedbib, isodict) # count the words/relations

    return [iso, isodict[iso]]

# a function to run the other functions and write to a spreadsheet
# using tqdm.process_map for faster execution
def get_orders_from_conllu(outfile, fileslist, workers):

    values = process_map(get_isodict, fileslist, max_workers=workers, chunksize=1)
    
    isodict = {k[0]: k[1] for k in values}
    df = pd.DataFrame.from_dict(isodict, orient='index').reset_index() # convert to dataframe

    return df
