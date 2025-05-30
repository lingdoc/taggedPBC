# taggedPBC

**tldr**: POS-tagged verses from the Parallel Bible Corpus (PBC; [Mayer & Cysouw 2014](#1)), with Python code for extracting various metrics and making cross-linguistic comparisons.

> This repository is shared under a CC BY-NC-SA 4.0 license, and can be used solely for research purposes. Copyright of the selected verses of each translation is retained by the original copyright holders.

If you use this data, please cite the following source:

- Ring, Hiram. 2025. The *taggedPBC*: Annotating a massive parallel corpus for crosslinguistic investigations. https://doi.org/10.48550/arXiv.2505.12560 *[Submitted on 18 May 2025]*

The two folders in this repository contain corpus data and scripts to run various analyses.

- `corpora`: contains the actual POS-tagged data for a large number of (non-contiguous) parallel verses taken from New Testament translations in 1,599 languages of the PBC (including two conlangs: Esperanto and Klingon). The data is formatted as a `json` dict with the following keys:
	- `info`: general information about the data
	- `license`: information on permitted use and relevant copyright
	- `metadata`: the original PBC metadata
	- `tagged`: a list of lists, with the first item in each sublist being the verse number (following PBC convention) and the second being a list of tuples in [word, POS] format where `unk` represents unknown tags


- `scripts`: contains scripts to verify and analyze the data of the `taggedPBC`, with reference to particular papers (currently draft versions of submissions to journals). Refer to the `README` file in the subfolder for additional information.
	- Ring, Hiram. 2025. The *taggedPBC*: Annotating a massive parallel corpus for crosslinguistic investigations. https://doi.org/10.48550/arXiv.2505.12560 *[Submitted on 18 May 2025]*
	- Ring, Hiram. 2025. Word length predicts word order: "Min-max"-ing drives language evolution. https://doi.org/10.48550/arXiv.2505.13913 *[Submitted on 20 May 2025]*

The following table gives counts of verses per language in the corpora:

|Number of verses|Number of languages|
|--|--|
|1800+|1547|
|1500-1800|21|
|1000-1500|26|
|700-1000|5|
|**Total**|**1599**|

![Verse counts in corpora](scripts/data/output/plots_distr/hist-Verse_counts.png)



## References <a name="references"></a>

<a id="1">[1]</a>
Mayer, Thomas & Michael Cysouw. 2014. Creating a massively parallel Bible corpus. In Proceedings of the Ninth International Conference on Language Resources and Evaluation (LREC'14), pages 3158–3163, Reykjavik, Iceland. European Language Resources Association (ELRA). https://aclanthology.org/L14-1215/  
