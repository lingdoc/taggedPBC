import glob, os, json, tqdm

allfold = [x for x in glob.glob("../../ud-iso/*") if os.path.isdir(x)]

# go through the ISO-converted UD data
for testfold in tqdm.tqdm(allfold):
    iso = testfold.split("/")[-1]
    print(iso)
    # get all the conllu files
    filens = [x for x in glob.glob(testfold+"/*.conllu")]

    postagged = []
    # convert all sentences to a single set of POS tagged sentences
    for fn in filens:
        with open(fn) as f:
            tempfile = f.read()
            tempfile = tempfile.split("\n")
            lines = []
            trueline = []
            for line in tempfile:
                if line.startswith("#"):
                    if len(trueline) > 0:
                        lines.append(trueline)
                        trueline = []
                    else:
                        trueline = []
                else:
                    line = line.split("\t")
                    if len(line) > 1:
                        trueline.append((line[1], line[3]))

            postagged += lines
    print(len(postagged))
    # write the tagged sentences to a single file for each ISO
    FILE_PATH = "iso-tagged/"+iso+"_tagged.txt"
    with open(FILE_PATH, 'w') as output_file:
        json.dump(postagged, output_file)#, indent=1)
