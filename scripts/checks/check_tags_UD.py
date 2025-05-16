import json, string
import tqdm
import pandas as pd

# add some additional characters to the standard punctuation
punct = string.punctuation+"“”‘’,"

# function to get ratios of shared nouns/verbs between languages in the UDT and the PBC
def get_langratios(sharedlangs, udlangsf, taggedfiles):
    dfdict = {}

    for sl in tqdm.tqdm(sharedlangs):
        # go through each UDT dataset shared with PBC
        source_lang = sl
        # get the tagged file (the UDT data has previously been converted to a single file of POS-tagged text per language)
        taggedsourcefile = [x for x in udlangsf if sl in x][0]
        # open the file
        with open(taggedsourcefile) as s:
            source = json.load(s)
        # id the number of sentences contained in the treebank
        print(f"Number of sentences in UD -{sl}- treebank:", len(source))

        # only check languages where there are at least 200 sentences in the treebank
        if len(source) > 200:
            # now get the corresponding tagged file from the PBC
            trainfile = taggedfiles[sl]
            with open(trainfile) as s:
                taggedcorp = json.load(s)

            allwordsbib = []
            # create a single list of all the tagged words in (word, pos) format
            for sent in taggedcorp:
                tagged = sent[1]
                if len(tagged) > 0:
                    words = []
                    for wd in tagged:
                        if wd[0] in punct:
                            words.append((wd[0], 'PUNCT'))
                        else:
                            words.append((wd[0].lower(), wd[1]))
                    allwordsbib += words

            nslist = ["NOUN", "PROPN", "PRON"] # all arguments
            onlist = ["NOUN"] # only nouns
            proplist = ["PROPN"] # only proper nouns
            pronlist = ["PRON"] # only pronouns
            vslist = ["VERB", "AUX"] # all predicates
            ovlist = ["VERB"] # only verbs
            auxlist = ["AUX"] # only auxiliaries

            # filter out unknown words
            allwordsbib = [x for x in allwordsbib if x[1] != 'unk']
            print(len(allwordsbib))
            # create a list of arguments
            nsbib = [x for x in list(set(allwordsbib)) if any(wd in x[1] for wd in nslist)]
            bibns = len(nsbib)
            # create a list of predicates
            vsbib = [x for x in list(set(allwordsbib)) if any(wd in x[1] for wd in vslist)]
            bibvs = len(vsbib)

            finalcorp = []
            testcorp = []
            allwordstest = []
            # create a list of words for the UDT texts
            for sent in source:
                finalcorp.append([x[0].lower() for x in sent])
                words = []
                for wd in sent:
                    words.append((wd[0].lower(), wd[1]))
                testcorp.append(words)
                allwordstest += words

            allwordstest = [x for x in allwordstest if x[1] != 'unk']
            print(len(allwordstest))
            nstest = [x for x in list(set(allwordstest)) if any(wd in x[1] for wd in nslist)]
            udnouns = len(nstest)
            vstest = [x for x in list(set(allwordstest)) if any(wd in x[1] for wd in vslist)]
            udverbs = len(vstest)

            # get the intersection of the two lists (matches on both word and pos)
            sharednouns = list(set(nstest).intersection(set(nsbib)))
            sharedns = len(sharednouns)
            sharedverbs = list(set(vstest).intersection(set(vsbib)))
            sharedvs = len(sharedverbs)
            print("number of shared nouns:", sharedns)
            print("number of shared verbs:", sharedvs)

            dfdict[sl] = {"ISO": sl, "UD verbs": udverbs, "UD nouns": udnouns, "Bib verbs": bibvs, "Bib nouns": bibns, "Shared nouns": sharedns, "Shared verbs": sharedvs, "Arguments": str(sharednouns), "Predicates": str(sharedverbs)}
            #, "Only nouns": corronlyns, "Only propns": corronlypropns, "Only prons": corronlyprons, "Only verbs": corronlyvs, "Only auxs": corronlyauxs} , "Ratio of corresponding nouns": corrns, "Ratio of corresponding verbs": corrvs

    df = pd.DataFrame.from_dict(dfdict, orient='index')

    return df
