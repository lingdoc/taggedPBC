# Recipes for working with the *taggedPBC*

This folder contains Python scripts that illustrate how to access data in the *taggedPBC*. Scripts are listed and described briefly below.

`get_words_by_family.py` illustrates how to get information from the tagged corpora using a list of ISO codes. It prints a list of shared nouns between languages in your Python terminal.

- In this example, we first identify two language families from Glottolog that we want to compare: Kartvelian and Nakh-Daghestanian. It is possible, given that languages from these two families are located in the Caucasus region, that there are shared terms across different groups of these languages.
- Although there are some major concerns here with the validity of identifying overlaps with this particular dataset (romanization of orthography, questions regarding proper identification of word classes, etc.), it serves to illustrate how such comparisons can be made.
- In this case, we can see that there are 5 languages identified by Glottolog (as of 3 June 2025) in the two language families, all of which are represented by an individual corpus in the *taggedPBC*. This means that we can extract information on various parts of speech and find their intersecting values between the respective corpora.
- We can make minor adjustments to the code to get/compare different parts of speech between languages, or simply look for all shared word forms between the different corpora. Finding the intersection between words tagged as "NOUN" between particular language pairs (i.e. Lezgian [lez] and Chechen [che]) gives the following output in the terminal:

  ```Between Lezgian & Chechen: khalk, lam, dustar, chan, tur, sha, masa, tazh, barkalla```
- Additional/improved annotations would increase the kind of comparisons that could be made and crosslinguistic information that could be extracted.


`make_language_map.py` illustrates how to plot features based on the dataset using a list of ISO codes. It produces an interactive html map using the `lingtypology` library.
- the code makes use of the language affiliations and geographical information available from Glottolog
- we can use this information to group languages and gather statistics about the languages found in the *taggedPBC*, such as the number of languages in each family, the number of families represented by a certain number of languages, etc:

```There are 56 families in the dataset represented by a single language
There are 52 families in the dataset represented by 2-9 languages: 211 total
There are 18 families in the dataset represented by 10-32 languages: 366 total
There are 7 families in the dataset represented by 70+ languages: 1289 total```