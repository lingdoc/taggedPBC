import json, os, glob, sys
# get functions from the `analysis` scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts/analysis/")))
from get_nvs import convert_conllu, get_wordorders, get_isodict
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# this script gets verses in the tagged PBC for a select group of languages
# (i.e. in a language family), allowing for comparison

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

# let's compare verses between languages in the Austroasiatic family
familylist = ["Austroasiatic"]
# the dict below contains the families and languages within these families
indict = {k: v for k, v in lineages.items() if any(x in k for x in familylist)}

# now let's see what the intersection is between these languages and our dataset

# these are the ISO codes & info for the languages in the family above
isos = {x: [v[x][0], v[x][5], v[x][6]] for k, v in indict.items() for x in v.keys()}

corploc = "../corpora/conllu/" # the location of the conllu-formatted corpora
# get a list of filenames that have the iso codes we are interested in
filens = [x for x in glob.glob(corploc+"*.conllu") if x.split("/")[-1].split("-")[0] in isos.keys()]
newisos = {}
branches = {}
for y in filens:
	iso = y.split("/")[-1].split("-")[0]
	branch = isos[iso][1].split("\t")[-1]
	newisos[iso] = [isos[iso][0], isos[iso][1]]
	if branch in branches.keys():
		branches[branch].append(iso)
	else:
		branches[branch] = [iso]

# let's look at the number of languages in our corpus from each branch
for k, v in branches.items():
	print(k, len(v))

# let's take the Khasi-Palaung branch which has 8 languages
langs = branches['Khasi-Palaung']
print(langs) # the isos
# here are the actual corpora for those languages
filens = [x for x in filens if x.split("/")[-1].split("-")[0] in langs]
print(filens) # the paths of the corpora

# now we have the filenames and we can get the data for these languages
isodict = {}
for cor in filens:	
	iso = cor.split("/")[-1].split("-")[0] # this is the ISO code
	# this function converts a corpus to a list of items
	corpus, englines = convert_conllu(cor, trans=True)
	
	isodict[iso] = {}
	# here we create a dictionary for each corpus with the actual data
	# if 'verses' is True, it will return a 'tracked_sents' dict with the verse
	# number of a particular word order pattern - this can be useful for extracting
	# particular verses for syntactic comparison, but we won't use it in this script
	isodict = get_wordorders(iso, corpus, isodict, verses=True)

	isodict[iso]['corpus'] = corpus # this is the tagged corpus for this iso
	isodict[iso]['englines'] = englines # this is a list of the English translations

print(isodict.keys()) # these are the isos of the corpora whose information we stored

# There are various ways to determine which verses you want to compare,
# such as looking for particular structures across sentences. Maybe you 
# want to find verses with particular combinations of words or glosses 
# or orders of constituents. In our case we are simply getting a single 
# verse for the sake of illustration.

# this is our list of verses, it currently contains a single verse reference number
countlist = ['44005040']

entries = {} # a new dict to store our entries
# go through each verse in our list
for verse in countlist:
	newisodict = {} # create a new dict
	# go through each corpus in our (reduced) dataset
	for k in isodict.keys():
		# for each corpus
		for line in isodict[k]['corpus']:
			# if the verse is in our list
			if line[0] == verse:
				# add it to the new dict under the iso code
				newisodict[k] = line[1]
	# add this verse in each language to the entries dict
	entries[verse] = newisodict
				
# now we can write this info to a file for comparison
for entry in entries.keys():
	print(entry) # print the verse number for our info
	# We will write the information to a tab-separated file for viewing as a spreadsheet.
	# You may want to modify this path if you are working with multiple verses, since
	# this will write a single file in the current directory for each verse.
	with open(entry+"_verses.tsv", "w") as f:
		# first we write the English translation at the top of the file
		f.write(isodict[k]['englines'][entry]+"\n\n")
		# print the English to the terminal too, for our info
		print(isodict[k]['englines'][entry]+"\n")
		for k, v in entries[entry].items():
			# print(k) # this is the iso code
			f.write(k+"\n") # write the iso code in the file
			wordlist = [word[0] for word in v] # get all the words of the verse in a list
			poslist = [word[1] for word in v] # get all the POS of the verse in a list
			deplist = [word[2] for word in v] # get all the dependencies
			glosslist = [word[3] for word in v] # get all the glosses
			f.write("\t".join(wordlist)+"\n") # write a line of the words
			f.write("\t".join(poslist)+"\n") # write a line of the POS
			f.write("\t".join(deplist)+"\n") # write a line of the dependencies
			f.write("\t".join(glosslist)+"\n") # write a line of the glosses
			f.write("\n")
