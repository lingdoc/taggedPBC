import json, os
import pandas as pd

# this script gets the list of languages with corpora in the taggedPBC and creates a README
front = """# Languages in the *taggedPBC*

This README file outlines the languages represented by CoNNL-U formatted corpora in the 
current version of the *taggedPBC* and is automatically generated based on the stats file 
(["stats_All.xlsx"](../scripts/data/output/stats_All.xlsx)) found under the 
[scripts/data/output](../scripts/data/output/) folder. This file can be re-generated 
via a script in the [recipes](../recipes/) folder.

The current document organizes languages by language phylum/family and ISO 639-3 code. 
Additional information includes the full name of the language and region, with links (that 
have not been fully verified) to the ISO 639-3 site, Glottolog, and the Ethnologue. Isolates 
are listed within a single group, and single languages that represent an individual family 
are also listed together at the end of this document.

"""

stats = "../scripts/data/output/stats_All.xlsx" # the file of stats extracted from the dataset
df = pd.read_excel(stats) # read the file with language statistics

df['index'] = df['index'].fillna('nan') # import language data
dfdict = df.set_index("index").to_dict("index") # convert to dict

# load the lineage information that is present in Glottolog (as of 3 June 2025)
linfile = "../scripts/checks/glottolog/lineages.json"

with open(linfile) as f:
	# load the json file with lineages and ISO codes from Glottolog, stored in json format
	lineages = json.load(f)

# here we get the language names and add them to our dictionary
for fam, v in lineages.items():
	for k in v.keys():
		if k in dfdict.keys():
			dfdict[k]['Name'] = lineages[fam][k][0]

# convert back to df
df = pd.DataFrame.from_dict(dfdict, orient='index').astype(str).reset_index()
# get only some of the data
headlist = ['index', 'Name', 'Verse_counts', 'macroarea', 'Family_line', 'Family_branch', 'Family_subgroup']
df = df[headlist]
# rewrite the names of the columns
newheadlist = ['ISO 639-3', 'Name', 'Verses in corpus', 'Macroarea', 'Family', 'Branch', 'Subgroup']
df.columns = newheadlist
print(df.head())

# group by the 'Family' column
groups = df.groupby('Family')

# extract keys from groups
keys = groups.groups.keys()

famdict = {} # this dictionary stores our families
singles = [] # track single languages (no other family member in the dataset)
isogroups = [] # track isolates
for i in keys:
	# check if there is more than one member in the family
	if len(groups.get_group(i)) > 1:
		family = groups.get_group(i)['Family'].iloc[0] # get this family name
		dfdict = groups.get_group(i).drop('Family', axis=1) # retrieve all related languages
		dfdict = dfdict.sort_values(by=['Branch', 'Subgroup', 'ISO 639-3']) # sort this df
		interdict = dfdict.set_index("ISO 639-3").to_dict("index") # convert to dict
		famdict[family] = {idx: list(row_dict.values()) for idx, row_dict in interdict.items()} # convert rows to lists
	else:
		# if there is only one member of the family
		tmp = groups.get_group(i)
		# check whether the language is an isolate
		if tmp['ISO 639-3'].iloc[0] == tmp['Family'].iloc[0]:
			singles.append(i) # if it's just a lone language, add it to our singles list
		else:
			isogroups.append(i) # otherwise add it to our isolates list

# get the group of isolates
isolates = pd.concat([groups.get_group(name) for name in isogroups])
interdict = isolates.set_index("ISO 639-3").to_dict("index")
# add it to the family dictionary
famdict['Isolates'] = {idx: list(row_dict.values()) for idx, row_dict in interdict.items()}

# get the group of single languages
single_lgs = pd.concat([groups.get_group(name) for name in singles])
interdict = single_lgs.set_index("ISO 639-3").to_dict("index")
# add them to the family dictionary
famdict['Single languages'] = {idx: list(row_dict.values()) for idx, row_dict in interdict.items()}

# this helps us format the tables
newheadlist.remove('Family')
splist = ["--" for x in newheadlist]
temp = ["Single", "Isolates"]

readmefile = "../corpora/README.md" # the documentation that we're creating (list of language info)

# open the file
with open(readmefile, "w") as f:
	f.write(front) # write the intro material
	for family, data in famdict.items():
		f.write("<details>") # write a details block to hide initial view
		f.write("\n")
		f.write("<summary>"+family+"</summary>")
		f.write("\n\n")
		if any(x in family for x in temp):
			f.write(" ### "+family+" in the *taggedPBC*:\n\n") # here's the heading for each family
		else:
			f.write(" ### "+family+" languages in the *taggedPBC*:\n\n") # here's the heading for each family
		f.write("|"+"|".join(newheadlist)+"|Links|\n") # here's the header of the table
		f.write("|"+"|".join(splist)+"|--|\n")
		for lang, vals in data.items():
			# autogenerate links for each language
			links = f"[ISOs](https://iso639-3.sil.org/code/{lang}), [Ethnologue](https://www.ethnologue.com/language/{lang}), [Glottolog](http://glottolog.org/glottolog?iso={lang})"
			# write the language information
			f.write("|"+lang+"|"+"|".join(vals)+"|"+links+"|\n")
		f.write("\n") # end the section
		f.write("</details>")
		f.write("\n")
