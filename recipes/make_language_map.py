import os, json, matplotlib # standard packages for data, plotting
import pandas as pd # dataframe package
import colorcet as cc # color package
import seaborn as sns # another plotting package
from html2image import Html2Image # a package for getting images from html
tempdir = "./tmp"
hti = Html2Image(temp_path=tempdir) # to convert the html to a png file we create a temp dir
import lingtypology # this package handles a lot of the mapping functions

stats = "../scripts/data/output/stats_All.xlsx" # the file of stats extracted from the dataset
df = pd.read_excel(stats) # read the file with stats on word order
isolist = df['index'].fillna('nan').to_list() # get the iso codes - "nan" is imported by `pandas` as NaN so we replace it
print(len(isolist)) # there should be 1597 languages (we exclude the conlangs)
# the `gdict` below gives us ISO to Glottocode mappings not present in the `lingtypology` package
gdict = {'msa': 'mala1479', 'oji': 'ojib1241', 'nan': 'minn1241', 'aze': 'nort2697', 'nwx': 'newa1245', 'est': 'esto1258', 'zho': 'comm1247'}
glist = [] # a list to store the Glottocodes
for iso in isolist:
	gcode = lingtypology.glottolog.get_glot_id_by_iso(iso) # get the Glottocode using our ISOs
	if gcode:
		glist.append(gcode)
	else:
		glist.append(gdict[iso])

# the following ISO codes are not mapped to a corresponding Glottocode, so their family 
# affiliations have been manually added to the `lineages` dictionary:
# msa (Malay), oji (Ojibwa), nan (Min Nan Chinese), aze (Azerbaijani), nwx (Newari), est (Estonian), zho ([Common] Chinese)

# load the lineage information that is present in Glottolog (as of 3 June 2025)
linfile = "../scripts/checks/glottolog/lineages.json"
with open(linfile) as f:
	# load the json file with lineages and ISO codes from Glottolog, stored in json format
	lineages = json.load(f)

# `lineages` is a dictionary of all the high-level lineages (and isolates) identified
# by Glottolog scholars, with ISO codes, names, lat, long and general location
# the keys of this dictionary are the Glottocode for the family, followed by a tab
# character and the name of the family
famdict = {} # dict to store family info by ISO code
for k, v in lineages.items():
	print(k)
	for key in v.keys():
		if 'isolate' in k:
			famdict[key] = 'isolate'
		else:
			famdict[key] = k

# let's get the list of features (in this case language family affiliation)
flist = [famdict[x].split("\t")[-1] for x in isolist]
# let's get a set of unique colors for our features
palette = sns.color_palette(cc.glasbey, n_colors=len(set(flist)))
palette = [matplotlib.colors.rgb2hex(c) for c in palette] # convert them to hex format

# here we create a map of languages based on Glottocodes
m = lingtypology.LingMap(glist, glottocode=True)
m.start_location = (20, 20) # set the start location
m.start_zoom = 2.5 # set the zoom level
m.add_features(flist, colors=palette) # color the languages by family
m.add_popups(flist) # add the language family affiliation to the popups
m.legend=False # 117 colors is a bit much for the legend, so leave the legend off
m.create_map() # create the map
m.save('map.html') # save it to html
# m.save_static(fname="map.png") # requires `geckodriver`

# produce a screenshot of the html
hti.screenshot(
    html_file='map.html',# css_file='blue_background.css',
    save_as='map.png'
)
# cleanup
os.rmdir(tempdir)
os.remove('map.html')