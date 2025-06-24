import os, glob
import pandas as pd

# let's run statistics to see how well word class length correlates with word order
import analysis.anovas
from analysis.anovas import *

# the code below assumes you have imputed word order values using the consolidated databases as a training set
filen = "data/output/All_comparisons_imputed.xlsx" # spreadsheet with all languages classified for "SV", "VS", "free" word order
outfold = "data/output/plots_means/" # output folder for the resulting datasheets and plots

try:
    df = pd.read_excel(filen)
except:
    print("The file `{filen}` does not exist. Run the `annotating_tagged_PBC.py` script to create it.".format(filen=filen))
    exit()

df['index'] = df.index

subj = 'index'
betw = 'Noun_Verb_order'
comparisons = [
                ['Nlen', 'Vlen'], ['Nlen_freq', 'Vlen_freq'],
                ['Arglen', 'Predlen'], ['Arglen_freq', 'Predlen_freq'],
                ['Pronlen', 'Vlen'], ['Pronlen_freq', 'Vlen_freq'],
                ['Nlen_freq', 'Nlen'], ['Vlen_freq', 'Vlen'],
                ['Arglen_freq', 'Arglen'], ['Predlen_freq', 'Predlen'],
                ['Pronlen_freq', 'Pronlen'],
                ]

# conduct the repeated measures anova for each pair of comparisons
for within in comparisons:
    print(within)
    get_rm_plot(df, subj, betw, within, outfold, repl=True)


## Now let's see how well the measurements of noun and verb lengths can differentiate between
## 2 modern languages and 2 historical languages with different word orders.

import checks.test_hist.classify_lgs
from checks.test_hist.classify_lgs import *

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
# (via UD 2.14) and tagged corpora of Classical and Egyptian Arabic (via the Quran
# and BOLT). See `checks/test_hist/check_corpora.py` for more detail.
udstats = "checks/test_hist/corpora_stats.xlsx"
# get the data for prediction
df = get_predict_data(udstats)
# train on the training data and predict on the unseen data
df = train_predict(df, classifiers, X, y)
# write the results to a file
df.to_excel("checks/test_hist/word_order_hist.xlsx", index=False)
# indeed, length of nouns and verbs allows us to predict word order


## Now let's conduct a hierarchical linear regression to assess whether noun/verb lengths
## allow for better prediction than descent from a common ancestor language, attempting to
## replicate Dunn et al 2011.

import checks.hierlinreg
from checks.hierlinreg import *

famfile = "checks/glottolog/All_comparisons_imputed_families_geodata.xlsx" # the file where we add family info from Glottolog
complete = "data/output/All_comparisons_imputed.xlsx" # the file with all word orders for the taggedPBC

# check if the file with families exists
if not os.path.isfile(famfile):
    linfile = "checks/glottolog/lineages.json" # the lineages and ISO codes from Glottolog, stored in json format
    dfcom = pd.read_excel(complete)
    dfam = get_families(dfcom, linfile)
    dfam.to_excel(famfile)

dunnfile = "checks/glottolog/Dunn_isos.xlsx" # this file contains the ISO codes and families of the languages from the Dunn et al paper
dunn = pd.read_excel(dunnfile) # read in the file

# These are the actual languages (ISO codes) from the Dunn et al paper. Some of these were split into separate
# Glottocodes (under a single ISO code), but the PBC only has ISO codes, so we end up with fewer.
dunnlist = dunn['ISO639_3'].to_list()
print("Number of languages investigated by Dunn et al:", len(dunnlist))
print(dunn['Family'].value_counts()) # these are the number of languages per family in the Dunn et al paper
print(list(dunn['Family'].value_counts().keys())) # these are the language families in the Dunn et al paper
# we could replace 'Bantu' with 'Atlantic-Congo', which is the top-level language family
# but let's be a bit more selective and choose 'Narrow Bantu' (Glottocode 'narr1281'), which is more in line with Dunn et al
# for this we will need to import another file containing languages with that classification
dunnfams = ['Narrow Bantu', 'Austronesian', 'Indo-European', 'Uto-Aztecan']
with open("checks/glottolog/NarrowBantu-narr1281.json") as f:
    bantu = json.load(f) # load the list with ISO codes of 'Narrow Bantu' lgs from Glottolog, stored in json format

# read in the dataset with families from Glottolog
df = pd.read_excel(famfile)
df['index'] = df['index'].fillna('nan') # when pandas imports the spreadsheet it thinks this ISO code is NaN
# print(df.head())
df.loc[df['index'].isin(bantu), 'Family_line'] = 'Narrow Bantu' # change this value for languages in the Bantu list

# remove 'free' languages from the dataset to allow for binary DV
df = df[~df["Noun_Verb_order"].str.contains('free')]
print("Number of languages in the taggedPBC with SV/VS orders:", len(df))
print("Top 10 families by number of members in the taggedPBC:", df['Family_line'].value_counts()[:10])

famlist = filter_families(df, dunnfams) # these are families in the taggedPBC and the Dunn et al paper (Bantu is subsumed by 'Atlantic-Congo')
lgls1 = df[df['index'].isin(dunnlist)] # these are languages in the taggedPBC which are also in the Dunn et al paper
print("Number of languages in the taggedPBC shared with Dunn et al:", len(lgls1))
lglist = filter_lgs(df, famlist) # these are languages in the taggedPBC which are in the families from the Dunn et al paper
print("Number of languages in the taggedPBC shared with the families investigated by Dunn et al:", len(lglist))
lnum = 75
famlistcount1 = filter_lgs(df, filter_families(df, lnum))
print("Number of languages in the taggedPBC in families with more than {num} members: {famc}".format(num=lnum, famc=len(famlistcount1)))
cnum = 1
famlistcount2 = filter_lgs(df, filter_families(df, cnum))
print("Number of languages in the taggedPBC in families with more than {num} members: {famc}".format(num=cnum, famc=len(famlistcount2)))
dnum = 0
famlistcount3 = filter_lgs(df, filter_families(df, dnum))
print("All languages in the taggedPBC including isolates: {famc}".format(famc=len(famlistcount3)))

fit_transform_cats(df, 'Noun_Verb_order', 'Class') # convert the SV/VS classes to binary
fit_transform_cats(df, 'Family_line', 'Fam_class') # convert the language family to numeric
fit_transform_cats(df, 'macroarea', 'Macro_class') # convert the Macroarea to numeric

# Define the models for hierarchical regression including predictors for each model
X1 = {
     1: ['N1ratio-ArgsPreds'], # variable known to differentiate word order between languages (base model)
     2: ['N1ratio-ArgsPreds', 'latitude', 'longitude', 'Macro_class'], # include lat/long coordinates and macroarea
     3: ['N1ratio-ArgsPreds', 'latitude', 'longitude', 'Macro_class', 'Fam_class'], # include family
     4: ['N1ratio-ArgsPreds', 'latitude', 'longitude', 'Macro_class', 'Fam_class', 'Nlen_freq', 'Vlen_freq'], # include Nlen/Vlen
     }

# Define the outcome variable
y = 'Class' # SV/VS

# set up a series of lists of languages (samples) to check using HLR models
checklists = [
               (dunnlist, "Dunn_lgs"), # the languages common to the taggedPBC and Dunn et al
               (lglist, "Dunn_fams"), # languages in the taggedPBC from the families investigated by Dunn et al
               (famlistcount1, ">{lnum}_lg_families".format(lnum=lnum)), # languages in the taggedPBC from families with a large number of members
               (famlistcount2, ">{lnum}_lg_families".format(lnum=cnum)), # languages from families with 2+ members in the taggedPBC (excludes isolates)
               (famlistcount3, "All_lg_families".format()), # all languages in the taggedPBC
               ]

# go through each sample and run the HLR models
for num, check in enumerate(checklists):
     temp = df[df['index'].isin(check[0])]
     run_HLR(temp, X1, y, "{:02d}".format(num+1)+"_"+check[1], "checks/results/")

## Based on this analysis, Noun/Verb lengths are a stronger predictor of word order
## than descent from a common ancestor (family membership).

## Let's run another set of models, removing language area, just to check

# Define the models for hierarchical regression, excluding language area
X2 = {
     1: ['N1ratio-ArgsPreds'], # variable known to differentiate word order between languages (base model)
     2: ['N1ratio-ArgsPreds', 'Fam_class'], # include family
     3: ['N1ratio-ArgsPreds', 'Fam_class', 'Nlen_freq', 'Vlen_freq'], # include Nlen/Vlen
     }

# go through each sample and run the HLR models
for num, check in enumerate(checklists):
     temp = df[df['index'].isin(check[0])]
     run_HLR(temp, X2, y, "{:02d}".format(num+6)+"_"+check[1]+"_noLgArea", "checks/results/")

## Based on these models, family membership is only significant with the sample
## of languages from the families in the Dunn et al paper, whereas Noun/Verb lengths
## are significant for all samples and account for more variance.

## We can also check another set of models, where family membership is considered
## before language area.

# Define the models for hierarchical regression, excluding language area
X3 = {
     1: ['N1ratio-ArgsPreds'], # variable known to differentiate word order between languages (base model)
     2: ['N1ratio-ArgsPreds', 'Fam_class'], # include family
     3: ['N1ratio-ArgsPreds', 'Fam_class', 'latitude', 'longitude', 'Macro_class'], # include geographical features
     4: ['N1ratio-ArgsPreds', 'Fam_class', 'latitude', 'longitude', 'Macro_class', 'Nlen_freq', 'Vlen_freq'], # include Nlen/Vlen
     }

# go through each sample and run the HLR models
for num, check in enumerate(checklists):
     temp = df[df['index'].isin(check[0])]
     run_HLR(temp, X3, y, "{:02d}".format(num+11)+"_"+check[1]+"_Famfirst", "checks/results/")

## Still, based on these models, family membership is only significant with the sample
## of languages from the families in the Dunn et al paper, and accounts for less variance
## than either geographical/areal factors and Noun/Verb lengths.

## Now let's do some language sampling, to see how this affects results

# First we import a randomization library
import random, tqdm

# set up a dictionary to count which variables are significant for each HLR
countdict = {"NVlengths": 0, "Family": 0, "Area": 0, "None": 0}
# let's just count how many languages are present in families with > 40 members
famdict = family_dict(df, filter_families(df, 40))
count = 0
for k, v in famdict.items():
    count += len(v)

print(count) # this is the number of languages in the dataset found in large families (1017)
print(len(famdict.keys())) # here are the families in question (8)
# Now let's get all the languages in the dataset
famdict = family_dict(df, filter_families(df, 0))

n = 4 # this is our divisor: let's sample 1/4th of languages in a family

# set up 1000 runs
for num in tqdm.tqdm(range(1000)):
    # for each run we take a random sample based on our divisor
    dlist = []
    for k, v in famdict.items():
        try:
            dlist += random.sample(v, int(len(v)/n))
        except:
            dlist.append(random.choice(v))
    
    # go through each sample and run the HLR models
    temp = df[df['index'].isin(dlist)]
    # here we use the first set of models
    fdict = run_HLR(temp, X1, y, "XX"+"_"+check[1]+"_random", "checks/results/", feedback=True, repl=True)
    # first we check if NVlengths is significant (model 4)
    if fdict[4]['F-val change'] > 0.0:
        if fdict[4]['P-val (F-val change)'] < 0.05:
            countdict["NVlengths"] += 1
    # then we check if Family is important (model 3)
    elif fdict[3]['F-val change'] > 0.0:
        if fdict[3]['P-val (F-val change)'] < 0.05:
            countdict["Family"] += 1
    # then we check if Area is important (model 2)
    elif fdict[2]['F-val change'] > 0.0:
        if fdict[2]['P-val (F-val change)'] < 0.05:
            countdict["Area"] += 1
    # otherwise we assume there are none
    else:
        countdict["None"] += 1

print(len(dlist)) # this should be 1000 runs
print(countdict) # this is the dictionary of results
## Here we see that NVlengths is more significant that all other factors
## over 50% of the time.