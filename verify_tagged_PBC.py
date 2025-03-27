import os, glob
import pandas as pd

## the following code checks how well the POS tags in the tagged PBC correspond
## to tags from SpaCy taggers for various languages
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

## the following code checks how well the POS tags in the tagged PBC correspond
## to tags from Trankit taggers for various languages

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

## The following code checks how many of the words in the tagged PBC have exact form/tag matches
## in the UDT dataset (for languages in the UDT with at least 200 sentences). An analysis file
## with correspondences is included here - if you want to re-run these analyses you will need
## to have downloaded the UDT (version 2.14) and taken additional pre-processing steps. Code
## for handling this can be found in the `processing` folder.
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

## the code below combines all the word order observations from the three typological databases
## first get the language stats from the tagged PBC (N1 ratio, number/length of nouns/verbs etc)
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

## the following code computes statistics for the N1 ratio and word order classifications in
## three typological databases: Grambank, WALS, and Autotyp
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

## the anovas show a significant correlation between intransitive word order and the N1 ratio
## the difference in means is also visible in the plots

## now that we have combined all the data from the different databases we can
## proceed to impute the data for all languages in the tagged PBC which have not
## been coded for word order, using the N1 ratio as the feature for classification

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


## Now let's see how well the measurements of noun and verb lengths can differentiate between
## a modern language and a historical language with different word orders.

import checks.test_hbo_heb.classify_lgs
from checks.test_hbo_heb.classify_lgs import *

# import dataset of word order comparisons (doesn't affect outcome)
# data = "data/output/All_comparisons_imputed.xlsx" # including all languages from the tagged PBC
data = "data/output/All_comparisons.xlsx" # only languages from typological databases

# convert the data into the correct format
X, y = get_train_data(data)
# create a dictionary of classifiers for testing multiple
classifiers = {"GNB": GaussianNB(),}
# train/test to assess accuracy
for clf in classifiers.keys():
    test_clf(X, y, preprocessor, classifiers[clf], clf)

# import stats on nouns/verbs from POS-tagged corpora of Ancient and Modern Hebrew
# via UD 2.14 (see `checks/test_hbo_heb/check_UD.py` for more detail)
udstats = "checks/test_hbo_heb/UD_stats.xlsx"
# get the data for prediction
df = get_predict_data(udstats)
# train on the training data and predict on the unseen data
df = train_predict(df, classifiers, X, y)
# write the results to a file
df.to_excel("checks/test_hbo_heb/word_order_hbo_heb.xlsx", index=False)


## Finally, we can conduct a hierarchical linear regression to assess whether noun/verb lengths
## allow for better prediction than descent from a common ancestor language, attempting to 
## replicate Dunn et al 2011.

import checks.hierlinreg
from checks.hierlinreg import *

famfile = "checks/glottolog/All_comparisons_imputed_families.xlsx" # the file where we add family info from Glottolog
complete = "data/output/All_comparisons_imputed.xlsx" # the file with all word orders for the taggedPBC

# check if the file with families exists
if not os.path.isfile(famfile):
    linfile = "checks/glottolog/lineages.json" # the lineages and ISO codes from Glottolog, stored in json format
    get_families(famfile, complete, linfile)

dunnfile = "checks/glottolog/Dunn_isos.xlsx" # this file contains the ISO codes and families of the languages from the Dunn et al paper
dunn = pd.read_excel(dunnfile) # read in the file

# These are the actual languages (ISO codes) from the Dunn et al paper. Some of these were split into separate
# Glottocodes (under a single ISO code), but the PBC only has ISO codes, so we end up with fewer.
dunnlist = dunn['ISO639_3'].to_list()
print("Number of languages investigated by Dunn et al:", len(dunnlist))
print(dunn['Family'].value_counts()) # these are the number of languages per family in the Dunn et al paper
print(list(dunn['Family'].value_counts().keys())) # these are the language families in the Dunn et al paper
# we could replace 'Bantu' with 'Atlantic-Congo', which is the top-level language family
# but let's be a bit more selective and choose 'Narrow Bantu' (Glottocode 'narr1281')
# for this we will need to import another file which contains languages with that classification
dunnfams = ['Narrow Bantu', 'Austronesian', 'Indo-European', 'Uto-Aztecan']
with open("checks/glottolog/NarrowBantu-narr1281.json") as f:
    bantu = json.load(f) # load the list with ISO codes of 'Narrow Bantu' lgs from Glottolog, stored in json format

# read in the dataset with families from Glottolog
df = pd.read_excel(famfile)
df['index'] = df['index'].fillna('nan') # when pandas imports the spreadsheet it thinks this ISO code is NaN
# print(df.head())

# remove 'free' languages from the dataset to allow for binary DV
df = df[~df["Noun_Verb_order"].str.contains('free')]
print("Number of languages in the taggedPBC with SV/VS orders:", len(df))

famlist = filter_families(df, dunnfams) # these are families in the taggedPBC and the Dunn et al paper (Bantu is subsumed by 'Atlantic-Congo')
lgls1 = df[df['index'].isin(dunnlist)] # these are languages in the taggedPBC which are in the Dunn et al paper
print("Number of languages in the taggedPBC shared with Dunn et al:", len(lgls1))
famlist = famlist+bantu # add the 'Narrow Bantu' languages
lglist = filter_lgs(df, famlist) # these are languages in the taggedPBC which are in the families from the Dunn et al paper
print("Number of languages in the taggedPBC shared with the families investigated by Dunn et al:", len(lglist))
lnum = 80
famlistcount = filter_lgs(df, filter_families(df, lnum))
print("Number of languages in the taggedPBC in families with more than {num} members: {famc}".format(num=lnum, famc=len(famlistcount)))
cnum = 1
famlistcount2 = filter_lgs(df, filter_families(df, cnum))
print("Number of languages in the taggedPBC in families with more than {num} members: {famc}".format(num=cnum, famc=len(famlistcount2)))
dnum = 0
famlistcount3 = filter_lgs(df, filter_families(df, dnum))
print("All languages in the taggedPBC including isolates: {famc}".format(famc=len(famlistcount3)))

fit_transform_cats(df, 'Noun_Verb_order', 'Class') # convert the SV/VS classes to binary
fit_transform_cats(df, 'Family_line', 'Fam_class') # convert the language family to numeric

# Define the models for hierarchical regression including predictors for each model
X = {
     1: ['N1ratio-ArgsPreds'], # variable known to differentiate word order between languages
     2: ['N1ratio-ArgsPreds', 'Nlen_freq', 'Vlen_freq'], # include Nlen/Vlen
     3: ['N1ratio-ArgsPreds', 'Nlen_freq', 'Vlen_freq', 'Fam_class'], # include family
     }

# Define the outcome variable
y = 'Class' # SV/VS

# set up a series of lists to check using HLR models
checklists = [
               (dunnlist, "Dunn_lgs"), # the languages common to the taggedPBC and Dunn et al
               (lglist, "Dunn_fams"), # languages in the taggedPBC from the families investigated by Dunn et al
               (famlistcount, ">{lnum}_lg_families".format(lnum=lnum)), # languages in the taggedPBC from families with a large number of members
               (famlistcount2, ">{lnum}_lg_families".format(lnum=cnum)), # languages from families with 2+ members in the taggedPBC
               (famlistcount3, "All_lg_families".format()), # all languages in the taggedPBC
               ]

# go through each list and run the HLR models
for num, check in enumerate(checklists):
     temp = df[df['index'].isin(check[0])]
     run_HLR(temp, X, y, str(num+1)+"_"+check[1], "checks/results/")

## Based on this analysis, Noun/Verb lengths are a stronger predictor of word order
## than descent from a common ancestor (family membership).