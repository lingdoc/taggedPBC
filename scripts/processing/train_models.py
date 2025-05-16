import os, json, glob, time, nltk, torch, spacy, datetime, string, tqdm
from nltk.translate import AlignedSent, IBMModel2
import dill as pickle
from tokenizers import SentencePieceBPETokenizer
from transformers import AutoTokenizer

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') # if NLTK could utilize GPU that would make this faster
nlp = spacy.load("en_core_web_sm") # language model for English part of speech
model_checkpoint = "Helsinki-NLP/opus-mt-fr-en" # name of the model we're loading the tokenizer from

# add some additional characters to the standard punctuation
punct = string.punctuation+"“”‘’,"

# preprocess sentences using language-specific tokenizers (trained using Sentence Piece BPE)
def clean_sentences(sentences, tokenizer):
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip() # strip the newline
        ## the processes below were found to not be helpful and were abandoned, leaving in for future testing
        # sentence = sentence.lower() # lowercase
        # sentence = re.sub(r"[^a-zA-Z0-9]+", " ", sentence) # remove punctuation
        # sentence = ''.join([x for x in sentence if x not in punct])
        sentence = ' '.join(sentence.split())
        sentence = tokenizer.encode(sentence).tokens # get the tokens from the tokenizer
        cleaned_sentences.append(" ".join(sentence))#.strip()) # join the tokens
    return cleaned_sentences

# Train the Translation Model for each language (source) > English (target)
def train_translation_model(source_sentences, target_sentences):
    aligned_sentences = [AlignedSent(source.split(), target.split()) for source, target in zip(source_sentences, target_sentences)]
    start_time = time.time()
    # train ibm word alignment model (sentences, iterations)
    ibm_model = IBMModel2(aligned_sentences, 50)#, probability_tables=None)
    end_time = time.time()
    print('training time: ', datetime.timedelta(seconds=end_time - start_time))
    return ibm_model

# Translate Input Sentences
def translate_input(source_text, ibm_model):
    # clean the text using the source tokenizer
    cleaned_text = clean_sentences(source_text.split(), source_tokenizer)
    source_words = cleaned_text
    translated_words = []
    for source_word in source_words:
        max_prob = 0.0
        translated_word = None
        for target_word in ibm_model.translation_table[source_word]:
            prob = ibm_model.translation_table[source_word][target_word]
            if prob > max_prob:
                max_prob = prob
                translated_word = target_word
        if translated_word is not None:
            translated_words.append(translated_word)
    translated_text = ' '.join(translated_words).replace("▁", "")

    return translated_text

# tag the source text based on the English POS of translated terms
def tag_source(test_source, test_target, translation_model, posdict):
    # don't worry about position, just assume that each translation target has the same POS
    taggedtarget = {k.text: k.pos_ for k in nlp(test_target)}
    taggedsource = []
    for word in test_source.split():
        tword = translate_input(word, translation_model)
        if tword in taggedtarget.keys():
            taggedsource.append((word, taggedtarget[tword]))
        else:
            taggedsource.append((word, "unk"))

    return taggedsource

bibdir = "../../bible/combined/" # location of the parsed bibles
engbib = bibdir+"eng-x-bible-newliving_parsed.txt" # name of the English translation
# get the indices (corresponding verses based on stated criteria)
with open("../data/translation/indices.json") as readfile:
    indices = json.load(readfile)

# get all the isos in the Bible corpus based on files
isos = list(set([x.split("/")[-1].split("-")[0] for x in glob.glob(bibdir+"*.txt")]))

# print(isos)
print(len(isos))

# get the English bible
with open(engbib) as f:
    engdata = f.readlines()

print(engdata[:4])

engind = [i.split("\t")[0] for i in engdata] # get the lines and verse numbers of indices for English

errors = []

# go through our list of isos
for iso in tqdm.tqdm(isos):
    # get the list of Bibles, exclude "newworld" translations as they differ from standard translations
    sourcebib = [x for x in glob.glob(bibdir+iso+"*") if "newworld" not in x][0]
    # for languages with multiple translations, select one of them manually
    # criteria for selection are that they are relatively modern and broadly representative
    if iso == 'got':
        print([x for x in glob.glob(bibdir+iso+"*")]) # Gothic Bible
    if iso == 'deu':
        sourcebib = '../bible/combined/deu-x-bible-neue_parsed.txt'
    elif iso == 'afr':
        sourcebib = '../bible/combined/afr-x-bible-lewende_parsed.txt'
    elif iso == 'dan':
        sourcebib = '../bible/combined/dan-x-bible-1931_parsed.txt'
    elif iso == 'ind':
        sourcebib = '../bible/combined/ind-x-bible-easy2005_parsed.txt'
    elif iso == 'tur':
        sourcebib = '../bible/combined/tur-x-bible-2009_parsed.txt'
    elif iso == 'eus':
        sourcebib = '../bible/combined/eus-x-bible-batua_parsed.txt'
    elif iso == 'bul':
        sourcebib = '../bible/combined/bul-x-bible-modern_parsed_romanized.txt'
    elif iso == 'eng':
        sourcebib = '../bible/combined/eng-x-bible-newinternational_parsed.txt'
    elif iso == 'hrv':
        sourcebib = '../bible/combined/hrv-x-bible-complete_parsed.txt'
    elif iso == 'cat':
        sourcebib = '../bible/combined/cat-x-bible-inter_parsed.txt'
    elif iso == 'gla':
        sourcebib = '../bible/combined/gla-x-bible-reference_parsed.txt'
    elif iso == 'slv':
        sourcebib = '../bible/combined/slv-x-bible_parsed.txt'
    elif iso == 'lit':
        sourcebib = '../bible/combined/lit-x-bible-ecumenical_parsed.txt'
    elif iso == 'pol':
        sourcebib = '../bible/combined/pol-x-bible-living_parsed.txt'
    print(sourcebib)

    with open(sourcebib) as f:
        sourcedata = f.readlines()

    sourceind = [i.split("\t")[0] for i in sourcedata]
    # ensure that the same verses are in both datasets
    sharedind = sorted(list(set(engind).intersection(set(sourceind))))#.intersection(set(indices))))
    # print(len(engind))
    # print(len(targetind))
    # print(len(sharedind))

    # process the data
    source = [x.split("\t")[1].strip() for x in sourcedata if x.split("\t")[0] in sharedind]
    source = [' '.join(x.split()) for x in source]
    target = [x.split("\t")[1].strip() for x in engdata if x.split("\t")[0] in sharedind]
    target = [' '.join(x.split()) for x in target]
    nlp.max_length = len(" ".join(target)) + 100

    poslist = [(k.text, k.pos_) for k in nlp(" ".join(target))] # tag the English sentence using SpaCy
    fdist = nltk.FreqDist(poslist)

    posdict = {k[0][0]: k[0][1] for k in list(reversed(fdist.most_common()))}
    for p in punct:
        posdict[p] = "PUNCT" # ID punctuation

    source_lang = sourcebib.split("/")[-1].split("-")[0]
    target_lang = engbib.split("/")[-1].split("-")[0]

    # these are the paths to tagged datasets and model files, so we can access them later
    taggedsourcefile = f'tagged/{source_lang}-{target_lang}-tagged-'+sourcebib.split("/")[-1][:-4]+'.json'
    taggedsourcefile2 = f'tagged/{source_lang}-{target_lang}-tagged-'+'.json'
    pickledmodel = f'models/{source_lang}-{target_lang}-ibmModel2-'+sourcebib.split("/")[-1][:-4]+'.pk'
    pickledstok = f'models/tokenizers/{source_lang}-BPEtokenizer.pk'
    pickledttok = f'models/tokenizers/{target_lang}-BPEtokenizer.pk'

    pretrained_tokenizer = AutoTokenizer.from_pretrained(model_checkpoint) # load the tokenizer

    # set tokenizer parameters
    bos_token = '<s>' # begining of sequence
    unk_token = '<unk>' # unknown token
    eos_token = '</s>' # end of sequence
    pad_token = '<pad>' # padding
    special_tokens = [unk_token, bos_token, eos_token, pad_token]

    tokenizer_params = {
        # 'min_frequency': 3,#doesn't work with unigram
        # 'unk_token': '<unk>',#required for unigram
        'vocab_size': 5000,# limit the vocab size to 5k, though some languages might benefit from more
        'show_progress': True,
        'min_frequency': 2,
        'special_tokens': special_tokens
    }

    # train a new tokenizer for the source language, or load an existing one
    if not os.path.isfile(pickledstok):
        print(f"Training {source_lang} tokenizer...")
        start_time = time.time()
        source_tokenizer = SentencePieceBPETokenizer()#lowercase=True)
        source_tokenizer.train_from_iterator(source, **tokenizer_params)

        end_time = time.time()
        print('time elapsed: ', end_time - start_time)
        print('source vocab size: ', source_tokenizer.get_vocab_size())

        with open(pickledstok, 'wb') as fout:
            pickle.dump(source_tokenizer, fout)

    else:
        print(f"Loading {source_lang} tokenizer...")
        with open(pickledstok, 'rb') as fin:
            source_tokenizer = pickle.load(fin)
        print(source_tokenizer)

    # train a new tokenizer for the target language, or load an existing one
    if not os.path.isfile(pickledttok):
        print(f"Training {target_lang} tokenizer...")
        target_tokenizer = SentencePieceBPETokenizer()#lowercase=True)
        target_tokenizer.train_from_iterator(target, **tokenizer_params)

        end_time = time.time()
        print('time elapsed: ', end_time - start_time)
        print('target vocab size: ', target_tokenizer.get_vocab_size())
        print('target vocab size: ', target_tokenizer.get_vocab_size())
        with open(pickledttok, 'wb') as fout:
            pickle.dump(target_tokenizer, fout)
    else:
        print(f"Loading {target_lang} tokenizer...")
        with open(pickledttok, 'rb') as fin:
            target_tokenizer = pickle.load(fin)
        print(target_tokenizer)

    # train a new translation model for the source/target language, or load an existing one
    if not os.path.isfile(pickledmodel):
        translation_model = None
        print(f'Translate from {source_lang} to {target_lang}: ')
        cleaned_source = clean_sentences(source, source_tokenizer)
        cleaned_target = clean_sentences(target, target_tokenizer)

        print(f"Training new model for {source_lang}-{target_lang}...")
        translation_model = train_translation_model(cleaned_source, cleaned_target)
        with open(pickledmodel, 'wb') as fout:
            pickle.dump(translation_model, fout)

    else:
        print(f"Loading {source_lang}-{target_lang} model...")
        with open(pickledmodel, 'rb') as fin:
            translation_model = pickle.load(fin)
        print(translation_model)

    # tag the dataset by transferring POS tags from English
    if not os.path.isfile(taggedsourcefile2):
        test_source = source#[:5]
        test_target = target#[:5]

        sourcetagged = []
        if len(test_source) == len(test_target):
            for num, text in enumerate(test_source):
                result = tag_source(text, test_target[num], translation_model, posdict)
                sourcetagged.append([sharedind[num], result])
            # print(sourcetagged)
            with open(taggedsourcefile, 'w') as fout:
                json.dump(sourcetagged, fout)
        else:
            errors.append(iso)

print(errors)
