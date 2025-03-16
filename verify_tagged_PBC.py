import os, glob
import pandas as pd

# the following code checks how well the POS tags in the tagged PBC correspond
# to tags from SpaCy taggers for various languages
taggedfiles = "data/tagged/" # folder containing the tagged PBC data
# get the list of files and languages in the tagged PBC
taggedlangs = [x.split("/")[-1].split("-")[0] for x in glob.glob(taggedfiles+"*.json")]

# check first for an existing analysis file (delete this if you want to re-run the analysis)
outputfile = "checks/results/Spacy_correspondences.xlsx" # path to the analysis file
if not os.path.isfile(outputfile):
    # we do imports here to avoid having to install too many modules if the analysis file exists
    import checks.check_tags_spacy
    from checks.check_tags_spacy import *
    # file containing the list of SpaCy language models (languages with non-roman scripts removed)
    splangfile = "checks/tag_models/spacy_models.xlsx"
    spdf = pd.read_excel(splangfile)
    # print(spdf.columns)
    splangs = spdf.set_index('ISO 639-3').T.to_dict('list')

    sharedlangs = []

    for l in splangs.keys():
        if splangs[l][4] == "yes":
            if l in taggedlangs:
                if l != 'eng':
                    sharedlangs.append(l)
    print(len(sharedlangs)) # the number of languages shared between the tagged PBC and SpaCy

    df = get_langratios(sharedlangs, taggedfiles, splangs) # get correspondences and store in dataframe
    print(df.head())
    df.to_excel(outputfile)

df = pd.read_excel(outputfile)
# print out some info
print("There are {langs} languages shared between the PBC and SpaCy".format(langs=len(df)))
print("The avg correspondence with arguments in SpaCy is {nouns}".format(nouns=df['Ratio of corresponding nouns'].mean()))
print("The avg correspondence with predicates in SpaCy is {verbs}".format(verbs=df['Ratio of corresponding verbs'].mean()))

# the following code checks how well the POS tags in the tagged PBC correspond
# to tags from Trankit taggers for various languages

# check first for an existing analysis file (delete this if you want to re-run the analysis)
outputfile = "checks/results/Trankit_correspondences.xlsx" # path to the analysis file
if not os.path.isfile(outputfile):
    # do imports here to avoid having to install additional modules if the analysis file exists
    import checks.check_tags_trankit
    from checks.check_tags_trankit import *
    trlangfile = "checks/tag_models/trankit_models.xlsx" # file with a list of Trankit models (non-roman scripts removed)
    trdf = pd.read_excel(trlangfile)
    print(trdf.columns)
    trlangs = trdf.set_index('ISO 639-3').T.to_dict('list')

    sharedlangs = []

    for l in trlangs.keys():
        if trlangs[l][6] == "yes":
            if l in taggedlangs:
                if l != 'eng':
                    sharedlangs.append(l)
    print(len(sharedlangs)) # the number of languages shared between the tagged PBC and Trankit

    df = get_langratios(sharedlangs, taggedfiles, trlangs, '../cacheTrankit/') # get correspondences and store in dataframe
    print(df.head())
    df.to_excel(outputfile)

df = pd.read_excel(outputfile)
# print some info
print("There are {langs} languages shared between the PBC and Trankit".format(langs=len(df)))
print("The avg correspondence with arguments in Trankit is {nouns}".format(nouns=df['Ratio of corresponding nouns'].mean()))
print("The avg correspondence with predicates in Trankit is {verbs}".format(verbs=df['Ratio of corresponding verbs'].mean()))

# The following code checks how many of the words in the tagged PBC have exact form/tag matches
# in the UDT dataset (for languages in the UDT with at least 200 sentences). An analysis file
# with correspondences is included here - if you want to re-run these analyses you will need
# to have downloaded the UDT (version 2.14) and taken additional pre-processing steps. Code
# for handling this can be found in the `processing` folder.
import checks.check_tags_UD
from checks.check_tags_UD import *

# check first for an existing analysis file (delete this if you want to re-run the analysis)
outputfile = "checks/results/UD_correspondences.xlsx"
if not os.path.isfile(outputfile):
    udfiles = "../ud-2.14/iso-tagged/" # the location of the processed UDT datasets
    udlangsf = [x for x in glob.glob(udfiles+"*.txt")]
    udlangs = [x.split("/")[-1].split("_")[0] for x in udlangsf]
    print(len(udlangs))

    ibtag = "data/tagged/" # location of the taggedPBC corpus
    ibtags = [x for x in glob.glob(ibtag+"*.json")]
    print(len(ibtags))

    sharedlangs = []

    for l in udlangs:
        if l in [x.split("/")[-1].split("-")[0] for x in ibtags]:
            sharedlangs.append(l)
    print(len(list(set(sharedlangs)))) # the number of languages shared between the tagged PBC and the UDT

    taggedfiles = {}

    for l in sharedlangs:
        tagl = [x for x in ibtags if x.split("/")[-1].split("-")[0] == l][0]
        taggedfiles[l] = tagl

    df = get_langratios(sharedlangs, udlangsf, taggedfiles) # get correspondences and store in dataframe

    print(df.head())
    df.to_excel(outputfile)

df = pd.read_excel(outputfile)
print("There are {langs} languages shared between the PBC and UDT 2.14".format(langs=len(df)))
print("The avg number of shared nouns with UD is {nouns}".format(nouns=df['Shared nouns'].mean()))
print("The avg number of shared verbs with UD is {verbs}".format(verbs=df['Shared verbs'].mean()))

# the code below combines all the word order observations from the three typological
# first get the language stats from the tagged PBC (N1 ratio, number/length of nouns/verbs etc)
main = pd.read_excel("data/output/stats_All.xlsx", index_col=0).to_dict('index')

print(len(main)) # check the number of languages

# select the datasets with word order info
datasets = ['wals_word_order.xlsx', 'grambank_word_order.xlsx', 'autotyp_word_order.xlsx',]
datasets = ['data/word_order/'+x for x in datasets]

newdf = pd.DataFrame() # instantiate a new df to store info

# go through each of the typological databases
for data in datasets:
    df = pd.read_excel(data, index_col=3)
    if "grambank" in data:
        df = df[df['Intrans_Order'] != "UNK"] # remove languages with "UNK" word order
    datadict = df.to_dict('index')
    print(len(datadict))

    combinedkeys = list(main.keys() & datadict.keys())
    print(len(combinedkeys))

    combineds = {k: main[k] for k in combinedkeys}

    for k in combinedkeys:
        for v, vals in datadict[k].items():
            combineds[k][v] = vals

    print(len(combineds)) # total number of languages that occur in PBC and databases

    df = pd.DataFrame.from_dict(combineds, orient='index')
    df.reset_index()

    # do some conversions to match coding between databases
    if "auto" in data:
        rpldict = {"V=1": "VS", "V=3": "SV", "V=2": "SV"}
        df['Noun_Verb_order'] = df['PositionVBasicLex'].replace(rpldict)
        df.to_excel("data/output/comparisons_Autotyp.xlsx")
    elif "wals" in data:
        rpldict = {"No dominant order": "free"}#, 'SV': 'N1', 'VS': 'V1'}
        df['Noun_Verb_order'] = df['Order of Subject and Verb'].replace(rpldict)
        df.to_excel("data/output/comparisons_WALS.xlsx")
    elif "grambank" in data:
        # rpldict = {"VS": "V1", "SV": "N1"}
        df['Noun_Verb_order'] = df['Intrans_Order']#.replace(rpldict)
        df = df[df['Noun_Verb_order'] != "UNK"] # remove languages with "UNK" word order
        df.to_excel("data/output/comparisons_Grambank.xlsx")
    print(df.head())
    # print(df.columns)
    print(len(df))
    newdf = pd.concat([newdf, df])

newdf = newdf.reset_index()
newdf = newdf[newdf['Noun_Verb_order'] != 'UNK'] # remove languages with "UNK" word order
newdf = newdf.drop_duplicates(subset=['index'], keep='first') # remove duplicated classifications

newdf.to_excel("data/output/All_comparisons.xlsx", index=False)

# the following code computes statistics for the N1 ratio and word order classifications in
# three typological databases: Grambank, WALS, and Autotyp
import analysis.anovas
from analysis.anovas import *

# check the comparisons between the N1 ratio and word order values in the three databases
datasets = ['comparisons_Grambank.xlsx', 'comparisons_WALS.xlsx', 'comparisons_Autotyp.xlsx',]
datasets = ['data/output/'+x for x in datasets]

for nfile in datasets:
    outfold = "data/output/plots_wdorder/"
    ds = nfile.split("_")[-1][:-5]

    print(nfile)
    df = pd.read_excel(nfile)
    df['index'] = df.index
    repldict = {'N1': 'SV', 'V1': 'VS'}
    df['Noun_Verb_order'] = df['Noun_Verb_order'].replace(repldict)

    subj = 'index'
    betw = 'Noun_Verb_order'
    within = 'N1ratio-ArgsPreds'
    get_anova_wordorder(df, subj, betw, within, outfold, ds)

# the anovas show a significant correlation between intransitive word order and the N1 ratio
# the difference in means is also visible in the plots

# now that we have combined all the data from the different databases we can
# proceed to impute the data for all languages in the tagged PBC which have not
# been coded for word order, using the N1 ratio as the feature for classification

import analysis.train_classifiers
from analysis.train_classifiers import *

# we could use this dict to test multiple classifiers, but
# in our case the data is normally distributed so we use GNB
classifiers = {
                "GNB": GaussianNB(),
                }
# import dataset
filen = "data/output/All_comparisons.xlsx" # path to isos in databases where word order has been coded
original = "data/output/stats_All.xlsx" # get isos from the tagged PBC stats
result = test_classifier_on_df(filen, classifiers, original)

result.to_excel("data/output/All_comparisons_imputed.xlsx", index=False)
