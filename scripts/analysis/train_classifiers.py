# import libraries and classes
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectPercentile, chi2
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
import pandas as pd
from collections import Counter
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# a function to instantiate the classifier pipeline
def get_pipe(preprocessor, classifier):
	clf = Pipeline(
	    steps=[("preprocessor", preprocessor), ("classifier", classifier)]
	)
	return clf

# a function to test the classifier on known data
def test_clf(X, y, preprocessor, clf, name):
	clf = get_pipe(preprocessor, clf)

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

	clf.fit(X_train, y_train)
	score = clf.score(X_test, y_test)
	print("{name} model score: {score:.3f}".format(name=name, score=score))

# a function to train the classifier on all the data
def train_clf(X, y, preprocessor, clf, name):
	clf = get_pipe(preprocessor, clf)
	clf.fit(X, y)
	return clf

# a function to test a classifier using a dataset with features and coded classes
def test_classifier_on_df(filen, classifiers, original, target_col, num_feats=[], cat_feats=[]):
	"""
	filen: excel spreadsheet with the hand-coded data to train the classifier
	classifiers: a dict of classifiers to train on the data
	original: excel spreadsheet with unclassified data
	target_col: the spreadsheet column containing the classes for prediction
	num_feats: a list of columns containing numerical features for training
	cat_feats: a list of columns containing categorical features for training
	"""

	# read the hand-coded word order data
	dataset = pd.read_excel(filen)
	print(dataset.head())
	print(len(dataset))

	# use the label encoder to convert our word orders to classes
	le = LabelEncoder()
	le.fit(dataset[target_col])
	print(list(le.classes_))
	# make a new column which is the transformed classes
	dataset['Class'] = list(le.transform(dataset[target_col]))

	# feature columns for our classifier can be numeric (continuous) or categorical (discrete)
	# these are the numerical feature columns
	numerical_features = num_feats
	# these are the categorical feature columns
	categorical_features = cat_feats

	# Assign values to the X and y variables:
	X = dataset[numerical_features+categorical_features]
	y = dataset['Class']
	print(Counter(le.inverse_transform(y)))

	# build the pipeline to impute missing values and scales for numeric values
	# since our dataset isn't missing values, this isn't really necessary, but
	# a good practice anyway
	numeric_transformer = Pipeline(
		steps=[("imputer", SimpleImputer(strategy="median")),
				("scaler", StandardScaler())
				]
			)

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

	# test the classifier by training/validating with a split of the data
	for clf in classifiers.keys():
		test_clf(X, y, preprocessor, classifiers[clf], clf)

	# import data with unknown labels
	df = pd.read_excel(original)
	print(df.head())
	print(len(df))

	# create a new dataframe with only data from languages not coded for
	# word order in the typological databases
	unkst = [x for x in list(df['index']) if x not in list(dataset['index'])]
	print(len(unkst))
	unks = df[df['index'].isin(unkst)]

	print("There are {unknum} languages in the dataset that are not coded for {target_col}.".format(unknum=len(unks), target_col=target_col))
	print("There are {Xnum} languages in the dataset with codes for {target_col} from existing databases.".format(Xnum=len(X), target_col=target_col))

	# now train the classifier on all the coded languages and impute word order for the other languages
	predictions = []
	for clf in classifiers.keys():
		model = train_clf(X, y, preprocessor, classifiers[clf], clf)
		preds = list(model.predict(unks))
		predictions.append(preds)

	# If you wanted to link multiple classifiers in an ensemble you could
	# use the following code to combine their predictions. Some experiments
	# with a Decision Tree classifier gave different predictions (a larger
	# number of languages classed as "free") but manual checking of those
	# ISO codes showed that all such languages were actually "V1" - the code
	# assigned by the GNB classifier.
	finalpreds = [] # instantiate an empty list for final predictions
	# predictions are returned in an array, so get them and store them in a list
	for cl in list(range(len(predictions[0]))):
		avgs = []
		for z in list(range(len(classifiers))):
			avgs.append(predictions[z][cl])
		avgs = round(sum(avgs)/len(avgs))
		finalpreds.append(avgs)
	print(len(finalpreds))
	print(Counter(le.inverse_transform(finalpreds)))

	# get the final values from the predictions
	unks[target_col] = list(le.inverse_transform(finalpreds))

	# combine the predicted values with the database values
	dataset = pd.concat([dataset, unks])
	print(len(dataset))
	# print(dataset.columns)
	# language with iso 'nan' gets removed because python thinks it's NaN, so restore it here
	dataset['index'] = dataset['index'].fillna('nan')
	print(len(dataset))
	print(Counter(dataset[target_col]))
	print(len(dataset))

	return dataset
