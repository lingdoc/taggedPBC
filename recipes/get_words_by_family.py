import json, os, glob, sys, string
# get functions from the `analysis` scripts
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts/analysis/")))
from get_nvs import convert_conllu
from collections import Counter

punc = string.punctuation+"—“‘’"

# this script gets all nouns in the tagged PBC for a select group of languages
# (i.e. in a language family), allowing for comparison

# first we load the lineage information that is present in Glottolog (as of 3 June 2025)
linfile = "../scripts/checks/glottolog/lineages.json"

with open(linfile) as f:
	# load the json file with lineages and ISO codes from Glottolog, stored in json format
	lineages = json.load(f)

# this is a dictionary of all the high-level lineages (and isolates) identified
# by Glottolog scholars, with ISO codes, names, lat, long and general location
# the keys of this dictionary are the Glottocode for the family, followed by a tab
# character and the name of the family
for k in lineages.keys():
	print(k)

# let's see if we can extract information from the dataset to compare nouns between
# the Kartvelian and Nakh-Daghestanian families
familylist = ["Kartvelian", "Nakh-Daghestanian"]
# the dict below contains the families and languages within these families
indict = {k: v for k, v in lineages.items() if any(x in k for x in familylist)}
print(indict)

# now let's see what the intersection is between these languages and our dataset
# these are the ISO codes & names for the languages in the families above
isos = {x: v[x][0] for k, v in indict.items() for x in v.keys()}
# print(isos)

corploc = "../corpora/conllu/" # the location of the conllu-formatted corpora
# get a list of filenames that have the iso codes we are interested in
filens = [x for x in glob.glob(corploc+"*.conllu") if x.split("/")[-1].split("-")[0] in isos.keys()]

# now we have the filenames and we can get the data for these languages
wordsdict = {} # dictionary to store the sets of words for each language
POStag = "NOUN" # let's look only at words with this POS tag for now
# POStag = None # uncomment this line if you want all corresponding words
for cor in filens:
	# print(cor)
	iso = cor.split("/")[-1].split("-")[0] # this is the ISO code
	# this function converts a corpus to a list of items
	corpus = convert_conllu(cor)
	# let's get a set of tokens POS-tagged as "NOUN" for each language
	# we also strip some punctuation characters
	if POStag:
		wordlist = [(x[0].rstrip(".").rstrip(",").rstrip("»").rstrip(":").rstrip("?").rstrip("!").lstrip("«").lstrip("„").lower()) for y in corpus for x in y if x[1] == POStag if x[0] not in punc if len(x[0])>0]
	else:
		wordlist = [(x[0].rstrip(".").rstrip(",").rstrip("»").rstrip(":").rstrip("?").rstrip("!").lstrip("«").lstrip("„").lower()) for y in corpus for x in y if x[0] not in punc if len(x[0])>0]
	uniques = sorted(list(set(wordlist))) # this is a unique set of words
	counted = Counter(wordlist) # this is a frequency distribution of the words
	wordsdict[iso] = uniques # for now just get the unique set

# find the intersection of nouns between pairs of languages
# the code below looks for exact matches, and keep in mind that
# the data has been romanized from the various scripts present
# in the original texts of the PBC
interdict = {} # this stores our sets of common words
# go through each set of words for each language
for lang, nouns in wordsdict.items():
	# compare with each other language
	for iso, nlist in wordsdict.items():
		if iso != lang:
			# store the info on shared items
			if iso+"-"+lang not in interdict.keys():
				inter = list(set(nouns) & set(nlist))
				# but only if there are any
				if len(inter) > 0:
					interdict[lang+"-"+iso] = inter

# here we clean things up a bit for printing
interdict = {k.replace(k.split("-")[0], isos[k.split("-")[0]]).replace(k.split("-")[1], isos[k.split("-")[1]]): v for k, v in interdict.items()}

# print things to the terminal a bit more nicely
print("\nWords shared between pairs of languages in the taggedPBC ({POS})\n--------------".format(POS=POStag))
for key, val in interdict.items():
	val = [x for x in val if len(x) >= 1]
	print("Between "+key+": "+", ".join(val))

# there is a lot of noise here, but with more comprehensive annotations we could
# observe some really interesting things