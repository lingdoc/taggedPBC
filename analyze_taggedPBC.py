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


# now run statistics
import analysis.anovas
from analysis.anovas import *

# the code below assumes you have imputed word order values using the consolidated databases as a training set
filen = "data/output/All_comparisons_imputed.xlsx" # spreadsheet with all languages classified for "SV", "VS", "free" word order
outfold = "data/output/plots_means/" # output folder for the resulting datasheets and plots

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
                ['Pronlen', 'Vlen'], ['Pronlen_freq', 'Vlen_freq'],
                ['Nlen_freq', 'Nlen'], ['Vlen_freq', 'Vlen'],
                ['Arglen_freq', 'Arglen'], ['Predlen_freq', 'Predlen'], 
                ['Pronlen_freq', 'Pronlen'],
                ]

# conduct the repeated measures anova for each pair of comparisons
for within in comparisons:
    print(within)
    get_rm_plot(df, subj, betw, within, outfold)
