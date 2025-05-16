# The following code illustrates how the indices are selected for the parallel corpus
# of New Testament text used for word alignment in the translation tagging method.
# Since these translations have various copyright restrictions, only the lemmatized
# versions of the two English translations used for verse selection are included in
# the data folder. To replicate these results fully, the translations (numbered
# in accordance with the PBC conventions) can be placed in the correct location and the
# respective code below can be uncommented.
import os, json, spacy, tqdm

nlp = spacy.load("en_core_web_sm")

datafold = "../data/translation/" # the folder we're storing processed files in
# biblefold = "../data/bibles/" # the folder containing the original NIV and NLT bibles
# engniv = "eng-x-bible-newinternational_parsed.txt" # path to the NIV New Testament
# engnlt = "eng-x-bible-newliving_parsed.txt" # path to the NLT New Testament

# ## the following code ensures that we're working with the same verses in both translations
# nltnums = []
# engbibs = [engnlt, engniv]
# for bib in engbibs:
#     if not os.path.isfile(datafold+bib):
#         with open(biblefold+bib, "r") as f:
#             nt = f.readlines()
#             if "newliving" in bib:
#                 for line in nt:
#                     nltnums.append(line.split("\t")[0])
#             else:
#                 nt = [line for line in nt if line.split("\t")[0] in nltnums]
#             print(len(nt))
#         with open(datafold+bib, "w") as newf:
#             for line in nt:
#                 newf.write(line)

# # the following code loads the newly parsed files from the data folder
# with open(datafold+engnlt) as f:
#     nltbible = f.readlines()
# with open(datafold+engniv) as f:
#     nivbible = f.readlines()

def get_lemmas(text):
    """
    Convert the words in the verses to lemmas.
    """
    tlist = [(token.lemma_, token.pos_) for token in nlp(text) if not token.is_stop and token.is_alpha]
    return tlist

nltjson = "eng-nlt-NT_lemmatized.json" # path to store lemmatized version of NLT New Testament
nivjson = "eng-niv-NT_lemmatized.json" # path to store lemmatized version of NIV New Testament

if not os.path.isfile(datafold+nltjson):
    # convert verses/sentences to lemmatized words
    lemnlt = [[line.split("\t")[0]]+get_lemmas(line.split("\t")[1]) for line in tqdm.tqdm(nltbible)]
    lemniv = [[line.split("\t")[0]]+get_lemmas(line.split("\t")[1]) for line in tqdm.tqdm(nivbible)]
    with open(datafold+nltjson, 'w') as fout:
        json.dump(lemnlt, fout, indent=4)
    with open(datafold+nivjson, 'w') as fout:
        json.dump(lemniv, fout, indent=4)

# reload the files
with open(datafold+nltjson) as f:
    nltbible = json.load(f)
with open(datafold+nivjson) as f:
    nivbible = json.load(f)

# sanity check that the number of verses is the same
print(len(nltbible), len(nivbible))

sharedlist = []

for num, line in enumerate(nltbible):
    nltline = set(["_".join(x) if 'PROPN' not in x[1] else "PROPN" for x in line[1:]])
    nivline = set(["_".join(x) if 'PROPN' not in x[1] else "PROPN" for x in nivbible[num][1:]])
    # find all sentences where there are at least 4 matches between the lemmatized words in each verse
    if len(list(nltline.intersection(nivline))) >= 4:
        sharedlist.append(line[0])

print("Total shared indices:", len(sharedlist))

nsharedlist = []

nltbible = [line for line in nltbible if line[0] in sharedlist] # reduce the NLT to only the lines in `sharedlist`
sharedverbs = {}
sharednouns = {}

verbsjson = "sharedverbs.json" # the full list of verbs shared between verses
nounsjson = "sharednouns.json" # the full list of nouns shared between verses

# the following code searches through the lemmatized NLT verses that share 4 or more lemmas with the
# corresponding NIV verses, and makes a list of verbs and nouns that occur in verses where at least 4
# lemmas match, counting the number of occurrences and tracking the verses where they occur
if not os.path.isfile(datafold+verbsjson):
    for line1 in tqdm.tqdm(nltbible):
        nline1 = set(["_".join(x) if 'PROPN' not in x[1] else "PROPN" for x in line1[1:]])
        for line2 in nltbible:
            nline2 = set(["_".join(x) if 'PROPN' not in x[1] else "PROPN" for x in line2[1:]])
            if line1 != line2:
                intsect = list(nline1.intersection(nline2))
                if len(intsect) >= 4:
                    vlist = [x for x in intsect if 'VERB' in x]
                    nlist = [x for x in intsect if 'NOUN' in x]
                    for verb in vlist:
                        if not verb in sharedverbs.keys():
                            sharedverbs[verb] = [line2[0]]
                        else:
                            sharedverbs[verb].append(line2[0])
                    for noun in nlist:
                        if not noun in sharednouns.keys():
                            sharednouns[noun] = [line2[0]]
                        else:
                            sharednouns[noun].append(line2[0])
                    if line2[0] not in nsharedlist:
                        nsharedlist.append(line2[0])
    with open(datafold+verbsjson, 'w') as fout:
        json.dump(sharedverbs, fout, indent=4)
    with open(datafold+nounsjson, 'w') as fout:
        json.dump(sharednouns, fout, indent=4)

# reload the list of verbs and nouns
with open(datafold+verbsjson) as f:
    sharedverbs = json.load(f)
with open(datafold+nounsjson) as f:
    sharednouns = json.load(f)

print("Number of indices with sharednouns:", len(nsharedlist))

print("Total shared verbs:", len(sharedverbs), "Total shared nouns:", len(sharednouns))

svlen = [len(n) for k, n in sharedverbs.items()]
snlen = [len(n) for k, n in sharednouns.items()]
print("Max shared verbs:", max(svlen))
print("Avg shared verbs:", sum(svlen)/len(svlen))
print("Max shared nouns:", max(snlen))

# get the length of each verse
sentlens = {line[0]: len(line[1:]) for line in nltbible}

lenslist = [v for k, v in sentlens.items()]
print("Longest sentence:", max(lenslist), "words")
print("Average length of sentence:", sum(lenslist)/len(lenslist), "words")

# re-parse the shared verbs to remove entries where the verses are longer
fsharedverbs = {}
for k, v in sharedverbs.items():
    for x in v:
        if sentlens[x] < 12:
            if k not in fsharedverbs.keys():
                fsharedverbs[k] = [x]
            else:
                fsharedverbs[k].append(x)

# remove entries that have more than 6k values
fsharedverbs = {k: v for k, v in fsharedverbs.items() if 6000 > len(v) > 5}
print(len(fsharedverbs))

# store this reduced list as a final version
with open(datafold+"sharedverbsf.json", 'w') as fout:
    json.dump(fsharedverbs, fout, indent=4)

# get the unique verse indices
indicesNT = []
for k, v in fsharedverbs.items():
    for x in v:
        if x not in indicesNT:
            indicesNT.append(x)

indicesNT = list(set(indicesNT))
print(len(indicesNT)) # this is the total number of verses used for training word alignment models

# save the sorted indices
with open(datafold+"indices.json", 'w') as fout:
    json.dump(sorted(indicesNT), fout, indent=4)
