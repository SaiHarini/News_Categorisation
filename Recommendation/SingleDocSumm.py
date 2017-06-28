from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.porter import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import random
from collections import Counter
import math
from functools import reduce
from operator import itemgetter
import os

# generate random numbers for b and k1
incrementer = 0
lgt = 0


def bm25(docs):


	def Preprocess(Paragraph):
		# Replace the aporstophes and "
		Paragraph = Paragraph.replace('"', " ")
		Paragraph = Paragraph.replace("'s", "")

		# Create a list of tokenized sentences
		sent = sent_tokenize(Paragraph)
		global lgt
		lgt = lgt + len(sent)
		global incrementer
		incrementer = incrementer + 1
		if incrementer % 2 != 0:
			lgtOfDocs.append(lgt)
			lgt = 0
		words = []

		# Create a list of list of words-each sublist is the list of words in
		# one article
		for sentence in sent:
		    words.append(word_tokenize(sentence))

		# Flatten the nested list into a single list-vocabulary of the corpus
		words = [item for sublist in words for item in sublist]

		# Create objects for stemming and lemmatization
		stemmer = PorterStemmer()
		lemmatizer = WordNetLemmatizer()
		puncts = '.?!:)(}{[],'

		# Do case folding of the words
		for index, word in enumerate(words):
			words[index] = word.lower()

		# Remove punctuations from the vocabulary
		for index in range(len(words)):
			for sym1 in puncts:
				if index < len(words):
					if sym1 == words[index]:
						words.remove(sym1)
				else:
					break

		# Perform stemming and lemmatization of the terms
		for index in range(len(words)):
			words[index] = stemmer.stem(words[index])

		for index in range(len(words)):
			words[index] = lemmatizer.lemmatize(words[index])

		# Remove all the stop words
		stop_words = set(stopwords.words('english'))
		words = [w for w in words if not w in stop_words]

		return words


	article = []
	doc = []
	doclen = []
	processed_doc = []
	total_len = 0

	doc = docs
	# f = open("final_file.txt",'r')
	index = 0
	all_words = []
	lgtOfDocs = []
	for doc1 in doc:
		temp = 0
		for article in doc1:
			words = word_tokenize(''.join(article))
			all_words.append(words)

			temp = temp + len(words)
		total_len = total_len + temp
		# Length of each document is stored in doclen
		doclen.append(temp)

	# Flatten the all_words nested list
	all_words = [item for sublist in all_words for item in sublist]

	# Keep only unique terms
	all_words = set(all_words)

	# terms is the vocabulary of the corpus
	# terms=Preprocess("".join(all_words))

	# BETTER TO USE TERMS,REMOVE ALL WORDS AND INDEX IN THE ABOVE LOOP
	NoOfDocs = len(doc)

	temp = []
	processed_article = []
	# temp=[[words in title],[words in text]]
	# processed_doc=[ [[title words of doc1],[text words of doc1]], [[title
	# words of doc2],[text words of doc2]] ]

	for eachDoc in range(NoOfDocs):
		# Title or text of article
		for eachArticle in range(2):
			temp.append(Preprocess(''.join(doc[eachDoc][eachArticle])))
		processed_article.append(temp)

		processed_doc.append(processed_article)
		temp = []
		processed_article = []

	temp = []
	docDict = []

	# List for maintaining freq of words in title n text of each doc in the form of dict
	# dict=[ [ {title1 dict},{text1 dict} ],[ {title2 dict},{text2 dict} ]
	# ]
	for i in range(NoOfDocs):
		for j in range(2):
			temp.append(dict(Counter(processed_doc[i][0][j])))
		docDict.append(temp)
		temp = []

	MaxNoOfDocs = 1
	temp = []
	relTerms = []
	# freq=[]
	# counter=0
	# add=[]
	for i in range(0, MaxNoOfDocs):
		for t in range(2):
			for key in docDict[0][t]:
				temp.append(key)

		relTerms.append(temp)
		temp.append(i)
		temp = []
		# freq=[]


		FlattenedrelTerms = [item for sublist in relTerms for item in sublist]

		value = {}
		for index, trm in enumerate(FlattenedrelTerms):
			value[trm] = 0
			for i in range(0, MaxNoOfDocs):
				for j in range(0, 2):
					if trm in docDict[0][j]:
						value[trm] = value[trm] + docDict[0][j][trm]

		sents=[]
		for i in range(MaxNoOfDocs):
			for j in range(2):
				sents.append(sent_tokenize("".join(doc[0][j])))

		sents=[item for sublist in sents for item in sublist]


	def sum_basic(update_non_redundency=True):
		def weight(sents, distribution):
			def _weight_sent(sent):
				tokens = Preprocess(sent)
				# #print("\n\nTOKENS ARE ",tokens)
				if len(tokens) != 0:
					return reduce(lambda x, y: x + y, [distribution.get(x) for x in tokens]) / len(tokens)
				else:
					return 0.0

			return [_weight_sent(sent) for sent in sents]

		def probability_distribution(tokens):
			N = len(tokens)
			distinct_words = set(tokens)

			probabilities = map(lambda w: value[w] / N, distinct_words)
			return dict(zip(distinct_words, probabilities))

		pd = probability_distribution(FlattenedrelTerms)

		summary = ""

		while len(word_tokenize(summary)) < 200:
			weights = weight(sents, pd)
			temp = max(zip(sents, weights), key=itemgetter(1))
			highest_weight_sentence= temp[0]
			summary += " " + highest_weight_sentence
			if update_non_redundency:
				for token in Preprocess(highest_weight_sentence):
					pd[token] = pd[token] * pd[token]
			else:
				sents.remove(highest_weight_sentence)

		return summary

	summary = sum_basic()

	#print(summary)

	return summary


#bm25([[['Stories of struggle on Muthukrishnans Facebook wall'],['more-in  A look at J. Muthukrishnans Facebook wall reveals the discrimination and struggle that this first-generation JNU research scholar faced all through his life, before it tragically ended on Tuesday.  Muthukrishnan vividly describes his early days in long posts on Facebook. The odd-jobs to meet his family\'s needs as well as to fund his education, the double whammy of poverty and hailing from a marginalised community and the discrimination that is rampant in one of the most prestigious universities in the National Capital.  When equality is denied everything is denied, begins Muthukrishnans last post, written three days before his alleged suicide.  The post describes his childhood days in Salem, Tamil Nadu. They were on how he bought Maana (beef/meat in colloquial Tamil) for his family and boarded a bus and how he had to come across dirty stares from fellow passengers, and even his schoolmate refused to speak with him, because of the meat he was carrying.  Many people turned aside, and crossed opposite side, after seeing the Maana carry bag. In those days there was no equality for Maana, but nowadays there is no maana , that is to say there is no equality (sic), he says.  Muthukrishnan further writes: There is no Equality in M.phil/phd Admission, there is no equalitiy in Viva  voce, there is only denial of equality, denying prof. Sukhadeo Thorat recommendation, denying Students protest places in Ad  block, denying the education of the Marginals (sic). When Equality is denied everything is denied.  Many sides of One-Side love  In another post dated February 15, Muthukrishan remembers his crush from college days, and his interactions with her. He goes on to reveal that the girl is a married woman now and that he too has moved on.  And I don\'t want to become ILavarasan, Gokul Raj, Shankar ! most importantly all my crush said, You will get Better girl In the World! (sic) Muthukrishnan writes drawing parallel with the murder of three Dalit youth in Tamil Nadu for marrying caste Hindu girls.  History is Maths  At a time when JNU students were protesting against a new proposal of University Grant Commission to do away with entrance tests for M. Phil and PhD aspirants and conduct admission only through interview, Muthukrishnan wrote this post.  He recalls how a Maths teacher targeted him for not joining his private tuition. His post also mentions how he was humiliated, mentioning where "he hails from" and for having a new hair cut. Muthukrishnan goes on to say how he hated the subject after that. He also says he took it up as a challenge and went on to become a first-generation graduate trying to build a chances for others.  He ends the post with an appeal to the Acting Chairman of UGC: please give chance to the first generation Marginals, otherwise, he/she will misunderstand Maths means enemy! Education means depression! He/she will misunderstand university means discrimination! Please change, please give a chance!  Remembering the lady he loved  Recalling another incident, during a visit to Taj Mahal, Muthukrishnan remembers his grandmother Sellammal and her perseverance to build a house for her family. Sellammal, he says, worked as a sanitation worker at a private school and lived on her earning till her last days. He recalls his grandmothers occasional advice not to indulge in liquor and look after the family. He couldnt pay his last respects when Sellammal passed away due to paucity of funds to travel from Delhi to his hometown. From the monument of love Muthukrishnan writes: In Taj Mahal, without girlfriend, I was thinking about only my Sellammal Aaya, I actualised My sellamma is my soul.']]])
