import os

titleDict=dict()
def getTitles():
	path="/home/sai/14IT152/6thsem/IR/project/FollowUp/docs/"
	
	titles=""
	for fname in os.listdir(path):
		f=open(os.path.join(path, fname),"r")
		line=f.readline()
		
		line=line.replace("\n","")
		#print("line:",line)
		titleDict[line]=int(fname.split(".")[0])
		titles+=line+"~~ "
		f.close()
	titles=titles[:len(titles)-3]
	print(titles)

getTitles()

# def func(title):
# 	global titleDict
# 	#f=open(titleDict[title]+".txt","r")
# 	f=open("docs/"+str(titleDict[title])+".txt")