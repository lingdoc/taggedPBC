import glob, json, os
from statistics import mean
import pandas as pd

# the following code assumes you have two files from UD (v2.14) for Ancient Hebrew (hbo)
# and Modern Hebrew (heb) that have been romanized using the `uroman` converter. Each 
# file contains the complete UDT corpus of POS-tagged sentences.
folder = "../../../ud-2.14/iso-tagged/roman/" # this is the folder of romanized UDT

isos = ['hbo', 'heb']
# get the Hebrew isos
fileslist = [x for x in glob.glob(folder+"*.txt") if x.split("/")[-1].split("_")[0] in isos]

# check to make sure the stats file doesn't exist at the current location
if not os.path.isfile("UD_stats.xlsx"):
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

		# open the file and compute the stats
		with open(fn) as readfile:
		    texts = json.load(readfile)

		    for sent in texts:
		    	sentords = []
		    	for word in sent:
		    		if word[1] == "NOUN":
		    			nouns.append(word[0])
		    			sentords.append("N")
		    		elif word[1] == "VERB":
		    			verbs.append(word[0])
		    			sentords.append("V")
		    		elif any(x in word[1] for x in nslist):
		    			sentords.append("N")
		    		elif any(x in word[1] for x in vslist):
		    			sentords.append("V")
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
		nlenunique = mean([len(x) for x in set(nouns)])
		nlenfreq = mean([len(x) for x in nouns])
		vlenunique = mean([len(x) for x in set(verbs)])
		vlenfreq = mean([len(x) for x in verbs])

		isodict[iso] = {'Nlen_freq': nlenfreq, 'Vlen_freq': vlenfreq, 'Nlen': nlenunique, 'Vlen': vlenunique, 'N1ratio-ArgsPreds': N1ratio}

	df = pd.DataFrame.from_dict(isodict, orient='index').reset_index()
	print(df.head())


	df.to_excel("UD_stats.xlsx")