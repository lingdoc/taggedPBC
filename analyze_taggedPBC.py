import os, glob

# first get the data directly from the tagged corpus
import analysis.get_nvs
from analysis.get_nvs import *
import matplotlib.pyplot as plt
import seaborn as sns

too_few = [] # a list to store the ISO639-3 codes of languages with fewer than 100 unique nouns/verbs/predicates
datafold = "data/tagged/" # the location of the tagged PBC
fileslist = [x for x in glob.glob(datafold+"*.json")] # a list of the JSON files for each tagged language
outputfile = "data/output/stats_All.xlsx"

# if the spreadsheet doesn't exist, do the following (delete spreadsheet if you want to re-run the analyses)
if not os.path.isfile(outputfile):
    # get the tagged data, run analyses, store it in this dataframe
    # might take a while..
    df = get_df_from_tagged(fileslist, too_few)
    print(df.head())
    df.to_excel(outputfile, index=False) # write to an output file
    print(list(set(too_few))) # these languages have fewer than 100 unique nouns/verbs
else:
    df = pd.read_excel(outputfile)

# to get an overview of the number of sentences in each corpus, let's create a histogram to get counts in bins
n_plt, bins_plt, patches = plt.hist(df['Verse_counts']) # plot histogram
print(bins_plt) # these are the different bins with values for each bin
plt.savefig("data/output/plots/hist-Verse_counts.png")
plt.clf()
# based on this output, it looks like the majority of languages have over 1800 verses
vcounts = df['Verse_counts'].to_list()
print("The fewest number of verses in any corpus in the tagged PBC is:", min(vcounts))
print("The most number of verses in any corpus in the tagged PBC is:", max(vcounts))
# let's create 4 bins for sorting
w, x, y, z = 700, 1000, 1500, 1800
# create a dict to store the counts
finalbins = {">="+str(w): len([v for v in vcounts if x > v >= w]), ">"+str(x): len([v for v in vcounts if y > v >= x]), ">"+str(y): len([v for v in vcounts if z > v >= y]), ">"+str(z): len([v for v in vcounts if v >= z])}
print(finalbins) # these are the counts of languages in each bin
# set the keys for plotting
keys = list(finalbins.keys())
# get values in the same order as keys
vals = [finalbins[k] for k in list(finalbins.keys())]
sns.barplot(x=keys, y=vals, palette=sns.color_palette('coolwarm'), hue=keys) # plot the bins
plt.savefig("data/output/plots/hist-Verse_counts.png") # save the plot
plt.clf()
print("{}\t{}".format('N_verse','N_Langs'))
for k, v in finalbins.items():
    label = v
    print("{}\t{}".format(k, label))

# get some histograms to see if the data is normally distributed
# first check N1 ratio in the dataset
cols = ['N1ratio-ArgsPreds', 'N1ratio-NsVs']
sns.kdeplot(data=df[cols], fill=True, palette=sns.color_palette('bright'))#, palette='coolwarm')
plt.savefig("data/output/plots/density_plot-counts_N1ratio.png")
plt.clf()
# next check on our counts of arguments and predicates in the dataset
cols = ['Args_count', 'Preds_count']
sns.kdeplot(data=df[cols], fill=True, palette=sns.color_palette('bright'))#, palette='coolwarm')
plt.savefig("data/output/plots/density_plot-counts_arguments_predicates.png")
plt.clf()
# now look at counts of only Nouns and Verbs
cols = ['Ns_count', 'Vs_count']
sns.kdeplot(data=df[cols], fill=True, palette=sns.color_palette('bright'))#, palette='coolwarm')
plt.savefig("data/output/plots/density_plot-counts_nouns_verbs.png")
plt.clf()
# next check on the distributions of only Noun/Verb lengths, with/without frequency info
cols = ['Vlen_freq', 'Nlen_freq', 'Vlen', 'Nlen']
sns.kdeplot(data=df[cols], fill=True, palette=sns.color_palette('bright'))#, palette='coolwarm')
plt.savefig("data/output/plots/density_plot-lengths_nouns_verbs.png")
plt.clf()
# next let's look at distributions of all argument/predicate lengths, with/without frequency info
cols = ['Arglen_freq', 'Predlen_freq', 'Arglen', 'Predlen']
sns.kdeplot(data=df[cols], fill=True, palette=sns.color_palette('bright'))#, palette='coolwarm')
plt.savefig("data/output/plots/density_plot-lengths_arguments_predicates.png")
plt.clf()
# data has normal distributions, with some kurtosis but nothing major

# now run statistics
import analysis.anovas
from analysis.anovas import *

# the code below assumes you have imputed word order values using the consolidated databases as a training set
filen = "data/output/All_comparisons_imputed.xlsx" # spreadsheet with all languages classified for "SV", "VS", "free" word order
outfold = "data/output/plots/" # output folder for the resulting datasheets and plots

try:
    df = pd.read_excel(filen)
except:
    print("The file `{filen}` does not exist. Run the `verify_tagged_PBC.py` script to create it.".format(filen=filen))
    exit()

df['index'] = df.index

subj = 'index'
betw = 'Noun_Verb_order'
comparisons = [
                ['Nlen', 'Vlen'], ['Nlen_freq', 'Vlen_freq'],
                ['Arglen', 'Predlen'], ['Arglen_freq', 'Predlen_freq'],
                ['Pronlen', 'Vlen'], ['Pronlen_freq', 'Vlen_freq']
                ]

# conduct the repeated measures anova for each pair of comparisons
for within in comparisons:
    print(within)
    get_rm_plot(df, subj, betw, within, outfold)
