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

#generate random numbers for b and k1
incrementer=0
lgt=0

def bm25(qry,docs):
	b=random.uniform(0,1)
	K1=random.uniform(1.2,2)
	article=[]
	doc=[]
	doclen=[]
	processed_doc=[]
	total_len=0
	#f = open("final_file.txt",'r')
	index=0
	all_words=[]
	lgtOfDocs=[]
	
	#Perform all the preprocessing for the paragraphs in each article,for each text and title
	def Preprocess(Paragraph):
		#Replace the aporstophes and "
		Paragraph=Paragraph.replace('"'," ")
		Paragraph=Paragraph.replace("'s","")
		
		#Create a list of tokenized sentences
		sent=sent_tokenize(Paragraph)
		global lgt
		lgt=lgt+len(sent)
		global incrementer
		incrementer=incrementer+1
		if incrementer%2!=0:
			lgtOfDocs.append(lgt)
			lgt=0
		words=[]
		
		#Create a list of list of words-each sublist is the list of words in one article
		for sentence in sent:
			words.append(word_tokenize(sentence))
		
		#Flatten the nested list into a single list-vocabulary of the corpus
		words=[item for sublist in words for item in sublist]
		
		#Create objects for stemming and lemmatization
		stemmer=PorterStemmer()
		lemmatizer=WordNetLemmatizer()
		puncts='.?!:)(}{[],'
		
		#Do case folding of the words
		for index,word in enumerate(words):
			words[index]=word.lower()
		
		#Remove punctuations from the vocabulary
		for index in range(len(words)):
			for sym1 in puncts:
				if index<len(words):
					if sym1==words[index]:
						words.remove(sym1)
				else:
					break
					
		#Perform stemming and lemmatization of the terms
		for index in range(len(words)):
			words[index]=stemmer.stem(words[index])

		for index in range(len(words)):
			words[index]=lemmatizer.lemmatize(words[index])

		#Remove all the stop words
		stop_words = set(stopwords.words('english'))
		words = [w for w in words if not w in stop_words]
		
		return words
		
	doc=docs
	for doc1 in doc:
		temp=0
		for article in doc1:
			words=word_tokenize(''.join(article))
			all_words.append(words)

			temp=temp+len(words)
		total_len=total_len+temp
		#Length of each document is stored in doclen
		doclen.append(temp)
		
	#Flatten the all_words nested list
	all_words=[item for sublist in all_words for item in sublist]

	#Keep only unique terms
	all_words=set(all_words)

	#terms is the vocabulary of the corpus
	#terms=Preprocess("".join(all_words))

	#BETTER TO USE TERMS,REMOVE ALL WORDS AND INDEX IN THE ABOVE LOOP
	NoOfTerms=len(all_words)
	NoOfDocs=len(doc)


	#Find average document length
	if len(doc)==0:
		return [[[]]]
	avg_doclen=float(float(total_len)/float(len(doc)))

	temp=[]
	processed_article=[]
	#temp=[[words in title],[words in text]]
	#processed_doc=[ [[title words of doc1],[text words of doc1]], [[title words of doc2],[text words of doc2]] ]

	for eachDoc in range(NoOfDocs):
		#Title or text of article
		for eachArticle in range(2):
			temp.append(Preprocess(''.join(doc[eachDoc][eachArticle])))
		processed_article.append(temp)

		processed_doc.append(processed_article)
		temp=[]
		processed_article=[]

	temp=[]
	docDict=[]

	#List for maintaining freq of words in title n text of each doc in the form of dict
	#dict=[ [ {title1 dict},{text1 dict} ],[ {title2 dict},{text2 dict} ] ]
	for i in range(NoOfDocs):
		for j in range(2):
			temp.append(dict(Counter(processed_doc[i][0][j])))
		docDict.append(temp)
		temp=[]

	Query=qry
	#input("Enter a query: ")
	QueryLen=len(Query.split(" "))
	Query=Preprocess(Query)

	#freq of query term in title
	title=[0.0]*NoOfDocs

	#freq of query term in text
	text=[0.0]*NoOfDocs

	f=[[0]*NoOfDocs for i in range(NoOfTerms)]

	for index,q in enumerate(Query):
		for i in range(NoOfDocs):
			if q in docDict[i][0]:
				title[i]=title[i]+docDict[i][0][q]

			if q in docDict[i][1]:
				text[i]=text[i]+docDict[i][1][q]


	#find the frequency of the query terms
	for index,q in enumerate(Query):
		for i in range(NoOfDocs):
			f[index][i]=float(title[i])+float(text[i])

	B=[[0.0]*NoOfDocs for i in range(QueryLen)]
	Lterm=[0.0]*QueryLen

	#Find the b[i][j] value
	for q in range(QueryLen):
		for d in range(NoOfDocs):
			B[q][d]=float((float((K1+1)*f[q][d]))/(float((K1*((1-b)+(float(b*doclen[d])/float(avg_doclen)))))+f[q][d]))

	n=[0]*QueryLen
	for index,q in enumerate(Query):
		for i in range(NoOfDocs):
			if q in docDict[i][0] or q in docDict[i][1]:
				n[index]=n[index]+1

		Lterm[index]=math.log(float(float(NoOfDocs-n[index]+0.5)/float(n[index]+0.5)),2)

	#sim array is [[sim1,docNo],[sim2,docNo],[..],[..]]
	sim=[[0.0]*2 for x in range(NoOfDocs)]

	for d in range(NoOfDocs):
		for index in range(QueryLen):
			sim[d][0]=sim[d][0]+float(B[index][d])
		sim[d][1]=d+1

	sim=sorted(sim,reverse=True)
	similarDocs=[]
	#print(sim)
	for simDoc in sim[:3]:
		docNo=simDoc[1]
		similarDocs.append(doc[docNo-1])

	return similarDocs
