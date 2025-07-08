import json, os, sys
# get functions from the `analysis` scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts/analysis/")))
from get_nvs import convert_conllu, get_wordorders, get_isodict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# this script compares word order proportions within branches

# first we load the lineage information that is present in Glottolog (as of 3 June 2025)
linfile = "../scripts/checks/glottolog/lineages.json"

with open(linfile) as f:
	# load the json file with lineages and ISO codes from Glottolog, stored in json format
	lineages = json.load(f)

# this is a dictionary of all the high-level lineages (and isolates) identified
# by Glottolog scholars, with ISO codes, names, lat, long, macro-area, branch, and subgroup
# the keys of this dictionary are the Glottocode for the family, followed by a tab
# character and the name of the family
for k in lineages.keys():
	print(k)

# let's compare word orders between languages in the Austroasiatic family
familylist = ["Austroasiatic"]
# the dict below contains the families and languages within these families
indict = {k: v for k, v in lineages.items() if any(x in k for x in familylist)}

# now let's see what the intersection is between these languages and our dataset

# these are the ISO codes & info for the languages in the family above
isos = {x: [v[x][0], v[x][5], v[x][6]] for k, v in indict.items() for x in v.keys()}

filen = "../scripts/data/output/stats_All.xlsx" # file with all the stats from the dataset

# check if the stats file exists, and throw an error if it doesn't
try:
    df = pd.read_excel(filen)
except:
    print("The file `{filen}` does not exist. Run the `annotating_tagged_PBC.py` script to create it.".format(filen=filen))
    exit()

langs = list(isos.keys()) # get the iso codes
langs = [x for x in langs if x in df['index'].to_list()] # make sure the codes are in the spreadsheet
langdf = df[df['index'].isin(langs)] # create a new df with just those languages
# get verb placement proportions
cols = ['VI_prop', 'VM_prop', 'VF_prop', 'Family_line', 'Family_branch']
# reformat
langdf = langdf[['index']+cols]
langdf = langdf.set_index('index').loc[langs].reset_index()
# rename the columns
langdf.columns = ['ISO', 'VI proportion', 'VM proportion', 'VF proportion', 'Family', 'Branch']
# reorder the data for plotting
melted_df = langdf.melt(id_vars=['ISO', 'Family', 'Branch'], var_name='WordOrder', value_name='Proportion')
# draw a lineplot with band-style deviations
ax = sns.lineplot(x='WordOrder', y='Proportion', hue="Branch", style='Branch', err_style='band', sort=False, data=melted_df)#hue_order=order, 
handles, labels = ax.get_legend_handles_labels()
ax.legend(handles=handles[:], labels=labels[:])
plt.savefig("AA_word_orders.png", dpi=300, bbox_inches='tight')
plt.clf()