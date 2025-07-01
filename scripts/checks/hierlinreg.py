import pandas as pd
import os, json
from HLR import HierarchicalLinearRegression
from sklearn.preprocessing import LabelEncoder

# filen = "glottolog/All_comparisons_imputed_families.xlsx"
# complete = "../data/output/All_comparisons_imputed.xlsx"

# a function to get lineages from one file and add them to a dataframe
def get_families(complete, linfile):
     # print(len(complete))
     complete['index'] = complete['index'].fillna('nan') # when pandas imports the spreadsheet it thinks this ISO code is NaN

     ind = complete['index'].to_list()
     print("Number of unique ISO codes in the data:", len(ind))

     with open(linfile) as f:
         lineages = json.load(f) # load the json file with lineages and ISO codes from Glottolog, stored in json format
     
     # create a dict with the lineages present in our dataset
     indict = {}
     indict = {y: [k, v[y][1], v[y][2], v[y][3]] for k, v in lineages.items() for y in v.keys() if y not in indict.keys()}
     print("Number of lineages in the Glottolog data:", len(indict))
     # print(len(complete))
     # print(complete.head())
     # create a new column with the family line for each ISO code
     complete["Family_line"] = [indict[x][0].split("\t")[1] for x in complete['index']]
     # create new colums with latitude, longitude, macroarea for each ISO code
     complete["latitude"] = [indict[x][1] for x in complete['index']]
     complete["longitude"] = [indict[x][2] for x in complete['index']]
     complete["macroarea"] = [indict[x][3] for x in complete['index']]
     # print(complete['Family_line'])
     complete.set_index('index', inplace=True) # set index
     compdict = complete.to_dict(orient='index') # convert to dict
     # dict below contains updated info missing from Glottolog
     newdictinfo = {
               'uth': {"Family_line": "Atlantic-Congo", "latitude": 11.5, "longitude": 4, "macroarea": "Africa"}, 
               'ukk': {"Family_line": "Austroasiatic", "latitude": 21.183333, "longitude": 100.366667, "macroarea": "Eurasia"}, 
               'xis': {"Family_line": "Dravidian", "latitude": 24.46, "longitude": 86.47, "macroarea": "Eurasia"}, 
               'fat': {"Family_line": "Atlantic-Congo", "latitude": 5.5, "longitude": -1, "macroarea": "Africa"}, 
               'ltg': {"Family_line": "Indo-European", "latitude": 56.948889, "longitude": 24.106389, "macroarea": "Eurasia"},
                    }
     # loop through the dict and add info to the compdict if the keys exist
     for k, v in newdictinfo.items():
          if k in compdict.keys():
               for key in v.keys():
                    compdict[k][key] = newdictinfo[k][key]

     # convert back to dataframe
     complete = pd.DataFrame.from_dict(compdict, orient='index').reset_index()

     return complete

# largefams = ['Atlantic-Congo': 293, 'Austronesian': 277, 'Indo-European': 136, 'Sino-Tibetan': 106, 'Nuclear Trans New Guinea': 96, 'Otomanguean': 80, 'Afro-Asiatic': 57, 'Quechuan': 27, 'Uto-Aztecan': 27]

# function to filter families from the dataset based on criteria
def filter_families(df, listval):
     famdict = df["Family_line"].value_counts() # get the number of languages per family in the dataset
     if isinstance(listval, list):
          famdict2 = {k: v for k, v in famdict.items() if k in listval} # check whether the item is in the list
     elif isinstance(listval, int):
          famdict2 = {k: v for k, v in famdict.items() if v > listval} # check whether the values is greater than the int
     elif isinstance(listval, tuple):
          famdict2 = {k: v for k, v in famdict.items() if listval[1] > v > listval[0]} # check whether the values is greater than the int
     else:
          print(type(listval), "not supported.")

     return list(famdict2.keys())

def filter_lgs(df, families):
     familydf = df[df["Family_line"].isin(families)]
     familylist = familydf["index"].to_list()
     return familylist

def family_dict(df, families):
     familydf = df[df["Family_line"].isin(families)]
     famdict = familydf["Family_line"].value_counts()
     familydict = {}
     for k in famdict.keys():
          dftemp = df[df["Family_line"] == k]
          familydict[k] = dftemp["index"].to_list()
     return familydict


le = LabelEncoder()

# function to convert categorical to numeric
def fit_transform_cats(df, col1, col2):
     le.fit(df[col1])
     # print(list(le.classes_))
     df[col2] = list(le.transform(df[col1]))
     # print(df[col2].value_counts())

def run_HLR(df, X, y, name, folder, feedback=None, repl=False):
     # Initiate the HLR object (missing_data and ols_params are optional parameters)
     hreg = HierarchicalLinearRegression(df, X, y, ols_params=None)

     
     # Generate a summarised report of HLR
     summ = hreg.summary()
     outfile = folder+"HLR_results_"+name+"_tPBC"
     if repl:
          summ.to_excel(outfile+".xlsx") # these are the full statistical results
     cols = ['Model Level', 'N (observations)', 'F-value', 'P-value (F)', 'F-value change', 'P-value (F-value change)']#, 'Std Beta coefs'
     tsumm = summ[cols]
     tsumm.columns = ['Model', 'N (obs)', 'F-val', 'P-val (F)', 'F-val change', 'P-val (F-val change)']#, 'Std Betas'
     # print(tsumm.head())
     if repl:
          tsumm.to_csv(outfile+".csv") # these are the main statistical results
     if feedback:
          fdict = tsumm.set_index("Model").to_dict("index")
          return fdict
     else:
          print("\n"+name+" results:")
          print(tsumm.head())

     # # Run diagnostics on all the models and display in terminal
     # hreg.diagnostics(verbose=True)

     # # Different plots (see docs for more)
     # fig1 = hreg.plot_studentized_residuals_vs_fitted()
     # fig2 = hreg.plot_qq_residuals()
     # fig3 = hreg.plot_influence()
     # fig4 = hreg.plot_std_residuals()
     # fig5 = hreg.plot_histogram_std_residuals()
     # fig_list = hreg.plot_partial_regression()