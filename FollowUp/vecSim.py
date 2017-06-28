import re, math
from collections import Counter


def vecSim(doc1,doc2):
	WORD = re.compile(r'\w+')
	def get_cosine(vec1, vec2):
		intersection = set(vec1.keys()) & set(vec2.keys())
		numerator = sum([vec1[x] * vec2[x] for x in intersection])

		sum1 = sum([vec1[x]**2 for x in vec1.keys()])
		sum2 = sum([vec2[x]**2 for x in vec2.keys()])
		denominator = math.sqrt(sum1) * math.sqrt(sum2)

		if not denominator:
			return 0.0
		else:
			return float(numerator) / denominator

	def text_to_vector(text):
		words = WORD.findall(text)
		return Counter(words)

	# input_doc=open("/home/sai/14IT152/6thsem/IR/project/web_service_retrieval-master/owls/docs/doc1.txt","r").readlines()
	# for inp in input_doc:
	# 	inp.replace("\n","")
	# input_doc="".join(input_doc)


	# input_doc2=open("/home/sai/14IT152/6thsem/IR/project/web_service_retrieval-master/owls/docs/doc2.txt","r").readlines()
	# for inp in input_doc2:
	# 	inp.replace("\n","")
	# input_doc2="".join(input_doc2)


	
	vector1 = text_to_vector(doc1)
	vector2 = text_to_vector(doc2)
	

	cosine = get_cosine(vector1, vector2)

	#print('Cosine:', cosine)
	return cosine
