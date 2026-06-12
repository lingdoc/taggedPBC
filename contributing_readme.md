## Contributing guidelines

As noted in other documents, the main aim of this repository is to provide a baseline dataset of parallel annotated corpora for crosslinguistic investigations. A secondary aim is to allow for ongoing annotation of corpora to support NLP for low-resource languages. As annotations are improved it is hoped that this will allow for more detailed comparisons and linguistic insights.

One way to improve the annotations is for specialists to manually annotate parts of speech and gloss the text. If you are a specialist or native speaker who would like to support this effort, please get in touch by opening an issue or sending an email to one of the maintainers, or simply download the corpus for the language you want to work on and start annotating. Some suggestions on verses to start with are given in [Guidelines for annotation](#guidelines-for-annotation). Basic instructions for downloading and annotating individual corpora are found under [Getting started 1](#getting-started-1), and sparse checkout instructions for the git-oriented user can be found under [Getting started 2](#getting-started-2).

### Getting started 1

To get started on editing/updating a corpus, the simplest way is simply to download the corpus directly. The base directory is [`corpora/conllu/`](corpora/conllu/) - this is where the original *taggedPBC* corpora are stored. Updated and edited corpora can be found under [`corpora/conllu-retagged/`](corpora/conllu-retagged/). The subfolder [`annotations/`](corpora/conllu-retagged/annotations/) contains semi-automated annotations (complete or partial) for various corpora, and [`autoUD/`](corpora/conllu-retagged/autoUD/) contains annotations derived from UD corpus-trained taggers. I recommend checking these subfolders for your language of interest first, as these should require less correction than the base corpora.

You can also find a direct link to each base corpus in the *taggedPBC* via [the README file in the `corpora` subfolder](corpora/README.md), which you can search for ISO code and language name as you would a webpage (CTRL+F).

#### Editing the corpus

Once you have downloaded the file to your computer, you can edit it as you would any other text or [CoNLL-U](https://universaldependencies.org/format.html) file. There are various [editing options and tools](https://universaldependencies.org/tools.html) that you can use to work with the files. There are also some [example scripts in this repository](recipes/) that you can use to convert CoNLL-U files to other formats and back.

#### Uploading the edited corpus

After you have made edits, I recommend opening a pull request to add your newly updated corpus to the `corpora/conllu-retagged/annotations/` folder. You can do this manually via the web by 1) navigating to the relevant directory on the Github site, 2) uploading the file, 3) following the instructions.

#### Reasons for maintaining original files

There are a few reasons for maintaining the original corpus files along with re-annotated files. The main reason is to track relevant updates so as not to duplicate effort. Another reason is to be able to credit contributors and support collaboration. A third reason is to differentiate different kinds of contributions and to observe changes over time or which may be due to different analyses.

### Getting started 2

If you are more technically inclined, the slightly more involved process below will allow you to clone the
corpus of interest locally to your own computer, copy it to a relevant directory for editing, and track changes
as you edit before pushing the final version for review. Keep in mind that these instructions assume that you
only want a single file. To checkout multiple files at once, you likely want a `sparse checkout` in cone mode instead.

#### Setting up sparse checkout

The process below illustrates how to get a local copy of the relevant corpus on your computer without downloading
the complete *taggedPBC*. Here we are only interested in working on one language, editing it locally, and then
being able to easily push changes to the Github repository for review. This process uses your local terminal
and a text editor, which may require a bit more technical familiarity.

In a terminal, run the following commands.

```bash
# clone without checkout, and no blobs, so as not to download anything
$ git clone --filter=blob:none --no-checkout https://github.com/lingdoc/taggedPBC
# navigate to the directory
$ cd taggedPBC
# disable cone mode (cone mode forces entire directories and root files to download, even if not displayed)
$ git sparse-checkout init --no-cone
```

#### Add the corpus file from the online repo and download via terminal

In the same directory, add the file(s) that you want. Keep in mind that the web link will not be the same as the internal repository path, i.e. for the Aymara taggedPBC corpus, the following link:
`https://github.com/lingdoc/taggedPBC/blob/main/corpora/conllu/ayr-eng-tagged-ayr-x-bible_parsed.conllu`
would be shortened to:
`corpora/conllu/ayr-eng-tagged-ayr-x-bible_parsed.conllu`
(removing the first part `https://github.com/lingdoc/taggedPBC/blob/main/`)
and this gives us the following local command in the terminal:

```bash
# set the single file to checkout using sparse checkout
$ git sparse-checkout set corpora/conllu/ayr-eng-tagged-ayr-x-bible_parsed.conllu
```

Then to download only this file, run the following command:
```bash
$ git checkout
```

#### Create new location for editing

Now you can create the folder (with subfolders) where you will be uploading the new file:

```bash
# command structure: (make directory command) (path flag) (new directory tree)
$ mkdir -p corpora/conllu-retagged/annotations/complete/
```

Then copy over the file that you will be editing. Change the relevant path for your particular file - note
that here I have renamed the file at the location where I will be editing it, i.e.:

```bash
# command structure: (copy command) (source path) (destination path)
$ cp corpora/conllu/ayr-eng-tagged-ayr-x-bible_parsed.conllu corpora/conllu-retagged/annotations/complete/ayr-1884_verses_annotated.conllu
```

And then add the new file path to the sparse checkout list:

```bash
# command structure: (git command) (sparse-checkout flag) add (path to added file)
$ git sparse-checkout add corpora/conllu-retagged/annotations/complete/ayr-1884_verses_annotated.conllu
```

Also add this file to your local git repo in order to track changes:

```bash
# command structure: (git command) add (path to added file)
$ git add corpora/conllu-retagged/annotations/complete/ayr-1884_verses_annotated.conllu
```

And commit your changes locally with a message:
```bash
# command structure: (git command) commit (message flag) (message within quotes)
$ git commit -m "New ayr (Aymara) corpus for editing"
```

Now you can follow the normal add/commit git workflow as you work on your annotations. Simply edit your
file in a text editor of your choice and save your changes. You can add the file and commit changes whenever
you like, i.e. in order to keep track of major changes. When you are ready to push your final changes and
create a pull request, you can use the following terminal command from within the repository:

```bash
# final push to online repository
$ git push
```


### Guidelines for annotation

To facilitate annotation, there are two subsets of verses that have been identified for broad coverage of POS tags. The first is a set of 21 verses, and the second is a set of an additional 100 verses. The first set of 21 verses are those that contain 12-14 of the POS tags present in the *taggedPBC* corpora, while the second set of 100 verses are those with between 6-11 of the POS tags. This means that annotating the first set of 21 verses gives a minimal set of verses with decent coverage for training a POS tagger for a given language. This can then assist in tagging the second set of 100 verses. With 121 or so verses, we have a good beginning for tagging remaining verses in a given corpus, aided by automatic taggers.

The following is the list of verses (following PBC convention) with 12-14 POS terms:

```
# there are 21 verses with 12-14 terms
["40006024", "40018012", "40020021", "40026002", "40026061", "40028016", "41002023", "41012032", "41014037",
 "42004002", "42016013", "42024018", "43001039", "43003016", "44002030", "44009038", "44011011", "44021034",
 "47012002", "62004009", "63001005"]
```

The following is the list of verses (following PBC convention) with 6-11 POS terms:

```
# there are 100 verses with 6-11 terms
["40009020", "40009027", "40010023", "40011001", "40013008", "40014017", "40015034", "40015037", "40019005",
 "40021024", "40021028", "40022025", "40024041", "40025018", "40025040", "40026015", "40026034", "40026040",
 "40026051", "40027021", "40027063", "41004008", "41006007", "41006038", "41006043", "41008005", "41008008",
 "41008014", "41010037", "41011029", "41012006", "41012007", "41012020", "41012022", "41013002", "41014010",
 "41014013", "41014018", "41014047", "41014061", "42002046", "42006012", "42008022", "42008042", "42009013",
 "42009028", "42009032", "42011026", "42015004", "42017002", "42017004", "42017024", "42017035", "42018010",
 "42020031", "42022030", "42022050", "42023033", "42024035", "43001040", "43002019", "43006010", "43006019",
 "43008009", "43011009", "43011050", "43018039", "43019023", "43020012", "44001010", "44004004", "44007029",
 "44007036", "44009033", "44010003", "44010007", "44010011", "44017002", "44019008", "44019010", "44023017",
 "44024021", "46008004", "48001018", "48002001", "49005031", "49006008", "51004009", "53001003", "58008013",
 "66001012", "66005014", "66007001", "66008002", "66009018", "66010003", "66011011", "66013011", "66021014",
 "66022008"]
```
