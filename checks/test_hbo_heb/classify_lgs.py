# Import libraries and classes required for this example:
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectPercentile, chi2
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
import pandas as pd
from collections import Counter

# these are the numerical feature columns we will use for our classifier
numerical_features = ['Nlen_freq', 'Vlen_freq', 'NVlenFreqRatio', 'NVlenFreqDiff']
# build a pipeline with a scaler for numeric values
numeric_transformer = Pipeline(
	steps=[("scaler", StandardScaler())]
	)
# these are the categorical feature columns
categorical_features = ['Longer_Freq']
# build a pipeline to encode categorical features as binary
categorical_transformer = Pipeline(
    steps=[
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ("selector", SelectPercentile(chi2, percentile=50)),
    ]
)
# use the preprocessor to handle multiple columns as input features
preprocessor = ColumnTransformer(
	transformers=[("num", numeric_transformer, numerical_features),
        ("cat", categorical_transformer, categorical_features),
        ]
	)

le = LabelEncoder() # label encoder to make it easier to convert between numbers/labels

# a function to add our categorical variable (whether nouns or verbs are longer)
def eval_len(df, ncol, vcol, new):
    df.loc[df[ncol] > df[vcol], new] = 'N'
    df.loc[df[ncol] < df[vcol], new] = 'V'
    df.loc[df[ncol] == df[vcol], new] = 'N'

def get_train_data(data):
	# convert dataset to a pandas dataframe
	dataset = pd.read_excel(data)
	# reduce dataset to the following columns
	names = ['index', 'Nlen', 'Vlen', 'Nlen_freq', 'Vlen_freq', 'N1ratio-NsVs', 'N1ratio-ArgsPreds', 'Noun_Verb_order']
	dataset = dataset[names]
	# compute ratio
	dataset['NVlenFreqRatio'] = dataset['Nlen_freq']/dataset['Vlen_freq']
	# compute difference
	dataset['NVlenFreqDiff'] = dataset['Nlen_freq']-dataset['Vlen_freq']
	# add categorical columns
	eval_len(dataset, 'Nlen_freq', 'Vlen_freq', 'Longer_Freq')

	print(dataset.head()) # view the first 5 rows
	print(len(dataset)) # view the length
	dataset = dataset[dataset['index'] != 'heb'] # remove Modern Hebrew from the dataset, since we'll be predicting it later

	# use the label encoder to convert our word orders to classes
	le.fit(dataset['Noun_Verb_order'])
	print(list(le.classes_))
	dataset['Class'] = list(le.transform(dataset['Noun_Verb_order']))
	print(dataset.columns)
	# Assign values to the X and y variables
	print(numerical_features+categorical_features)
	X = dataset[numerical_features+categorical_features]
	y = dataset['Class']

	return X, y

# a function to instantiate the classifier pipeline
def get_pipe(preprocessor, classifier):
	clf = Pipeline(
	    steps=[("preprocessor", preprocessor), ("classifier", classifier)]
	)
	return clf

# a function to train and test the classifier on data
def test_clf(X, y, preprocessor, clf, name):
	clf = get_pipe(preprocessor, clf)

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

	clf.fit(X_train, y_train)
	score = clf.score(X_test, y_test)
	print("{name} model score: {score:.3f}".format(name=name, score=score))

# a function to train the classifier on all data
def train_clf(X, y, preprocessor, clf, name):
	clf = get_pipe(preprocessor, clf)
	clf.fit(X, y)
	return clf

# a function to get the data we want to predict on (from the UD corpora)
def get_predict_data(original):
	df = pd.read_excel(original)
	# compute additional dimensions for data
	df['NVlenFreqRatio'] = df['Nlen_freq']/df['Vlen_freq']
	df['NVlenFreqDiff'] = df['Nlen_freq']-df['Vlen_freq']
	# add categorical data
	eval_len(df, 'Nlen_freq', 'Vlen_freq', 'Longer_Freq')
	# print(df.head())
	# print(len(df))
	return df

# a function to train on (X, y) and predict on `df` using the trained classifier
def train_predict(df, classifiers, X, y):
	# train the classifier and predict on data
	predictions = []
	for clf in classifiers.keys():
		model = train_clf(X, y, preprocessor, classifiers[clf], clf)
		preds = list(model.predict(df))
		predictions.append(preds)

	# the code below averages the predictions (if using an ensemble method)
	# or converts the array to a list (if using a single classifier)
	print(predictions)
	finalpreds = []
	for cl in list(range(len(predictions[0]))):
		avgs = []
		for z in list(range(len(classifiers))):
			avgs.append(predictions[z][cl])
		avgs = round(sum(avgs)/len(avgs))
		finalpreds.append(avgs)
	print(len(finalpreds))

	print(Counter(finalpreds))

	df["Noun_Verb_order"] = list(le.inverse_transform(finalpreds))
	print(df.head())

	return df

