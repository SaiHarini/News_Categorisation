import webhoseio
import requests
import lxml
import lxml.html
from newspaper import Article
from datetime import datetime, timedelta
import time
from joblib import Parallel, delayed
import multiprocessing
import timeit
import bm25
import sys

class NewsScrapping():
	query = ""
	webhoseio_query = ""
	output = dict()
	text_and_title_file = ""
	#days_back = []  # how old news do we want..used in parameter "ts"
	number_of_articles_to_extract = 0
	final_doc = []
	'''for empty query specify "" '''

	def __init__(self, query, token):
		self.query = query
		self.webhoseio_query = self.query + \
			" language:(english) (site_type:news)"
		self.text_and_title_file = "text_and_title_file.txt"
		self.number_of_articles_to_extract = 10
		self.config_webhoseio(token)

	'''config webhoseio with token'''

	def config_webhoseio(self, token):

		# jaju
		# webhoseio.config(token="ecd3d983-093a-4d8d-a7bd-71207dad85a9")
		# divya
		# webhoseio.config(token="e6c1084e-8b63-42cf-bfe3-8ccd24a3a9b1")
		webhoseio.config(token=token)


	'''set different parameters from webhoseio API'''
	
		
	def get_webhoseio_query(self):
		# self.webhoseio_query = self.query + " language:(english)"
		return self.webhoseio_query

	'''set the self.output to webhoseio results '''

	def get_results(self,days_back):
		# try parameters  domain_rank:<1000  , "ts":ts,
		ts = self.calculate_timestamp(days_back)

		self.output = webhoseio.query(
			"filterWebData", {"q": self.webhoseio_query,"ts":ts})

		'''if less than specified number of articles retrieved..then change that specified number'''
		if(len(self.output['posts']) < self.number_of_articles_to_extract):
			self.number_of_articles_to_extract = len(self.output['posts'])

	'''number of requests left for this account'''

	def get_requests_left(self):
		return self.output['requestsLeft']

	def start_fetching(self):
		inputs = range(self.number_of_articles_to_extract)
		#num_cores = multiprocessing.cpu_count()
		num_cores =10
		#print("NUM CORES", num_cores)
		self.final_doc = Parallel(n_jobs=num_cores, backend="threading")(
			delayed(self.fetch_results_and_store_in_list)(i) for i in inputs)
		self.final_doc = list(filter(None.__ne__, self.final_doc))

	'''open file...find the redirected_url...get text from newspaper library...store in file'''

	def fetch_results_and_store_in_list(self, i):
		# with open(self.text_and_title_file, "w") as text_file:
		# for i in range(len(self.output['posts'])):
		# for i in range(self.number_of_articles_to_extract):
		#     '''encode used to ignore non-ascii values...encode used to convert bytes to string'''
		#     # title = self.output['posts'][i]['thread']['title'].encode('ascii', 'ignore').decode()
		#     #
		#     # if title == '':
		#     #     continue
		url = self.output['posts'][i]['url']
		redirected_url = self.get_redirected_url(url)
		if redirected_url == "@@FROM_STRING_ERROR@@" or redirected_url is None:
			return None
			# continue
		#print(redirected_url)
		# text = self.get_text_from_url(redirected_url).encode('ascii', 'ignore')
		title, text = self.get_text_from_url(redirected_url)
		title = self.remove_non_ascii(title)
		text = self.remove_non_ascii(text)

		if title == '':
			return None
			# continue
		if text == "@@TEXT_FROM_URL_ERROR@@":
			return None
			# continue
		if text == '':
			return None
			# continue

		# textsplit = text.splitlines()
		'''decode used to convert bytes to string '''
		text = text.replace('\n', ' ').replace('\r', ' ')
		# #print(text)

		# article = []
		# article.append(title)
		# article.append(text)
		# self.final_doc.append(article)
		# article = None
		title_list = [title]
		text_list = [text]
		article = [title_list, text_list]
		return article
		# text_file.write(title)
		# text_file.write("\n")
		# text_file.write(text)
		# text_file.write("\n")

	def remove_non_ascii(self, text):
		return ''.join(i for i in text if ord(i) < 128)

	'''helper function for write_results_in_text() ..to get text from url'''

	def get_text_from_url(self, url):
		
		try:
			article = Article(url)

			article.download()
			'''empty article'''
			if article.html == "":
				return "", "@@TEXT_FROM_URL_ERROR@@"

			article.parse()
		except:
			return "", "@@TEXT_FROM_URL_ERROR@@"

		# #print(type(article.title), type(article.text))
		return article.title, article.text
		# return article.title.decode("utf-8").encode("ascii","ignore"),
		# article.text.decode("utf-8").encode("ascii","ignore")

	'''Webhoseio provides omgili url...we need to find redirected urls'''

	def get_redirected_url(self, url):
		r = requests.get(url)
		if not r.text:
			return "@@FROM_STRING_ERROR@@"
		try:
			html = lxml.html.fromstring(r.text)
		except Exception:
			return "@@FROM_STRING_ERROR@@"

		refresh = html.cssselect('meta[http-equiv="refresh"]')
		if refresh:
			# #print 'refresh:', refresh[0].attrib['content']
			x = refresh[0].attrib['content'].find('http')
			url = refresh[0].attrib['content'][x:]
			return url

	def calculate_timestamp(self,days_back):
		date_days_ago = datetime.now() - timedelta(days=days_back)
		ts=int(time.mktime(date_days_ago.timetuple())) * 1000
		return ts

	def call_bm25(self):
		
		smry = bm25.bm25(self.query, self.final_doc)
		#print(len(self.final_doc))
		return smry


def fill_days():
	days_back=[]
	for i in range(1,17):
		days_back.append(i)
	return days_back

def parallelDays(single_day_with_tokens,query):
	#print(single_day_with_tokens)
	day = single_day_with_tokens[0]
	token = single_day_with_tokens[1]

	start = timeit.default_timer()
	my_query = query
	model = NewsScrapping(my_query, token)
	model.get_results(day)
	model.start_fetching()
	stop = timeit.default_timer()
	#print("scrapping ", stop - start)
	start = timeit.default_timer()
	smry=[model.call_bm25()]
	stop = timeit.default_timer()
	return smry

def Scrape(query,webhose_tokens):
	days_back=fill_days()
	temp=[]
	tags_with_tokens=[]
	for i in range(len(days_back)):
		temp.append(days_back[i])
		temp.append(webhose_tokens[i % len(webhose_tokens)])
		tags_with_tokens.append(temp)
		temp = []
	
	sr=[]

	# f = open("I:\\6th semester\\Projects and Lab\\Projects\\IR\\Project\\Background\\Summary.txt", 'w')
	# f.write("")
	# f.close()

	for i in range(0,len(days_back),2):
		f = open("Summary.txt", 'a')
		smry=[]
		smry = Parallel(n_jobs=2)(
			delayed(parallelDays)(single_tag_with_token, query) for single_tag_with_token in tags_with_tokens[i:i+2])
		sr.append(smry)
		print(str(tags_with_tokens[i][0])+" day(s) ago")
		print("~~")
		print(smry[0])
		print("~~")
		print(str(tags_with_tokens[i+1][0])+" day(s) ago")
		print("~~")
		print(smry[1])
		print("~~")

		f.write(str(tags_with_tokens[i][0])+" day(s) ago")
		f.write("~~")
		f.write(str(smry[0][0]))
		f.write("~~")
		f.write(str(tags_with_tokens[i+1][0])+" day(s) ago")
		f.write("~~")
		f.write(str(smry[1][0]))
		f.write("~~")
		f.close()

	s=""
	#print("SMR:",smry)
	for twoSmry in sr:
		for oneSmry in twoSmry:
			#print("onesm:",oneSmry)
			s+=oneSmry[0]+"~~ "
	s=s[:len(s)-3]
	# print(s)
	
	# smry=[]
	# return Parallel(n_jobs=3)(delayed(parallelDays)(day,query)for day in days_back)
	
	#sendThread = news.send(smry)
	# sendThread.start()

	##print("summarizing ", stop - start)
	#return smry

def start(query):
	
	webhose_tokens = [    "e6c1084e-8b63-42cf-bfe3-8ccd24a3a9b1",
						  "cb5edba5-48ad-4afa-8d69-ab1ff1092835",
						  "de684b78-5b7e-4c6a-a3d4-4efe80f3e1de",
						  "39d754b3-64c2-48a2-ba0e-5d147168bda7",
						  "191c39da-2f67-4af6-9608-460cc6293108",
						  "a4423ef6-f4a3-4231-a0e0-2aa38546facf",
						  "e25db40a-f3c3-4d12-92f0-73251732b389"
						  ]

	Scrape(query,webhose_tokens)
	
if __name__ == "__main__":
	query = sys.argv[1]
	start(query)