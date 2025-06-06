import os, json, statistics, glob, tqdm
import pandas as pd
from collections import Counter

# function to get word orders from a sentence/verse
def get_orders(nslist, vslist, taggedbib, isodict, iso, nfcol, vfcol, nlcol, vlcol, nlfcol, vlfcol, term, too_few):
    """
    nslist: the list of POS tags corresponding to Nouns/Arguments
    vslist: the list of POS tags corresponding to Verbs/Predicates
    taggedbib: the POS-tagged Bible corpus
    isodict: the dictionary of ISO 639-3 codes
    iso: the ISO 639-3 code of the current Bible translation

    nfcol, vfcol, nlcol, vlcol, nlfcol, vlfcol: dataframe columns corresponding to noun/verb first counts
                                                and noun/verb average lengths, as well as counts of actual
                                                nouns/verbs

    """

    nouns = [] # list to track nouns
    verbs = [] # list to track verbs
    wordorders = [] # list to track word orders

    # print(len(taggedbib))
    # each sentence in the tagged bible contains a verse number followed by the POS-tagged verse
    for sent in taggedbib:
        sentord = []
        # search through each word in each verse
        for words in sent[1]:
            # check if the word is tagged with a Noun/Argument POS tag
            if any(x in words[1] for x in nslist):
                sentord.append("N") # if so, append the token "N" to our word order list
                nouns.append(words[0]) # also add the word to our list of nouns
            # check if the word is tagged with a Verb/Predicate POS tag
            elif any(x in words[1] for x in vslist):
                sentord.append("V") # if so, append the token "N" to our word order list
                verbs.append(words[0]) # also add the word to our list of verbs
        # add the order of N/Vs in the verse to our word order tracking list
        wordorders.append("_".join(sentord))
        # print(wordorders)

    newordorders = [] # list to store orders
    for nv in wordorders:
        # check whether both N and V occur in the verse
        if all(x in nv for x in ["N", "V"]):
            nvx = nv.strip()
            # if so, check which one occurs first
            if nvx[0] == "N":
                newordorders.append(nfcol)
            elif nvx[0] == "V":
                newordorders.append(vfcol)
            else:
                print(nvx)
                exit() # sanity check

    wordordercounts = Counter(newordorders) # count the number of N-first and V-first
    # print(f"Word orders for {iso}:", wordordercounts)
    for order, val in wordordercounts.items():
        isodict[iso][order] = val # add the counts to the dictionary

    # count the arguments/predicates and get basic stats
    setnouns = list(set(nouns))
    nounnums = len(setnouns)
    if nslist != ["PRON"]:
        if nounnums < 100:
            too_few.append(iso)
    if term == "_all":
        isodict[iso]['Args_count'] = nounnums
    elif term == "_only":
        isodict[iso]['Ns_count'] = nounnums
    avglennouns = statistics.mean([len(x) for x in setnouns])
    avglenfreqnouns = statistics.mean([len(x) for x in nouns])
    isodict[iso][nlcol] = avglennouns
    isodict[iso][nlfcol] = avglenfreqnouns
    # are there any languages with noun lengths longer than 14 chars?
    if avglennouns > 14:
        print(f"Avg noun lengths for {iso}:", avglennouns)
        # print(f"Number of nouns for {iso}:", nounnums)
        # print(f"Avg noun (freq) lengths for {iso}:", avglenfreqnouns)
        # print(f"Number of total nouns for {iso}:", len(nouns))

    setverbs = list(set(verbs))
    verbnums = len(setverbs)
    # there is one language with fewer than 100 unique verbs
    if verbnums < 100:
        too_few.append(iso)
    if term == "_all":
        isodict[iso]['Preds_count'] = verbnums
    elif term == "_only":
        isodict[iso]['Vs_count'] = verbnums
    avglenverbs = statistics.mean([len(x) for x in setverbs])
    avglenfreqverbs = statistics.mean([len(x) for x in verbs])
    isodict[iso][vlcol] = avglenverbs
    isodict[iso][vlfcol] = avglenfreqverbs
    # are there any languages with verb lengths longer than 14 chars?
    if avglenverbs > 14:
        print(f"Avg verb lengths for {iso}:", avglenverbs)
        # print(f"Number of verbs for {iso}:", verbnums)
        # print(f"Avg verb (freq) lengths for {iso}:", avglenfreqverbs)
        # print(f"Number of total verbs for {iso}:", len(verbs))

    return isodict

# function to get all tagged data from a list of JSON files
def get_df_from_tagged(fileslist, too_few):
    isodict = {}

    for bibfile in tqdm.tqdm(fileslist):
        # print(bibfile)
        iso = bibfile.split("/")[-1].split("-")[0]

        isodict[iso] = {}

        with open(bibfile) as f:
            taggedbib = json.load(f)
        taggedbib = taggedbib['tagged'] # tagged Bible portion is the list stored as the `tagged` key

        # get the total number of verses in each corpus
        isodict[iso]["Verse_counts"] = len(taggedbib)
        
        # these are the POS tags that we are tracking
        nounsonly = ["NOUN"] # only nouns treated as arguments
        pronsonly = ["PRON"] # only pronouns treated as arguments
        # nounsprop = ["NOUN", "PROPN"] # nouns and proper nouns treated as arguments (not used for analysis)
        # nounspron = ["NOUN", "PRON"] # nouns and pronouns treated as arguments (not used for analysis)
        nounspropro = ["NOUN", "PROPN", "PRON"] # nouns and proper nouns and pronouns treated as arguments
        verbsonly = ["VERB"] # only verbs treated as predicates
        verbaux = ["VERB", "AUX"] # verbs and auxiliaries treated as predicates

        # here we get the word orders in sentences, tracking only Nouns and Verbs
        isodict = get_orders(nounsonly, verbsonly, taggedbib, isodict, iso, "N1counts-Ns", "V1counts-Vs", "Nlen", "Vlen", "Nlen_freq", "Vlen_freq", "_only", too_few)
        # here we get the word orders in sentences, tracking only Pronouns and Verbs
        isodict = get_orders(pronsonly, verbsonly, taggedbib, isodict, iso, "N1counts-Prons", "V1counts-Vs", "Pronlen", "Vlen", "Pronlen_freq", "Vlen_freq", "_only", too_few)
        # here we get the word orders in sentences, tracking all arguments and predicates
        isodict = get_orders(nounspropro, verbaux, taggedbib, isodict, iso, "N1counts-Args", "V1counts-Preds", "Arglen", "Predlen", "Arglen_freq", "Predlen_freq", "_all", too_few)

    # create a dataframe
    df = pd.DataFrame.from_dict(isodict, orient='index').reset_index()

    # compute the N1 ratios
    df["N1ratio-NsVs"] = df["N1counts-Ns"]/df["V1counts-Vs"]
    df["N1ratio-ArgsPreds"] = df["N1counts-Args"]/df["V1counts-Preds"]

    return df


# function to convert a conllu-formatted file to countable lists
def convert_conllu(bibfile):
    """
    bibfile: the path of the conllu-formatted file (Bible verses)
    """
    # open the file and strip newlines
    with open(bibfile) as f:
        conllufile = f.readlines()
    conllufile = [x.strip() for x in conllufile]

    alines = [] # a list of all the lines
    tagged = [] # a list for tagging
    # go through each line in the file
    for line in conllufile:
        # if this is the start of a new sentence, append the tagging list to the list of lines and reset the tagging list
        if "# sent_id" in line and tagged != []:
            alines.append(tagged)
            tagged = []
        # otherwise, if this is an annotated word line in a sentence, get the following info
        if not "#" in line and line != '':
            linelist = line.split("\t") # split the line on tabs
            word = linelist[1] # the headword is at index 1
            pos = linelist[3] # the part of speech is at index 3
            deprel = linelist[7] # the dependency relation is at index 7
            tagged.append((word, pos, deprel)) # append this word-level info to the tagging list

    return alines

# a function to get transitive word order information from a list of dependency-tagged text
def get_sovs(iso, taggedbib, isodict):
    """
    iso: the 3-letter code of the language (ISO 639-3)
    taggedbib: the list of dependency-tagged text for this language, derived from the `convert_conllu()` function
    isodict: a dictionary of word orders with iso codes as keys
    """

    # here we instantiate various dicts and lists to count things
    ordersdict = {"SOV": 0, "SVO": 0, "OSV": 0, "OVS": 0, "VOS": 0, "VSO": 0, "SO": 0, "OS": 0, "VS": 0, "SV": 0, "VO": 0, "OV": 0,}
    n1dict = {"N1": 0, "V1": 0}
    errors = 0
    verbs = ["VERB", "AUX"] # the set of POS tags to consider for predicates
    nouns = ["NOUN", "PRON", "PROPN"] # the set of POS tags to consider for arguments

    # go through each sentence in the tagged corpus
    for sentence in taggedbib:
        # set each of these indices to None at the start
        subjind = None
        objind = None
        vind = None
        argind = None

        # for each of these conditions, update the relevant index
        # to reflect the first match
        for num, word in enumerate(sentence):
            # check for subject dependencies
            if "subj" in word[2]:
                if not subjind:
                    subjind = num
            # check for object dependencies
            elif "obj" in word[2]:
                if not objind:
                    objind = num
            # check for verbs
            if any(x in word[1] for x in verbs):
                if not vind:
                    vind = num
            # check for nouns
            elif any(x in word[1] for x in nouns):
                if not argind:
                    argind = num
        
        # now go through our indices for subject, object, and verb
        # if all three indices have been updated, update the respective
        # order in our dictionary of counts
        if subjind and objind and vind:
            if subjind < objind < vind:
                ordersdict["SOV"] += 1
            elif subjind < vind < objind:
                ordersdict["SVO"] += 1
            elif objind < subjind < vind:
                ordersdict["OSV"] += 1
            elif objind < vind < subjind:
                ordersdict["OVS"] += 1
            elif vind < subjind < objind:
                ordersdict["VSO"] += 1
            elif vind < objind < subjind:
                ordersdict["VOS"] += 1
        # if only two indices have been updated, make the relevant
        # dictionary updates
        elif subjind and objind:
            if subjind < objind:
                ordersdict["SO"] += 1
            elif objind < subjind:
                ordersdict["OS"] += 1
        elif subjind and vind:
            if subjind < vind:
                ordersdict["SV"] += 1
            elif vind < subjind:
                ordersdict["VS"] += 1
        elif objind and vind:
            if objind < vind:
                ordersdict["OV"] += 1
            elif vind < objind:
                ordersdict["VO"] += 1
        # if there's only one index updated, don't count it
        else:
            errors += 1
        # now see if the POS tag indices were updated, and
        # if so, check which one occurs first and count it
        # in our N1 dictionary 
        if vind and argind:
            if vind < argind:
                n1dict["V1"] += 1
            else:
                n1dict["N1"] += 1

    # here we get the totals for all verses with 3 elements (the 6 transitive word orders)
    sums3 = sum([v for k, v in ordersdict.items() if len(k) > 2])
    # here we get the totals for all verses with 2 elements that contain a V
    sums2 = sum([v for k, v in ordersdict.items() if len(k) < 3 if "V" in k])
    # now create proportions based on these values and add them to new dicts
    vecdict = {k+"_prop": v/sums3 for k, v in ordersdict.items() if len(k) > 2}
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
    # and add ratios for the 3 verb positions (verbpos/others)
    n1dict["VI_ratio"] = n1dict["VI"]/sum([n1dict["VM"], n1dict["VF"]])
    n1dict["VM_ratio"] = n1dict["VM"]/sum([n1dict["VI"], n1dict["VF"]])
    n1dict["VF_ratio"] = n1dict["VF"]/sum([n1dict["VI"], n1dict["VM"]])
    # and add proportions for the 3 verb positions
    n1dict["VI_prop"] = n1dict["VI"]/sums3
    n1dict["VM_prop"] = n1dict["VM"]/sums3
    n1dict["VF_prop"] = n1dict["VF"]/sums3
    
    # now add all the counted items, ratios, and proportions to our main isodict
    for k, v in ordersdict.items():
        isodict[iso][k] = v
    for k, v in n1dict.items():
        isodict[iso][k] = v

    return isodict

# a function to run the other functions, get counts, and write to a spreadsheet
def get_orders_from_conllu(outfile, fileslist):
    isodict = {} # instantiate our dictionary
    
    # go through each conllu-formatted file in the list
    for bibfile in tqdm.tqdm(fileslist):
        # print(bibfile)
        iso = bibfile.split("/")[-1].split("-")[0] # get the iso code
        # print(iso)

        isodict[iso] = {} # make a new embedded dictionary in our main file

        taggedbib = convert_conllu(bibfile) # run the function to get our list of tagged data

        isodict = get_sovs(iso, taggedbib, isodict) # count the words/relations

    df = pd.DataFrame.from_dict(isodict, orient='index').reset_index() # convert to dataframe

    return df
