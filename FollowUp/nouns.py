import nltk
import copy
import bm25
import RecomParallel
from textblob import TextBlob
from geotext import GeoText
from joblib import Parallel, delayed
from datetime import datetime, timedelta
import os, sys

def nouns(index):
	f=open("..\\sentimental_analysis\\docs\\"+str(index)+".txt","r", encoding='utf-8')
	doc=[]
	lines=f.readlines()

	for line in lines:
		line.replace("\n","")

	lines="".join(lines)

	#Get title and content for single doc summarization
	f.seek(0,0)
	title=f.readline()
	##print("OLD title:",title)
	# title = [s.rstrip() for s in title]
	# #print("title:",title)

	content=f.readlines()
	content="".join(content)
	content.replace("\\n","")
	content=[content]
	# for c in content:
	# 	c.replace("\\n","")
	temp=[]
	temp.append([title])
	temp.append(content)
	doc.append(temp)



	# blob = TextBlob(lines)
	# #print("TEXT BL:",list(set(blob.noun_phrases)))
	##print("REL :",relWords)



	text=nltk.word_tokenize(lines)
	tags=nltk.pos_tag(text)

	relWords=[]
	places = GeoText(lines)
	cities=places.cities
	countries=places.countries
	relWords=cities+countries
	temp=""
	i=0
	while i<len(tags):

		temp=""
		flag=False
		index=i
		##print("t:",tags[index])
		while index<len(tags) and tags[index][1]=='NNP':
			if flag:
				temp+=" "+tags[index][0]
				
			else:
				temp+=tags[index][0]
				
			index=index+1
			
			flag=True
		relWords.append(temp)
		temp=""
		if flag is False:
			i=i+1
		else:
			i=index

	relWords=list(set(relWords))




	stop_words=["January","February","March","April","May","June","July","August","September","October","November","December","Rs","Cr","Lakh","Thousand","Crore","Kg","Gram","Watch","Sources","Watch live","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday","I","We","He","She","It","You","They","We're"]
	puncts=["{","}","[","]","(",")"]

	##print("REL WORDS1 ",relWords)
	words=[]
	for i,word in enumerate(relWords):
		if word !='' and word not in stop_words:
			##print("i:",word)
			##print("word: ",word)
			words.append(word)

	for index,word in enumerate(words):
		for p in puncts:
			if p in word:
				words[index]=words[index].replace(p,"")
				

	##print("WORDS: ",words)
	new_list = []
	flag = False
	for i in range(len(words)):
	    for j in range(len(words)):
	        if i == j:
	            continue
	        if words[i] in words[j]:
	            flag = True
	            break
	    if flag == True:
	        flag = False
	        continue
	    else:
	        new_list.append(words[i])

	relWords=copy.copy(new_list)
	#print("REL :",relWords)
	query=" ".join(relWords)
	##print("QUERY ",query)
	def call_bm25():
		#allDocs=[]
		# for word in relWords:

		allDocs = Parallel(n_jobs=3)(delayed(RecomParallel.Scrape)(word)for word in relWords)
		# for word in relWords:
		# 	#print ("WORD IS ",word)
		# 	similarDocs = RecomParallel.Scrape(word)
		# 	allDocs.append(similarDocs)
		return allDocs


	allDocs=call_bm25()

	#4D list ---  [ [ [[title],[text]],[[title],[text]] for query1 ]     [[[]]]   ]
	
	#print("ALL DOc  ")
	# result=RecomSemantic.rec(starred_doc,summaries)
	# #print("\n\nRES:",result)
	#for doc in allDocs:
		#print("\n",doc)
		# f1.write(doc)
		# f1.write("\n")
	temp=[]
	for queryList in allDocs:
		for eachDoc in queryList:
			temp.append(eachDoc)

	allDocs=temp
	final=bm25.bm25(query,allDocs)
	#print("\nFINAL  ")
	f = open("Summary.txt", "w")
	f.write(final)
	f.close()
	print("STR:",final)
		# f2.write(doc)
		# f2.write("\n")

def follow_up(index):
	initialTime=datetime.now()
	interval=6
	flag=False
	while True:
		if flag is False:
			#print("time now :",initialTime)
			#print("FIRST TIME....")
			nouns(index)
			flag=True
		else:
			#print("Waiting...",datetime.now())
			if datetime.now()==initialTime+timedelta(hours=interval):
				#print("CALLLLLLLEEEEEEDDDDDDDD")
				nouns(index)

def getTitles():
	titleDict = dict()
	path="..\\sentimental_analysis\\docs\\"
	
	titles=""
	for fname in os.listdir(path):
		f=open(os.path.join(path, fname),"r", encoding='utf-8')
		line=f.readline()
		line=line.replace("\n","")
		titleDict[line]=int(fname.split(".")[0])
		titles+=line+"~~ "
		f.close()
	titles=titles[:len(titles)-3]
	return titleDict
	
def func(title, titleDict):
	follow_up(titleDict[title])


if __name__ == "__main__":
	titleDict = getTitles()
	query = sys.argv[1]
	func(query, titleDict)

# titles=getTitles()
# #print("titl:",titleDict)
# func("Reliance Jio chargeable & limited now:")