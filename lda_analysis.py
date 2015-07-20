#!/usr/bin/python -tt
# Stephen Muchovej

import os
import re
import sys
import urllib
import re
import pandas as pd
from bs4 import BeautifulSoup
import commands
import nltk
import string
import os
import itertools

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import text as sktext
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from sqlalchemy import create_engine
from sqlalchemy.types import String
from gensim import corpora, models, similarities
import pyLDAvis.gensim


"""
   Program used for NLP investigation and LDA analysis on bills from 
   the present term.
"""

token_dict = {}
stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def lemmatize_tokens(tokens, lemmatizer):
    stemmed = []
    for item in tokens:
        stemmed.append(lemmatizer.lemmatize(item))
    return stemmed

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems  = lemmatize_tokens(tokens, lemmatizer)
    return stems

def stop_word_list():
    # any two letter words get tossed                                                                                                                     
    letters = list(string.ascii_lowercase)
    short_words = [''.join(i) for i in itertools.product(letters, repeat = 2)]
    legaleze = ['law', 'california', 'department', 'pursuant', 'section', 'shall',
                'this', 'commission', 'provisions', 'committee', 'paragraph', 'chapter',
                'section', 'state', 'legislature', 'senate', 'act', 'subdivision', 'qualified',
                'assembly', 'existing', 'united', 'states', 'bill', 'would', 
                'is', 'amended', 'this', 'item', 'specified', 'person',' existing_law', 'united_states', 'bill_would',
                'is_amended', 'amended', 'this_item', 'specified', 'united_states', 'public', 'california_do',
                'following']
    all_words = short_words
    all_words.extend(letters)
    all_words.extend(legaleze)
    my_stop_words = sktext.ENGLISH_STOP_WORDS.union(all_words)
    return my_stop_words


"""
  ------------------------------------------------------------
  PREPARE THE DOCUMENTS FOR NLP
  ------------------------------------------------------------
"""

# upload the pandas dataframe with all info on bills and their text.
bill_df = pd.load('fullbilldetails_dataframe')
documents = bill_df['full_cleaned_text']
aa = bill_df['full_cleaned_text']

for i in range(len(documents)):
    documents[i] = documents[i].replace('-', ' ')
    documents[i] = documents[i].replace('ab ', ' ')
    documents[i] = documents[i].replace('_', ' ')
    
# playwing with bigrams                                                                                                        
doclist=[];
for doc in documents:
    doclist.append(doc.split())

bigram = models.Phrases(doclist)
trigram = models.Phrases(bigram[doclist])

stoplist = stop_word_list()

"""
  ------------------------------------------------------------
  Testing bigrams/trigrams.  Bigrams worked best.  0 trigrams added with frequency greater than 1.
  ------------------------------------------------------------
"""

#texts = [[word for word in document.lower().split() if (word not in stoplist and len(word)>2)]                                
#         for document in documents]                                                                                           

#texts = [[word for word in document if (word not in stoplist and len(word)>2)]                                
#         for document in doclist]                                                                                           

texts = [[word for word in bigram[document] if (word not in stoplist and len(word)>2)]                        
         for document in doclist]                                                                                           

#texts = [[word for word in trigram[document] if (word not in stoplist and len(word)>2)]
#         for document in doclist]

# remove words that appear only once                                                                                           
from collections import defaultdict
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1

texts = [[token for token in text if frequency[token] > 1]
         for text in texts]

dictionary = corpora.Dictionary(texts)
dictionary.save('/tmp/billdictionary.dict') # store the dictionary, for future reference                                                                                   

corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('/tmp/billcorpus.mm', corpus) # store to disk, for later use                                                                                    

"""
  ------------------------------------------------------------
  tfidf tests
  ------------------------------------------------------------
"""

# testing tfidf
#tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words=stop_words)
#tfs = tfidf.fit_transform(bill_df['full_cleaned_text'])

"""
  ------------------------------------------------------------
  LDA tests.
  ------------------------------------------------------------
"""

# testing LDA
lda3 = models.LdaModel(corpus, num_topics=3, id2word=dictionary, passes=10)
lda4 = models.LdaModel(corpus, num_topics=4, id2word=dictionary, passes=10)
lda5 = models.LdaModel(corpus, num_topics=5, id2word=dictionary, passes=10)
lda6 = models.LdaModel(corpus, num_topics=6, id2word=dictionary, passes=10)
lda7 = models.LdaModel(corpus, num_topics=7, id2word=dictionary, passes=10)
lda8 = models.LdaModel(corpus, num_topics=8, id2word=dictionary, passes=10)
lda9 = models.LdaModel(corpus, num_topics=9, id2word=dictionary, passes=10)
lda10 = models.LdaModel(corpus, num_topics=10, id2word=dictionary, passes=10)
lda11 = models.LdaModel(corpus, num_topics=11, id2word=dictionary, passes=10)
lda12 = models.LdaModel(corpus, num_topics=12, id2word=dictionary, passes=10)
lda13 = models.LdaModel(corpus, num_topics=13, id2word=dictionary, passes=10)
lda14 = models.LdaModel(corpus, num_topics=14, id2word=dictionary, passes=10)
lda15 = models.LdaModel(corpus, num_topics=15, id2word=dictionary, passes=10)



# inspect LDA
pyLDAvis.gensim.prepare(lda4, corpus, dictionary)
pyLDAvis.enable_notebook()
pyLDAvis.gensim.prepare(lda4, corpus, dictionary)


"""
  ------------------------------------------------------------
  4 LDA topics worked best, write the bills as decomposed 
  into those to a database.
  
  lda4.print_topics()

  ------------------------------------------------------------
"""


# 4 topics worked best.
# write the output to a dataframe and then to a sql database.
bill_summary_df = pd.DataFrame(columns=['bill_name', 'sunlight_id', 'education',
                                        'procedural', 'tax_economy', 'health_care'])

for i in range(len(bill_df)):
    name = bill_df['bill_name'][i];
    sid  = bill_df['sunlight_id'][i];

    doc_bow = dictionary.doc2bow(texts[i]);
    doc_lda = lda4[doc_bow]
    edu   = 0
    proc  = 0
    tax   = 0
    health= 0
    for index, value in doc_lda:
        if index == 0:
            health = value
        elif index == 1:
            proc = value
        elif index == 2:
            edu   = value
        elif index == 3:
            tax  = value
        else:
            print 'error'

    dfrow = pd.Series({'bill_name':name, 'sunlight_id':sid, 'education':edu, 'procedural':proc,
                       'tax_economy':tax, 'health_care':health})
    bill_summary_df.loc[i] = dfrow


engine = create_engine("mysql+pymysql://root@localhost/legislator_db")
bill_summary_df.to_sql('billsubject_final_table', engine,if_exists='replace')



"""
  ------------------------------------------------------------
  Inspecting some results
  ------------------------------------------------------------
"""
# unitopic ones are found like this
cc =bill_summary_df[bill_summary_df['education']>0.9]

# to decompose bills, you do this:
texts[382]
doc_bow = dictionary.doc2bow(texts[i])
doc_lda = lda4[doc_bow]
print doc_lda
