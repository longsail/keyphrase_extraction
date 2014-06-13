#!/usr/bin/env python
#coding=utf-8
import sys
import time
import operator
import itertools
from collections import defaultdict
try:
    import jieba
    import jieba.posseg as pseg
    import process

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


def rank_word(word_distribution,word_indegree,word_outdegree,daming_factor=0.85,max_iteration=100):
    
    word_num = len(word_distribution)
    wordrank = {word:1.0/word_num for word in word_distribution}
    for iteration in xrange(0,max_iteration):
        for word in word_distribution:
            weight = 0.0
            for word_j in word_indegree[word]:
		try:
                	out_degree = word_outdegree[word_j]
			weight1 = word_indegree[word][word_j]
                	weight += 1.0*weight1*wordrank[word_j]/out_degree
		except:
			pass
	    wordrank[word] = daming_factor*weight+(1-daming_factor)*word_distribution[word]
    print 'wordrank',len(wordrank)
    return wordrank

def topical_pagerank(word_indegree,word_outdegree,topic_worddistribution):
    
    topic_wordrank = defaultdict(defaultdict)
    for topic in topic_worddistribution:
        topic_wordrank[topic] = rank_word(topic_worddistribution[topic],word_indegree,word_outdegree)

    return topic_wordrank


def rank_keyphrase(keyphrase_list,topic_wordrank,topic_distribution):
    print 'keyphrase_list',len(keyphrase_list)
    topic_keyphraserank = defaultdict(lambda:defaultdict(int))
    for topic in topic_distribution:
        for keyphrase in keyphrase_list:
	    word_list = keyphrase.split(' ')
            weight = 0.0
	    for word in word_list:
		try:
                    weight += topic_wordrank[topic][word]
		except:
                    pass
	    topic_keyphraserank[topic][keyphrase] = weight
    
    keyphrase_rank = defaultdict(int)
    for keyphrase in keyphrase_list:
	keyphrase_weight = 0.0
        for topic in topic_distribution:
	    try:
            	keyphrase_weight += topic_keyphraserank[topic][keyphrase]*topic_distribution[topic]
	    except:
                pass
        keyphrase_rank[keyphrase] = keyphrase_weight
        
    sorted_keyphrase = sorted(keyphrase_rank.iteritems(),key=operator.itemgetter(1),reverse=True)
    final_keyphrase = sorted_keyphrase[0:100]
    with open('keyphrase_cup.txt','w') as f:
        for keyphrase in final_keyphrase:
            f.write(str(keyphrase[0])+','+str(keyphrase[1])+'\n')

def main(filename):
    keyphrases,word_indegree,word_outdegree,topic_distribution,topicword_distribution = process.process_file(filename=filename)
    print 'keyphrases',len(keyphrases)
    topic_wordrank = topical_pagerank(word_indegree,word_outdegree,topicword_distribution)
    rank_keyphrase(keyphrases,topic_wordrank,topic_distribution)


    
if __name__ == "__main__":
    start = time.time()
    main('test.txt')
    print 'time',time.time()-start
