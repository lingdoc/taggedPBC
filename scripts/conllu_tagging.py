import os, glob

# first get the data directly from the tagged corpus
import analysis.get_nvs
from analysis.get_nvs import *
import matplotlib.pyplot as plt
import seaborn as sns
from checks.hierlinreg import *

filen = "data/output/stats_All.xlsx" # file with all the stats from the dataset

# check if the stats file exists, and throw an error if it doesn't
try:
    df = pd.read_excel(filen)
except:
    print("The file `{filen}` does not exist. Run the `annotating_tagged_PBC.py` script to create it.".format(filen=filen))
    exit()

print(df.columns)
## print out some basic stats from the dataset
print("The average number of VSO sentences in the taggedPBC is:", df['VSO'].mean())
print("The average number of SVO sentences in the taggedPBC is:", df['SVO'].mean())
print("The average length of SOV sentences in the taggedPBC is:", df['SOV'].mean())
print("The average number of VI sentences in the taggedPBC is:", df['VI'].mean())
print("The average number of VM sentences in the taggedPBC is:", df['VM'].mean())
print("The average length of VF sentences in the taggedPBC is:", df['VF'].mean())
print("")

# get some histograms to see if the data is normally distributed
# here are the columns to use for density plots:
density = [['SOV', 'SVO', 'OSV', 'OVS', 'VOS', 'VSO'], # transitive word orders
            ['SO', 'OS', 'VS', 'SV', 'VO', 'OV'], # intransitive word orders
            ['SOV_prop', 'SVO_prop', 'OSV_prop', 'OVS_prop', 'VOS_prop', 'VSO_prop'], # transitive order proportions
            ['VS_prop', 'SV_prop', 'VO_prop', 'OV_prop'], # intransitive order proportions
            ['VI_prop', 'VM_prop', 'VF_prop'], # verb placement proportions
            ]

for cols in density:
    sns.kdeplot(data=df[cols], fill=True, palette=sns.color_palette('bright'))#, palette='coolwarm')
    titledict = {'SOV': 'Trans_orders', 'SOV_prop': 'Trans_props', 'VI_prop': 'Trans_V_props', 'SO': 'Intrs_orders', 'VS_prop': 'Intrs_props'}
    title = titledict[cols[0]]
    if not os.path.isfile("data/output/plots_distr/density_plot-"+title+".png"):
        plt.savefig("data/output/plots_distr/density_plot-"+title+".png")
    plt.clf()

# for particular languages (English, Irish, Hindi)
langs = ['gle', 'eng', 'hin']
langdf = df[df['index'].isin(langs)]
# get verb placement proportions
cols = ['VI_prop', 'VM_prop', 'VF_prop']
# reformat
langdf = langdf[['index']+cols]
langdf = langdf.set_index('index').loc[langs].reset_index()
langdf.columns = ['ISO639_3:', 'VI proportion', 'VM proportion', 'VF proportion']
langdf.set_index('ISO639_3:', inplace=True)
# plot the proportions
langdf.T.plot()
plt.savefig("data/output/plots_wdorder/proportion_plot-"+"_".join(langs)+".png")
plt.clf()

## the code below combines all the word order observations from the three typological databases
## first get the language stats from the conllu PBC (N1 ratio, word orders, etc)
# main = pd.read_excel("data/output/stats_All.xlsx", index_col=0).to_dict('index')
main = pd.read_excel("data/output/stats_All.xlsx", index_col=0).to_dict('index')

print(len(main)) # check the number of languages

# select the datasets with word order info
datasets = ['wals_word_order.xlsx', 'grambank_word_order.xlsx', 'autotyp_word_order.xlsx',]
datasets = ['data/word_order/'+x for x in datasets]

newdf = pd.DataFrame() # instantiate a new df to store info

# go through each of the typological databases to read transitive word order
# this overwrites existing files with intrans/transitive word order
for data in datasets:
    df = pd.read_excel(data, index_col=3) # index 3 is the ISO639-3 code
    datadict = df.to_dict('index')
    print(len(datadict))
    # get the combined set of codes between this dataset and the conllu corpora
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
        rpldict2 = {"AOV": "SOV", "AVO": "SVO", "OAV": "OSV", "OVA": "OVS", "VAO": "VSO", "VOA": "VOS", "Vxx": "VI", "V-2": "VM", "xxV": "VF"}
        df['SOV_order'] = df['WordOrderAPVBasicLex'].replace(rpldict2)
        print(df['SOV_order'].value_counts())
        df.to_excel("data/output/comparisons_Autotyp.xlsx")
    elif "wals" in data:
        rpldict = {"No dominant order": "free"}#, 'SV': 'N1', 'VS': 'V1'}
        df['SOV_order'] = df['Order of Subject, Object and Verb'].replace(rpldict)
        df['Noun_Verb_order'] = df['Order of Subject and Verb'].replace(rpldict)
        print(df['SOV_order'].value_counts())
        df.to_excel("data/output/comparisons_WALS.xlsx")
    elif "grambank" in data:
        df['Noun_Verb_order'] = df['Intrans_Order']
        
        rpldict = {"notVI": 0, "VI": 1, "notVM": 0, "VM": 1, "notVF": 0, "VF": 1, "UNK": 0}
        df['SOV_order'] = ""
        df['Trans_VI'] = df['Trans_VI'].replace(rpldict)
        df['Trans_VM'] = df['Trans_VM'].replace(rpldict)
        df['Trans_VF'] = df['Trans_VF'].replace(rpldict)
        df.loc[(df['Order_Fixed']=="UNK"), 'SOV_order'] = 'UNK'
        # print(len(df))
        df.loc[(df['Trans_VI'] == 1) & (df['Trans_VM'] == 1) & (df['Trans_VF'] == 1), 'SOV_order'] = "ALL"
        df.loc[(df['Trans_VI'] == 1) & (df['Trans_VM'] == 1) & (df['Trans_VF'] == 0), 'SOV_order'] = "VI+VM"
        df.loc[(df['Trans_VI'] == 1) & (df['Trans_VM'] == 0) & (df['Trans_VF'] == 1), 'SOV_order'] = "VI+VF"
        df.loc[(df['Trans_VI'] == 0) & (df['Trans_VM'] == 1) & (df['Trans_VF'] == 1), 'SOV_order'] = "VM+VF"
        df.loc[(df['Trans_VI'] == 1) & (df['Trans_VM'] == 0) & (df['Trans_VF'] == 0), 'SOV_order'] = "VI"
        df.loc[(df['Trans_VI'] == 0) & (df['Trans_VM'] == 1) & (df['Trans_VF'] == 0), 'SOV_order'] = "VM"
        df.loc[(df['Trans_VI'] == 0) & (df['Trans_VM'] == 0) & (df['Trans_VF'] == 1), 'SOV_order'] = "VF"
        df.loc[(df['Trans_VI'] == 0) & (df['Trans_VM'] == 0) & (df['Trans_VF'] == 0), 'SOV_order'] = "UNK"
        
        df.loc[(df['Order_Fixed'] == "UNK") & (df['Trans_VI'] == "UNK") & (df['Trans_VM'] == "UNK") & (df['Trans_VF'] == "UNK"), 'SOV_order'] = "UNK"
        df.loc[(df['Order_Fixed']=="Free"), 'SOV_order'] = 'free'
        # df['SOV_order'] = df['Intrans_Order'].replace(rpldict)
        print(len(df))
        df = df[df['SOV_order'] != "UNK"]
        print(df['SOV_order'].value_counts())
        df.to_excel("data/output/comparisons_Grambank.xlsx")

    print(df.head())
    # print(df.columns)
    print(len(df))
    newdf = pd.concat([newdf, df])

newdf = newdf.reset_index()
newdf = newdf[newdf['SOV_order'] != 'UNK']

items = {"SOV": "VF", "OSV": "VF", "SVO": "VM", "OVS": "VM", "VSO": "VI", "VOS": "VI"}
litems = ["VF", "VM", "VI", "free"]

newdf['SOV_order'] = newdf['SOV_order'].replace(items)
newdf = newdf[newdf['SOV_order'].isin(litems)]
newdf = newdf.drop_duplicates(subset=['index'], keep='first')
print(len(newdf))
print(newdf['SOV_order'].value_counts())

newdf.to_excel("data/output/All_comparisons_transitive.xlsx", index=False)

## the following code computes statistics for the N1 ratio and word order classifications in
## three typological databases: Grambank, WALS, and Autotyp
import analysis.anovas
from analysis.anovas import *

# check the comparisons between the N1 ratio and word order values in the three databases
datasets = ['comparisons_Grambank.xlsx', 'comparisons_WALS.xlsx', 'comparisons_Autotyp.xlsx',]
datasets = ['data/output/'+x for x in datasets]
datasets = ["data/output/All_comparisons_transitive.xlsx"]

for nfile in datasets:
    outfold = "data/output/plots_wdorder/"
    # ds = nfile.split("_")[-2]

    print(nfile)
    df = pd.read_excel(nfile)
    df['index'] = df.index
    df['Trans_order'] = df['SOV_order'].replace(items)

    subj = 'index'
    betw = 'Trans_order'
    within = 'N1_ratio'
    ds = betw
    get_anova_wordorder(df, subj, betw, within, outfold, ds, repl=True)
    within = 'VI_prop'
    ds = betw
    get_anova_wordorder(df, subj, betw, within, outfold, ds, repl=True)
    within = 'VM_prop'
    ds = betw
    get_anova_wordorder(df, subj, betw, within, outfold, ds, repl=True)
    within = 'VF_prop'
    ds = betw
    get_anova_wordorder(df, subj, betw, within, outfold, ds, repl=True)

## the anovas show a significant correlation between intransitive word order and the N1 ratio
## the difference in means is also visible in the plots
