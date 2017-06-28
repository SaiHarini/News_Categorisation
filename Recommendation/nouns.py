import nltk
import copy
import recomMatch
import bm25
import RecomParallel
from textblob import TextBlob
from geotext import GeoText
from joblib import Parallel, delayed
import SingleDocSumm
import os, sys
def recom(index):
    f=open("..\\sentimental_analysis\\docs\\"+str(index)+".txt","r", encoding='utf-8')
    doc=[]
    lines=f.readlines()

    for line in lines:
        line.replace("\n","")

    lines="".join(lines)


    #Get title and content for single doc summarization
    f.seek(0,0)
    title=f.readline()
    #print("OLD title:",title)
    # title = [s.rstrip() for s in title]
    # print("title:",title)

    content=f.readlines()
    content="".join(content)
    content.replace("\\n","")
    content=[content]
    # for c in content:
    #   c.replace("\\n","")
    temp=[]
    temp.append([title])
    temp.append(content)
    doc.append(temp)

    #print("DOC IS: ",doc)

    lines=SingleDocSumm.bm25(doc)
    #[ [[title],[text]] ]

    # blob = TextBlob(lines)
    # print("TEXT BL:",list(set(blob.noun_phrases)))
    #print("REL :",relWords)



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
        #print("t:",tags[index])
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

    #print("REL WORDS1 ",relWords)
    words=[]
    for i,word in enumerate(relWords):
        if word !='' and word not in stop_words:
            #print("i:",word)
            #print("word: ",word)
            words.append(word)

    for index,word in enumerate(words):
        for p in puncts:
            if p in word:
                words[index]=words[index].replace(p,"")
                

    #print("WORDS: ",words)
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
    #print("QUERY ",query)
    def call_bm25():
        #allDocs=[]
        # for word in relWords:
        webhose_tokens = [# "ecd3d983-093a-4d8d-a7bd-71207dad85a9",
                      "e6c1084e-8b63-42cf-bfe3-8ccd24a3a9b1",
                      "cb5edba5-48ad-4afa-8d69-ab1ff1092835",
                      "de684b78-5b7e-4c6a-a3d4-4efe80f3e1de",
                      "39d754b3-64c2-48a2-ba0e-5d147168bda7",
                      "191c39da-2f67-4af6-9608-460cc6293108",
                      "a4423ef6-f4a3-4231-a0e0-2aa38546facf",
                      "e25db40a-f3c3-4d12-92f0-73251732b389"
                      ] 
        tags_with_tokens = []
        temp = []

        for i in range(len(relWords)):
            temp.append(relWords[i])
            temp.append(webhose_tokens[i % len(webhose_tokens)])
            tags_with_tokens.append(temp)
            temp = []
           
        allDocs = Parallel(n_jobs=5)(delayed(RecomParallel.Scrape)(single_tag_with_token) for single_tag_with_token in tags_with_tokens)
        # for word in relWords:
        #   print ("WORD IS ",word)
        #   similarDocs = RecomParallel.Scrape(word)
        #   allDocs.append(similarDocs)
        return allDocs

    allDocs=call_bm25()





    #4D list ---  [ [ [[title],[text]],[[title],[text]] for query1 ]     [[[]]]   ]
    #print("ALL DOc  ")
    # result=RecomSemantic.rec(starred_doc,summaries)
    # print("\n\nRES:",result)
    # for doc in allDocs:
    #   print("\n",doc)
        # f1.write(doc)
        # f1.write("\n")

    temp=[]
    for queryList in allDocs:
        for eachDoc in queryList:
            temp.append(eachDoc)

    allDocs=temp
    # for doc in allDocs:
    #   print(doc)
    if len(allDocs) == 0:
        print("Cannot find relevant articles")
        return "" 
    final = recomMatch.bm25(query,allDocs)
    summary=[]
    index=1
    for doc in final:
        f=open(""+str(index)+".txt","w")
        f.write(doc[0][0])
        f.write("\n\n")
        f.write(doc[1][0])
        f.close()
        index=index+1

        sdoc=SingleDocSumm.bm25([doc])
        if sdoc not in summary:
            summary.append([sdoc])

    #print("SUMMARIES:....")
    ans=""
    for index in range(len(summary)):
        #print(summary[index][0],"\n",index,"\n\n\n")
        ans = "Article " + str(index+1) + ": " 
        print(ans)
        print("~~")
        ans = summary[index][0]
        print(ans)
        print("\n")
        print("~~")
    # ans += "Article " + str(index) +  ": \n"
    # ans += summary[index+1][0]
    # print(ans)
    return ans

# def getTitles():
#   path="/home/sai/14IT152/6thsem/IR/project/Recom/docs/"
#   title=[]
#   for fname in os.listdir(path):
#       f=open(os.path.join(path, fname),"r")
#       line=f.readline()
#       title.append([line,int(fname.split(".")[0])])
#       f.close()
#   return title

# ans=recom(8)
# print(ans)

def getTitles():
    path="..\\sentimental_analysis\\docs\\"
    titleDict = dict()
    titles=""
    for fname in os.listdir(path):
        f=open(os.path.join(path, fname),"r", encoding='utf-8')
        line=f.readline()
        line=line.replace("\n","")
        titleDict[line]=int(fname.split(".")[0])
        titles+=line+"~~"
        f.close()
    titles=titles[:len(titles)-2]
    return titleDict

def func(title, titleDict):
    recom(titleDict[title])

if __name__ == "__main__":
    titleDict = getTitles()
    query = sys.argv[1]
    func(query, titleDict)
