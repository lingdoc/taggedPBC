import pandas as pd
import os, json
from HLR import HierarchicalLinearRegression
from sklearn.preprocessing import LabelEncoder

# filen = "glottolog/All_comparisons_imputed_families.xlsx"
# complete = "../data/output/All_comparisons_imputed.xlsx"

def get_families(filen, complete, linfile):
     df = pd.read_excel(complete)
     print(len(df))
     df['index'] = df['index'].fillna('nan') # when pandas imports the spreadsheet it thinks this ISO code is NaN

     ind = df['index'].to_list()
     print(len(ind)) # this is the number of unique ISO codes in our dataset

     with open(linfile) as f:
         lineages = json.load(f) # load the json file with lineages and ISO codes from Glottolog, stored in json format
     
     # create a dict with the lineages present in our dataset
     indict = {}
     indict = {y: [k, v[y][1], v[y][2], v[y][3]] for k, v in lineages.items() for y in v.keys() if y not in indict.keys()}
     print("Number of lineages in the data:", len(indict))
     # print(len(df))
     print(df.head())
     # create a new column with the family line for each ISO code
     df["Family_line"] = [indict[x][0].split("\t")[1] for x in df['index']]
     # create new colums with latitude, longitude, macroarea for each ISO code
     df["latitude"] = [indict[x][1] for x in df['index']]
     df["longitude"] = [indict[x][2] for x in df['index']]
     df["macroarea"] = [indict[x][3] for x in df['index']]
     print(df['Family_line'])
     df.to_excel(filen)

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

le = LabelEncoder()

# function to convert categorical to numeric
def fit_transform_cats(df, col1, col2):
     le.fit(df[col1])
     # print(list(le.classes_))
     df[col2] = list(le.transform(df[col1]))
     # print(df[col2].value_counts())

def run_HLR(df, X, y, name, folder):
     # Initiate the HLR object (missing_data and ols_params are optional parameters)
     hreg = HierarchicalLinearRegression(df, X, y, ols_params=None)

     print("\n"+name+" results:")
     # Generate a summarised report of HLR
     summ = hreg.summary()
     outfile = folder+"HLR_results_"+name+"_tPBC"
     summ.to_excel(outfile+".xlsx") # these are the full statistical results
     cols = ['Model Level', 'N (observations)', 'F-value', 'P-value (F)', 'F-value change', 'P-value (F-value change)']#, 'Std Beta coefs'
     tsumm = summ[cols]
     tsumm.columns = ['Model', 'N (obs)', 'F-val', 'P-val (F)', 'F-val change', 'P-val (F-val change)']#, 'Std Betas'
     print(tsumm.head())
     tsumm.to_csv(outfile+".csv") # these are the main statistical results

     # # Run diagnostics on all the models and display in terminal
     # hreg.diagnostics(verbose=True)

     # # Different plots (see docs for more)
     # fig1 = hreg.plot_studentized_residuals_vs_fitted()
     # fig2 = hreg.plot_qq_residuals()
     # fig3 = hreg.plot_influence()
     # fig4 = hreg.plot_std_residuals()
     # fig5 = hreg.plot_histogram_std_residuals()
     # fig_list = hreg.plot_partial_regression()