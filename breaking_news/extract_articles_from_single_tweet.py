import tweepy
from textblob import TextBlob
import html
import re
import news_scrapping, bm25, summary
from joblib import Parallel, delayed
import sys


def extract_tags(tweet):
    unwanted_words = ["january", "jan" ,
                      "february", "feb" ,
                      "march",
                      "april",
                      "may",
                      "june",
                      "july",
                      "august", "aug" ,
                      "september", "sept" ,
                      "october", "oct" ,
                      "november", "nov"
                      "december", "dec"

                      "cr",
                      "rs",
                      "lakh",
                      "thousand",
                      "crore",
                      "kg",
                      "gram",
                      "watch",
                      "sources",
                      "watch live",

                      "i",
                      "we",
                      "he",
                      "she",
                      "it",
                      "you",
                      "they",
                      "we're",
                      "source",
                      "media",
                      ]
    tags = []                 
    blob = TextBlob(tweet)
    # print(blob.noun_phrases)
    noun_phrases = [x for x in blob.noun_phrases if x not in unwanted_words]
    tags = noun_phrases
    # print(noun_phrases)
    return tags

def extract_articles(tags, webhose_tokens):

    # temp = zip(tags, webhose_tokens)
    # print(temp)

    tags_with_tokens = []
    temp = []

    for i in range(len(tags)):
        temp.append(tags[i])
        temp.append(webhose_tokens[i % len(webhose_tokens)])
        tags_with_tokens.append(temp)
        temp = []
    # print(tags_with_tokens)
    similar_articles = Parallel(n_jobs=5)(
        delayed(news_scrapping.Scrape)(single_tag_with_token) for single_tag_with_token in tags_with_tokens)

    complete_query = ""
    for tag in tags:
        complete_query += tag + " "

    if similar_articles == []:
        return complete_query, "@@NO_DOCS_AVAILABLE@@"

    temp = []
    for article in similar_articles:
        if article == []:
            continue
        for arti in article:
            temp.append(arti)

    similar_articles = temp
    # for tag in tags:
    #     print("Tag is ", tag)
    #     articles = news_scrapping.Scrape(tag)
    #     similar_articles.extend(articles)
    return complete_query, similar_articles

if __name__ == "__main__":

    tweet = sys.argv[1]
    webhose_tokens = [# "ecd3d983-093a-4d8d-a7bd-71207dad85a9",
                      "e6c1084e-8b63-42cf-bfe3-8ccd24a3a9b1",
                      "cb5edba5-48ad-4afa-8d69-ab1ff1092835",
                      "de684b78-5b7e-4c6a-a3d4-4efe80f3e1de",
                      "39d754b3-64c2-48a2-ba0e-5d147168bda7",
                      "191c39da-2f67-4af6-9608-460cc6293108",
                      "a4423ef6-f4a3-4231-a0e0-2aa38546facf",
                      "e25db40a-f3c3-4d12-92f0-73251732b389"
                      ] 

    tags = extract_tags(tweet)  
    complete_query, similar_articles = extract_articles(tags, webhose_tokens)

    if similar_articles == "@@NO_DOCS_AVAILABLE@@":
        print("ERROR: Could not extract articles for the given tweet")

    final_articles = bm25.bm25(complete_query, similar_articles)
    summary_breaking_news = summary.bm25(complete_query, final_articles)
    # print(tweet + "\n")
    # print(complete_query + "\n")
    print(summary_breaking_news + "\n")
    # print("----------------------------------------------------\n")
