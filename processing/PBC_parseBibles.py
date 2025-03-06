##############################################################
#
# INPUT - bibles original bible corpus from Cysouw,
# OUTPUTS - (to stdout) - all the filenames, ISO lang codes as per header (sometimes conflict w/ filename), year, and title
# OUTPUTS - to outDirectory - bibles without the header and verse info.
# Currently it grabs the new testament only since that has wider coverage than old+new
#
# This script is a modification of the original `bibleParse.py` code, written to do
# additional romanization for various translations in non-roman scripts.
#
##############################################################

import re, sys, glob, os, random, tqdm
import unicodedataplus as ud
from uroman import uroman # for romanization
from fugashi import Tagger as ftagger # for tokenizing Japanese
from khmernltk import word_tokenize as khmtok # for tokenizing Khmer
import jieba # for tokenizing Mandarin
import pyidaungsu as pds # for tokenizing Karen
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_romanization(line):
	"""
	For each verse number and line, romanize the script. Expects a list
	of lists as input, in the format [[[num, 'text'], [iso]], [[num, 'text'], [iso]]]
	where each entry contains a number and text, followed by an ISO 639-3 code.
	"""
	number = line[0][0]
	text = line[0][1]
	# Processing...
	roman = uroman(text, language=line[1])
	return number, roman

jtagger = ftagger('-Owakati') # choose this dictionary for tokenizing Japanese

# romanized_ru = uroman("Да это транслит")
# # romanized_ru == "Da eto transit"
#
# # Provide language tag for better results (everything `langcodes` understands is accepted)
# romanized_zh = uroman("关 服务 高端 产品 仍 处于 供不应求 的 局面", language="zh")
#
# # Provide `chart=True` to get rich alignment between original and romanized texts in JSON
# chart = uroman(" القارة وتمتد من المحيط الأطلسي في الشرق إلى المحيط ", language="ar", chart=True)

print(sys.argv)
input_directory = ['corpus'] # directory where the corpus is located
outDirectory = 'parsed' # directory for the newly parsed files
epiDirectory = 'epi' # directory for the romanized files
output_filename = 'bibles_parsed_info.txt'
extension ="txt"
# here we are getting just the New Testament portions
verseStart 	= 40001001
verseEnd 	= 66022021
path = os.getcwd() #set path to current directory

shorter_portions = []
isos = {}
#read in files
fileList = []
for dir in input_directory:
	fileList.extend(glob.glob(os.path.join(path, dir, '*'+extension)))

header = "\t".join(['filename', 'numVerses', 'proposed_language_name', 'proposed_ISO', 'year', 'script', 'title'])
print(header)

for curFile in tqdm.tqdm(fileList):
	# print(curFile)
	fiso = curFile.split("/")[-1].split("-")[0]
	tran = curFile.split("/")[-1].split("-")[-1]
	print(fiso)
	if fiso not in isos.keys():
		isos[fiso] = [tran]
	else:
		isos[fiso].append(tran)

	inputfile = open(curFile,'r')

	allText = inputfile.readlines()
	textToWrite=[]
	someChars = []
	headerKey = headerValue = proposed_language_name = proposed_ISO = year = title = 'NA'
	for numLine,curLine in enumerate(allText):
		if '#' in curLine and numLine<12:  #probably in the header
			curLine = re.sub('\s+', ' ', curLine)
			try:
				headerKey,headerValue = curLine.split(":")[0:2] #URLs have colons too
			except:
				pass #can happen if there are hashtagged versenumbers in the beginning which some files have
			headerKey = re.sub('#\s', '', headerKey)
			if 'name' in headerKey and 'language' in headerKey:
				proposed_language_name = headerValue
			elif 'ISO' in headerKey:
				proposed_ISO = headerValue
			elif 'year_short' in headerKey:
				year = headerValue.split('/')[0]
				if year=='':
					year='NA'
			elif 'title' in headerKey:
				title = headerValue
			else:
				pass
		else: #we're in the body
			verseNum = verseText = ''
			try:
				verseNum,verseText = curLine.split('\t')
				# print(verseNum, verseText)
				unicodeVerseText = verseText#unicode(verseText,'utf-8')
				# print(unicodeVerseText)
				someChars.append(random.sample(unicodeVerseText,3)[0])
			except:
				pass #can happen if there's a stray newline
			try:
				verseNum = int(re.sub('#', '', verseNum))
			except:
				pass
				# print('### Integer conversion failed: ', os.path.basename(curFile), verseNum, curLine)
			if isinstance(verseNum, int):
				if verseNum >= verseStart and verseNum <= verseEnd:
					textToWrite.append([str(verseNum), verseText]) # include the verse number so we can link them up later
			else:
				pass

			numVerses = len(textToWrite)
	# check the script characters to see if it needs to be romanized
	scriptGuesses = [ud.script(curChar) for curChar in someChars]
	scriptGuesses = [scriptGuess for scriptGuess in scriptGuesses if scriptGuess !="Common"]
	# guess the script by taking the most common
	mostCommonScriptGuess = max(set(scriptGuesses), key=scriptGuesses.count)
	# set the filenames for the output files
	parsedfilen = outDirectory+'/'+os.path.basename(curFile)[0:-4]+'_parsed.txt'
	romandfilen = epiDirectory+'/'+os.path.basename(curFile)[0:-4]+'_parsed_romanized.txt'
	# don't overwrite parsed files
	if not os.path.isfile(romandfilen):
		# print some info about the current file
		print("\t".join([os.path.basename(curFile)[0:-4], str(numVerses), proposed_language_name, proposed_ISO, year, mostCommonScriptGuess, "\""+title+"\""]))
		if numVerses > 3000: # only get texts with many verses
			outputfile = open(parsedfilen,'w')
			for i in textToWrite:
				outputfile.write("\t".join(i)) # write the verse numbering along with the verse
			# check for particular ISOs to use language-specific tokenizers
			if mostCommonScriptGuess not in ["Latin"]:
				if fiso == 'jpn':
					textToWrite = [[x[0], jtagger.parse(x[1])] for x in textToWrite]
				elif fiso == 'khm':
					textToWrite = [[x[0], " ".join(khmtok(x[1], return_tokens=True))] for x in textToWrite]
				elif fiso == 'ksw':
					textToWrite = [[x[0], " ".join(pds.tokenize(x[1], lang="karen", form="word"))] for x in textToWrite]
				elif fiso == 'cmn':
					textToWrite = [[x[0], " ".join(jieba.lcut(x[1]))] for x in textToWrite]

				# create a list of data to parallelize the processing
				fisolist = [fiso for n in list(range(len(textToWrite)))]
				zipped = [list(x) for x in zip(textToWrite, fisolist)]
				print(fiso)
				# do the romanization
				with ThreadPoolExecutor() as executor:
					romans = list(tqdm.tqdm(executor.map(get_romanization, zipped), total=len(zipped)))
				with open(romandfilen, "w", encoding="utf-8") as stream:
					for line in romans:
						stream.write(f"{line[0]}\t{line[1]}\n")
				print(f"Romanized {fiso}-{mostCommonScriptGuess} for {os.path.basename(curFile)[0:-4]}")
		else:
			# store info for languages with fewer than 3k verses
			shorter_portions.append([str(numVerses), proposed_language_name, proposed_ISO])
	# clean up
	inputfile.close()
	outputfile.close()

allisos = len(isos)

isos = {k: v for k, v in isos.items() if len(v) > 1}

for short in shorter_portions:
	print("\t".join(short))
print(len(shorter_portions))

print(isos)
print("\nNumber of languages with multiple translations:", len(isos))
print("\nTotal unique isos:", allisos)
