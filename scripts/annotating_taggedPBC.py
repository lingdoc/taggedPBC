import os, glob

# first get the data directly from the tagged corpus
import analysis.get_nvs
from analysis.get_nvs import *
import matplotlib.pyplot as plt
import seaborn as sns

too_few = [] # a list to store the ISO639-3 codes of languages with fewer than 100 unique nouns/verbs/predicates
datafold = "../corpora/json/" # the location of the tagged PBC
fileslist = [x for x in glob.glob(datafold+"*.json")] # a list of the JSON files for each tagged language
outputfile = "data/output/stats_All.xlsx"

# if the spreadsheet doesn't exist, do the following (delete spreadsheet if you want to re-run the analyses)
if not os.path.isfile(outputfile):
    # get the tagged data, run analyses, store it in this dataframe
    # might take a while..
    df = get_df_from_tagged(fileslist, too_few)
    conlangs = ['epo', 'tlh'] # these are constructed languages (Esperanto and Klingon) in the PBC
    df = df[~df['index'].isin(conlangs)] # remove constructed languages from analysis spreadsheet
    print(df.head())
    df.to_excel(outputfile, index=False) # write to an output file
    print(list(set(too_few))) # these languages have fewer than 100 unique nouns/verbs, currently only 'yue' (Cantonese)
else:
    df = pd.read_excel(outputfile)

## print out some basic stats from the dataset
print("The average number of arguments in the tagged PBC is:", df['Args_count'].mean())
print("The average number of predicates in the tagged PBC is:", df['Preds_count'].mean())
print("The average length of arguments in the tagged PBC is:", df['Arglen'].mean())
print("The average length of predicates in the tagged PBC is:", df['Predlen'].mean())
print("The most arguments in the tagged PBC is:", df['Args_count'].max())
print("The most predicates in the tagged PBC is:", df['Preds_count'].max())
print("The fewest arguments in the tagged PBC is:", df['Args_count'].min())
print("The fewest predicates in the tagged PBC is:", df['Preds_count'].min())
print("")

# to get an overview of the number of sentences in each corpus, let's create a histogram to get counts in bins
n_plt, bins_plt, patches = plt.hist(df['Verse_counts']) # plot histogram
print(bins_plt) # these are the different bins with values for each bin
plt.savefig("data/output/plots_distr/hist-Verse_counts.png")
plt.clf()
# based on this output, it looks like the majority of languages have over 1800 verses
vcounts = df['Verse_counts'].to_list()
print("The fewest number of verses in any corpus in the tagged PBC is:", min(vcounts))
print("The most number of verses in any corpus in the tagged PBC is:", max(vcounts))
# let's create 4 bins for sorting
w, x, y, z = 700, 1000, 1500, 1800
# create a dict to store the counts
finalbins = {">"+str(w): len([v for v in vcounts if x > v >= w]), ">"+str(x): len([v for v in vcounts if y > v >= x]), ">"+str(y): len([v for v in vcounts if z > v >= y]), ">"+str(z): len([v for v in vcounts if v >= z])}
print(finalbins) # these are the counts of languages in each bin
# set the keys for plotting
keys = list(finalbins.keys())
# get values in the same order as keys
vals = [finalbins[k] for k in list(finalbins.keys())]
sns.barplot(x=keys, y=vals, palette=sns.color_palette('coolwarm'), hue=keys) # plot the bins
plt.savefig("data/output/plots_distr/hist-Verse_counts.png") # save the plot
plt.clf()
print("{}\t{}".format('N_verse','N_Langs'))
for k, v in finalbins.items():
    label = v
    print("{}\t{}".format(k, label))

# get some histograms to see if the data is normally distributed
# here are the columns to use for density plots:
density = [['N1ratio-ArgsPreds', 'N1ratio-NsVs'], # N1 ratios
            ['Args_count', 'Preds_count'], # counts of arguments and predicates
            ['Ns_count', 'Vs_count'], # counts of only Nouns and Verbs
            ['Vlen_freq', 'Nlen_freq', 'Vlen', 'Nlen'], # only Noun/Verb lengths, with/without frequency info
            ['Arglen_freq', 'Predlen_freq', 'Arglen', 'Predlen'], # all argument/predicate lengths, with/without frequency info
            ]

for cols in density:
    sns.kdeplot(data=df[cols], fill=True, palette=sns.color_palette('bright'))#, palette='coolwarm')
    titledict = {'N1ratio-ArgsPreds': 'N1ratios', 'Args_count': 'Args_Preds_counts', 'Ns_count': 'Ns_Vs_counts', 'Vlen_freq': 'Vs_Ns_lens', 'Arglen_freq': 'Args_Preds_lens'}
    title = titledict[cols[0]]
    plt.savefig("data/output/plots_distr/density_plot-"+title+".png")
    plt.clf()

# data has normal distributions, with some kurtosis in the lengths but nothing major
# let's check out the lengths using bootstrapping to see if they're ok
for col in density[3]+density[4]:
    pd.plotting.bootstrap_plot(df[col])
    plt.savefig("data/output/plots_distr/bootstrap_plot-"+col+".png")
    plt.clf()

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
