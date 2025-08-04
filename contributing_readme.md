## Contributing guidelines

As noted in other documents, the main aim of this repository is to provide a baseline dataset of parallel annotated corpora for crosslinguistic investigations. A secondary aim is to allow for ongoing annotation of corpora to support NLP for low-resource languages. As annotations are improved it is hoped that this will allow for more detailed comparisons and linguistic insights.

One way to improve the annotations is for specialists to manually annotate parts of speech and gloss the text. If you are a specialist or native speaker who would like to support this effort, please get in touch by opening an issue or sending an email to one of the maintainers, or simply download the corpus for the language you want to work on and start annotating.

### Guidelines for annotation

To facilitate annotation, there are two subsets of verses that have been identified for broad coverage of POS tags. The first is a set of 21 verses, and the second is a set of an additional 100 verses. The first set of 21 verses are those that contain 12-14 of the POS tags present in the *taggedPBC* corpora, while the second set of 100 verses are those with between 6-11 of the POS tags. This means that annotating the first set of 21 verses gives a minimal set of verses with decent coverage for training a POS tagger for a given language. This can then assist in tagging the second set of 100 verses. With 121 verses, we have a decent beginning for tagging remaining verses in a given corpus, aided by automatic taggers.

The following is the list of verses (following PBC convention) with 12-14 POS terms:

```
# there are 21 verses with 12-14 terms
["40006024", "40018012", "40020021", "40026002", "40026061", "40028016", "41002023", "41012032", "41014037", "42004002", "42016013", "42024018", "43001039", "43003016", "44002030", "44009038", "44011011", "44021034", "47012002", "62004009", "63001005"]
```

The following is the list of verses (following PBC convention) with 6-11 POS terms:

```
# there are 100 verses with 6-11 terms
["40009020", "40009027", "40010023", "40011001", "40013008", "40014017", "40015034", "40015037", "40019005", "40021024", "40021028", "40022025", "40024041", "40025018", "40025040", "40026015", "40026034", "40026040", "40026051", "40027021", "40027063", "41004008", "41006007", "41006038", "41006043", "41008005", "41008008", "41008014", "41010037", "41011029", "41012006", "41012007", "41012020", "41012022", "41013002", "41014010", "41014013", "41014018", "41014047", "41014061", "42002046", "42006012", "42008022", "42008042", "42009013", "42009028", "42009032", "42011026", "42015004", "42017002", "42017004", "42017024", "42017035", "42018010", "42020031", "42022030", "42022050", "42023033", "42024035", "43001040", "43002019", "43006010", "43006019", "43008009", "43011009", "43011050", "43018039", "43019023", "43020012", "44001010", "44004004", "44007029", "44007036", "44009033", "44010003", "44010007", "44010011", "44017002", "44019008", "44019010", "44023017", "44024021", "46008004", "48001018", "48002001", "49005031", "49006008", "51004009", "53001003", "58008013", "66001012", "66005014", "66007001", "66008002", "66009018", "66010003", "66011011", "66013011", "66021014", "66022008"]
```