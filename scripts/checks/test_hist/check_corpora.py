import glob, json, os
from statistics import mean
import pandas as pd

# the following code assumes you have two files from UD (v2.14) for Ancient Hebrew (hbo)
# and Modern Hebrew (heb), as well as two additional tagged corpus files for Classical Arabic
# and Egyptian Arabic (arz) that have been romanized using the `uroman` converter. In this case each UDT
# file contains the complete UDT corpus of POS-tagged sentences. The other files contain
# corpora based on the Quran and the BOLT corpus.
folder1 = "../../../ud-2.14/iso-tagged/roman/" # this is the folder of romanized UDT
folder2 = "../../../test_arabic/data/roman/" # this is the folder of romanized Arabic texts

isos = ['hbo', 'heb', 'cla', 'arz'] # get the Hebrew & Arabic isos (Classical Arabic has no iso code, so we give it one here that hasn't been assigned)
fileslist = [] # access the folders and get the test files
for folder in [folder1, folder2]:
	fileslist += [x for x in glob.glob(folder+"*.txt") if x.split("/")[-1].split("_")[0] in isos]

# check to make sure the stats file doesn't exist at the current location
if not os.path.isfile("corpora_stats.xlsx"):
	isodict = {}

	for fn in fileslist:
		iso=fn.split("/")[-1].split("_")[0]
		verbs = []
		nouns = []
		orders = []
		N1sents = 0
		V1sents = 0
		nslist = ["NOUN", "PROPN", "PRON"]
		vslist = ["VERB", "AUX"]
		N1ratio = 0
		totalsents = 0

		# open the file and compute the stats
		with open(fn) as readfile:
		    texts = json.load(readfile)

		    for sent in texts:
		    	totalsents += 1
		    	sentords = []
		    	for word in sent:
		    		if any(x in word[1] for x in vslist):
		    			sentords.append("V")
		    			if "VERB" in word[1]:
			    			verbs.append(word[0])
		    		elif any(x in word[1] for x in nslist):
		    			sentords.append("N")
		    			if "NOUN" in word[1]:
			    			nouns.append(word[0])
		    	if "V" in sentords and "N" in sentords:
		    		if sentords[0] == "N":
		    			orders.append("N1")
		    			N1sents += 1
		    		elif sentords[0] == "V":
		    			orders.append("V1")
		    			V1sents += 1
		    N1ratio = N1sents/V1sents

		print("Number of verbs for {iso}: {vlen}".format(iso=iso, vlen=len(verbs)))
		print("Number of nouns for {iso}: {nlen}".format(iso=iso, nlen=len(nouns)))
		print("Number of sentences for {iso}: {nlen}".format(iso=iso, nlen=len(nouns)))
		print("")
		nunique = set(nouns)
		vunique = set(verbs)
		nlenunique = mean([len(x) for x in nunique])
		nlenfreq = mean([len(x) for x in nouns])
		vlenunique = mean([len(x) for x in vunique])
		vlenfreq = mean([len(x) for x in verbs])

		isodict[iso] = {'Sentences': totalsents, 'Unique_nouns': len(nunique), 'Unique_verbs': len(vunique), 'Nlen_freq': nlenfreq, 'Vlen_freq': vlenfreq, 'Nlen': nlenunique, 'Vlen': vlenunique, 'N1ratio-ArgsPreds': N1ratio}

	df = pd.DataFrame.from_dict(isodict, orient='index').reset_index()
	print(df.head())


	df.to_excel("corpora_stats.xlsx")