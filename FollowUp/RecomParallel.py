import webhoseio
import requests
import lxml
import lxml.html
from newspaper import Article,ArticleException
from datetime import datetime, timedelta
import time
import bm25
from joblib import Parallel, delayed
import multiprocessing
import timeit
import recomMatch


class NewsScrapping():
	query = ""
	webhoseio_query = ""
	output = dict()
	text_and_title_file = ""
	days_back = 2  # how old news do we want..used in parameter "ts"
	number_of_articles_to_extract = 0
	final_doc = []
	'''for empty query specify "" '''

	def __init__(self, query):
		self.query = query
		self.webhoseio_query = self.query + \
			" language:(english) (site_type:news)"
		self.text_and_title_file = "text_and_title_file.txt"
		self.number_of_articles_to_extract = 10
		self.config_webhoseio()

	'''config webhoseio with token'''

	def config_webhoseio(self):
		webhoseio.config(token="e6c1084e-8b63-42cf-bfe3-8ccd24a3a9b1")

	'''set different parameters from webhoseio API'''

	def get_webhoseio_query(self):
		# self.webhoseio_query = self.query + " language:(english)"
		return self.webhoseio_query

	'''set the self.output to webhoseio results '''

	def get_results(self):
		# try parameters  domain_rank:<1000  , "ts":ts,
		# ts = self.calculate_timestamp()
		self.output = webhoseio.query(
			"filterWebData", {"q": self.webhoseio_query, "latest": "true"})

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
		##print("NUM CORES", num_cores)
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
		if redirected_url == "@@FROM_STRING_ERROR@@":
			return None
			# continue
		##print(redirected_url)
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
		# ##print(text)

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
			article.parse()
		
		except:
			return "", "@@TEXT_FROM_URL_ERROR@@"
		# '''empty article'''
		# if article.html == "":
		#     return "", "@@TEXT_FROM_URL_ERROR@@"

		# ##print(type(article.title), type(article.text))
		return article.title, article.text
		# return article.title.decode("utf-8").encode("ascii","ignore"), article.text.decode("utf-8").encode("ascii","ignore")

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
			# ##print 'refresh:', refresh[0].attrib['content']
			x = refresh[0].attrib['content'].find('http')
			url = refresh[0].attrib['content'][x:]
			return url
		else:
			return "@@FROM_STRING_ERROR@@"

	def calculate_timestamp(self):
		date_days_ago = datetime.now() - timedelta(days=self.days_back)
		ts = int(time.mktime(date_days_ago.timetuple())) * 1000
		return ts

	def call_bm25(self):
		##print(len(self.final_doc))
		similarDocs = recomMatch.bm25(self.query, self.final_doc)
		return similarDocs


def Scrape(query):
	start = timeit.default_timer()
	my_query = query
	model = NewsScrapping(my_query)
	model.get_results()
	model.start_fetching()
	stop = timeit.default_timer()
	##print("scrapping ", stop - start)
	start = timeit.default_timer()
	smry = model.call_bm25()
	stop = timeit.default_timer()
	#sendThread = news.send(smry)
	# sendThread.start()

	##print("summarizing ", stop - start)
	return smry
# Scrape("trump")
