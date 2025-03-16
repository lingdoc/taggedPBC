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
