#!/usr/bin/env python
#coding=utf-8
import re
import sys
import itertools
import time
from collections import defaultdict,Counter
try:
    import jieba
    import jieba.posseg as pseg
    #from gensim import corpora,models

except ImportError:
        print >> sys.stderr, """\

There was a problem importing one of the Python modules required.
The error leading to this problem was:

%s

Please install a package which provides this module, or
verify that the module is installed correctly.

It's possible that the above module doesn't match the current version of Python,
which is:

%s

""" % (sys.exc_info(), sys.version)
        sys.exit(1)


def get_stopwords(filename='stopwords'):

    with open(filename,'r') as f:
        lines = f.readlines()
    
    stopwords = set(line.rstrip("\r\n") for line in lines)
   
    return stopwords

def format(filename='data.txt'):

    stopwords = get_stopwords()
     
    noun_phrases = []
    texts = []
    with open(filename,'r') as f:
	for line in f:
	    print line
	    pseg_line = list(pseg.cut(line))
	    #print pseg_line
	    new_line = [item for item in pseg_line if item.flag != 'x']
	    print 'new_line', new_line
	    words = [(item.word).encode('utf8') for item in new_line]
	    #print ' '.join(words)
	    texts.append(words)

    	    flags = ['n','nr','ns','nt','nz','nl','ng','l','a','ad','an','ag','al']
            noun_flags = ['n','nr','ns','nt','nz','nl','ng','l']
	    item_phrase = []
	    for item in new_line:
	        if item.flag in flags:
	            if item not in item_phrase:
	    	        item_phrase.append(item)
	    	else:
		    if len(item_phrase) == 1:
                        noun_word = (item_phrase[0].word).encode('utf8')
		        if len(noun_word) >= 12:
			    print noun_word
	    		    noun_phrase = [(item.word).encode('utf8') for item in item_phrase]
			    noun_phrases.append(noun_phrase)
		    
		    if len(item_phrase) > 1:
	    	        if item_phrase[-1].flag in noun_flags:
	    		    noun_phrase = [(item.word).encode('utf8') for item in item_phrase]
			    print ' '.join(noun_phrase)
	    		    noun_phrases.append(noun_phrase)
	    	    item_phrase= []


    return texts, noun_phrases


def get_keyphrase(postags):

    candidate_keyphrases = []
    keyphrase = []
    for postag in postags:
        if postag.flag in ['n','nr','ns','nt','nz','nl','ng']:
            word = (postag.word).encode('utf-8')
            keyphrase.append(postag.word)
        else:
            if keyphrase:
                keyphrase_str = " ".join(keyphrase)
                print keyphrase_str
                candidate_keyphrases.append(keyphrase_str)
                keyphrase = []
    if keyphrase:
        keyphrase_str = " ".join(keyphrase)
        candidate_keyphrases.append(keyphrase_str)
    return candidate_keyphrases

def get_worddegree(texts,window_size=5):

	wordlist = list(itertools.chain(*texts))
	length = len(wordlist)
	wordgraph = [wordlist[i]+' '+wordlist[i+j] for i in range(0,length) for j in range(1,window_size) if i+j<length]
	word_dict = Counter(wordgraph)
	word_indegree = defaultdict(lambda:defaultdict(int))
	word_outdegree = defaultdict(int)
	for edge in word_dict:
		word_i = edge.split(' ')[0]
		word_j = edge.split(' ')[1]
		word_indegree[word_j][word_i] = word_dict[edge]
		word_outdegree[word_i] += word_dict[edge]
	return word_indegree,word_outdegree

def record_lda(texts,num_topics=5,update_every=1,passes=1):
	
    	dictionary = corpora.Dictionary(texts)
    	corpus = [dictionary.doc2bow(text) for text in texts]
    	doc = list(itertools.chain(*corpus))
    	topic_corpus = []
    	topic_corpus.append(doc)

	word_num = len(dictionary)
        doc_num = len(texts)
        chunksize = doc_num/1000

	lda = models.ldamodel.LdaModel(corpus=corpus,id2word=dictionary,num_topics=num_topics,update_every=update_every,chunksize=chunksize,passes=passes)
	for topic_tuple in lda[topic_corpus]:
		topic_distribution = dict(topic_tuple)
	
	topicword_distribution = defaultdict(lambda:defaultdict(float))
	i = 0
	for wordtuple_list in lda.show_topics(topics=num_topics,topn=word_num,formatted=False):
    		inv_map = {v:k for k,v in dict(wordtuple_list).items()}
    		topicword_distribution[i] = inv_map
    		i += 1
	return topic_distribution,topicword_distribution

def process_file(filename='data.txt'):
    
    texts,keyphrases = format(filename=filename)
    #keyphrases = get_keyphrase(postags=postags)
    word_indegree,word_outdegree = get_worddegree(texts)
    topic_distribution,topicword_distribution = record_lda(texts)

    return keyphrases,word_indegree,word_outdegree,topic_distribution,topicword_distribution

def main():
    keyphrases,word_indegree,word_outdegree,topic_distribution,topicword_distribution = process_file(filename='test1.txt')
    print len(word_indegree),len(word_outdegree),len(topicword_distribution[0])

if __name__ == "__main__":
    start = time.time()
    #process_file(filename='test.txt')
    format(filename='final.txt')
    print 'time',time.time()-start
