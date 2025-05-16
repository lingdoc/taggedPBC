import json, glob, trankit, tqdm
import pandas as pd

def get_langratios(sharedlangs, taggedfiles, trlangs, cacheDir):
    dfdict = {}
    for sl in sharedlangs:
        sourcefile = [x for x in glob.glob(taggedfiles+"*.json") if sl == x.split("/")[-1].split("-")[0]][0]
        print(sourcefile)
        with open(sourcefile) as s:
            source = json.load(s)
        # print(source[:2])
        sourcedict = {}
        sourcelines = []
        for line in source:
            newline = [x[0] for x in line[1]]
            sourcedict[line[0]] = line[1]
            sourcelines.append([line[0], newline])
        # print(sourcedict['40001023'])
        print(len(sourcelines))

        language = trlangs[sl][2]
        # set the cache directory to be outside the repo
        p = trankit.Pipeline(language, cache_dir=cacheDir)

        print("Tagging {lang} data with Trankit (might take a while)...".format(lang=sl))
        newposlines = {}
        for line in tqdm.tqdm(sourcelines):
            # print(line[1])
            try:
                newposlines[line[0]] = [[t['text'], t['upos']] for t in p.posdep(line[1], is_sent=True)['tokens']]
            except:
                print(line[0], line[1]) # some verses are missing/renumbered

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

        def get_ratios(dc, k, n, wd, l, app1, app2):
            if any(x in wd[1] for x in l):
                if dc[k][n][0] == wd[0]:
                    if dc[k][n][1] in l:
                        app1.append(1)
                    else:
                        app2.append(1)
                else:
                    print(wd[0], dc[k][n][0])

        print("Getting correspondences between {lang} data in PBC and Trankit...".format(lang=sl))
        for key, sent in sourcedict.items():
            for num, words in enumerate(sent):
                get_ratios(newposlines, key, num, words, nslist, correctns, incorrectns)
                get_ratios(newposlines, key, num, words, onlist, cns, ins)
                get_ratios(newposlines, key, num, words, proplist, cps, ips)
                get_ratios(newposlines, key, num, words, pronlist, cpns, ipns)
                get_ratios(newposlines, key, num, words, vslist, correctvs, incorrectvs)
                get_ratios(newposlines, key, num, words, ovlist, cvs, ivs)
                get_ratios(newposlines, key, num, words, auxlist, cas, ias)

        print("Language:", sl, trlangs[sl][0])
        print("Ratio of corresponding nouns", len(correctns)/(len(correctns)+len(incorrectns)))
        print("Ratio of corresponding verbs", len(correctvs)/(len(correctvs)+len(incorrectvs)))

        dfdict[sl] = {"Language": trlangs[sl][0], "Ratio of corresponding nouns": len(correctns)/(len(correctns)+len(incorrectns)), "Ratio of corresponding verbs": len(correctvs)/(len(correctvs)+len(incorrectvs)), "Only nouns": len(cns)/(len(cns)+len(ins)), "Only propns": len(cps)/(len(cps)+len(ips)), "Only prons": len(cpns)/(len(cpns)+len(ipns)), "Only verbs": len(cvs)/(len(cvs)+len(ivs)), "Only auxs": len(cas)/(len(cas)+len(ias))}
    df = pd.DataFrame.from_dict(dfdict, orient='index')
    return df
