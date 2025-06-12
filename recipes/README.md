# Recipes for working with the *taggedPBC*

This folder contains Python scripts that illustrate how to access data in the *taggedPBC*. Scripts are listed and described briefly below.

`get_words_by_family.py` illustrates how to get information from the tagged corpora using a list of ISO codes.

- In this example, we first identify two language families from Glottolog that we want to compare: Kartvelian and Nakh-Daghestanian. It is possible, given that languages from these two families are located in the Caucasus region, that there are shared terms across different groups of these languages.
- Although there are some major concerns here with the validity of identifying overlaps with this particular dataset (romanization of orthography, questions regarding proper identification of word classes, etc.), it serves to illustrate how such comparisons can be made.
- In this case, we can see that there are 5 languages identified by Glottolog (as of 3 June 2025) in the two language families, all of which are represented by an individual corpus in the *taggedPBC*. This means that we can extract information on various parts of speech and find their intersecting values between the respective corpora.
- We can make minor adjustments to the code to get/compare different parts of speech between languages, or simply look for all shared word forms between the different corpora. Finding the intersection between words tagged as "NOUN" between particular language pairs (i.e. Lezgian [lez] and Chechen [che]) gives the following output:

  ```Between Lezgian & Chechen: khalk, lam, dustar, chan, tur, sha, masa, tazh, barkalla```
- Additional/improved annotations would increase the kind of comparisons that could be made and crosslinguistic information that could be extracted.