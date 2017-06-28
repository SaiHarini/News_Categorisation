# News_Categorisation

Required Packages:
nltk
textblob
geotext
joblib
datetime
webhoseio
tweepy
webbrowser

Features:

Query based multiple document summarization
Based on the query given by the user, this application collects information from webhoseio and uses modified BM25 for ranking and summarizes the documents using Sum Basic Algorithm.

Summarization of single document
User can get the gist of the document by reading the summary and can save time. Given any document, it gives the summary with 300 (can set to any number required) words.

Follow up of news articles
When the user is interested on a topic, he can opt for following the topic where he can get the updates on it for a set time interval

Background of a particular news article
If the user wants to know what happened before the occurance of a particular event, he can request for background of the article and can get information on it.

Breaking news based on twitter
User can get breaking news based on twitter, as presently its faster for getting latest news.

Sentimental analysis of news articles
User can get to know if an article is positive or not.

Recommendation of news article
Based on the user's follow up topics, he can be recommneded other similar articles.
