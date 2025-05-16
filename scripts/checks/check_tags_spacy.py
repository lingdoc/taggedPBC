import spacy, json, glob
import pandas as pd
from spacy.tokens import Doc

def get_ratios(dc, k, n, wd, l, app1, app2):
        if any(x in wd[1] for x in l):
            if dc[k][n][0] == wd[0]:
                if dc[k][n][1] in l:
                    app1.append(1)
                else:
                    app2.append(1)
            else:
                print(wd[0], dc[k][n][0])

def get_langratios(sharedlangs, taggedfiles, splangs):
    dfdict = {}
    for sl in sharedlangs:
        sourcefile = [x for x in glob.glob(taggedfiles+"*.json") if sl == x.split("/")[-1].split("-")[0]][0]
        print(sourcefile)
        with open(sourcefile) as s:
            source = json.load(s)
        print(source[:2])
        sourcedict = {}
        sourcelines = []
        for line in source:
            line2 = [x[0] for x in line[1]]
            sourcedict[line[0]] = line[1]
            newline = " ".join(line2)
            sourcelines.append([line[0], line2])
        # print(sourcedict['40001023'])
        sourcepos = list(set([x[1] for k, v in sourcedict.items() for x in v]))
        print(sourcepos)

        language = splangs[sl][1]+"_core_news_sm"

        try:
            nlp = spacy.load(language)
        except OSError:
            print("Downloading language model for the spaCy POS tagger\n(don't worry, this will only happen once)")
            from spacy.cli import download
            download(language)
            nlp = spacy.load(language)

        print(len(nlp.vocab))
        print("Tagging {lang} data with SpaCy (might take a while)...".format(lang=sl))
        newposlines = {}
        for line in sourcelines:
            doc = Doc(nlp.vocab, words=line[1], spaces=[True]*len(line[1]))

            newposlines[line[0]] = [[w.text, w.pos_] for w in nlp(doc)]
        # print(newposlines['40001023'])
        newpos = list(set([x[1] for k, v in newposlines.items() for x in v]))
        # print(newpos)

        correctns = []
        incorrectns = []
        cns = []
        ins = []
        cps = []
        ips = []
        cpns = []
        ipns = []

        correctvs = []
        incorrectvs = []
        cvs = []
        ivs = []
        cas = []
        ias = []

        nslist = ["NOUN", "PROPN", "PRON"]
        onlist = ["NOUN"]
        proplist = ["PROPN"]
        pronlist = ["PRON"]
        vslist = ["VERB", "AUX"]
        ovlist = ["VERB"]
        auxlist = ["AUX"]

        print("Getting correspondences between {lang} data in PBC and SpaCy...".format(lang=sl))
        for key, sent in sourcedict.items():
            for num, words in enumerate(sent):
                get_ratios(newposlines, key, num, words, nslist, correctns, incorrectns)
                get_ratios(newposlines, key, num, words, onlist, cns, ins)
                get_ratios(newposlines, key, num, words, proplist, cps, ips)
                get_ratios(newposlines, key, num, words, pronlist, cpns, ipns)
                get_ratios(newposlines, key, num, words, vslist, correctvs, incorrectvs)
                get_ratios(newposlines, key, num, words, ovlist, cvs, ivs)
                get_ratios(newposlines, key, num, words, auxlist, cas, ias)

        print("Language:", sl, splangs[sl][0])
        print("Ratio of corresponding arguments", len(correctns)/(len(correctns)+len(incorrectns)))
        print("Ratio of corresponding predicates", len(correctvs)/(len(correctvs)+len(incorrectvs)))
        dfdict[sl] = {"Language": splangs[sl][0], "Ratio of corresponding nouns": len(correctns)/(len(correctns)+len(incorrectns)), "Ratio of corresponding verbs": len(correctvs)/(len(correctvs)+len(incorrectvs)), "Only nouns": len(cns)/(len(cns)+len(ins)), "Only propns": len(cps)/(len(cps)+len(ips)), "Only prons": len(cpns)/(len(cpns)+len(ipns)), "Only verbs": len(cvs)/(len(cvs)+len(ivs)), "Only auxs": len(cas)/(len(cas)+len(ias))}
        print(dfdict[sl])

    df = pd.DataFrame.from_dict(dfdict, orient='index')

    return df
