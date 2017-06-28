import tweepy
from textblob import TextBlob
import html
import re
import news_scrapping, bm25, summary
from joblib import Parallel, delayed
import sys

def get_all_tweets(api, screen_name):
    # Twitter only allows access to a users most recent 3240 tweets with this method
    # initialize a list to hold all the tweepy Tweets
    all_tweets = []
    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=5, include_rts=True, tweet_mode="extended")
    # save most recent tweets
    # all_tweets.extend(new_tweets)

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
    [all_tweets.append(html.unescape(i.full_text)) for i in new_tweets]
    clean_tweets = []
    tags = []
    for tweet in all_tweets:

        # remove RT @channel
        if tweet.startswith("RT"):
            tweet = tweet.split(' ', 2)[2]

        # remove all this shit
        tweet = tweet.replace("Read @ANI_news story", '')
        tweet = tweet.replace("Update", '')
        tweet = tweet.replace("UPDATE", '')
        tweet = tweet.replace("WATCH", '')
        tweet = tweet.replace(':', ' ')
        tweet = tweet.replace('-', ' ')

        tweet = tweet.replace('\n', '')
        tweet = tweet.replace('@', '')
        tweet = tweet.replace('#', '')
        tweet = re.sub("\\'s", '', tweet)
        tweet = re.sub("\\'", '', tweet)

        tweet = re.sub(r'https\S+', '', tweet)

        clean_tweets.append(tweet)
        blob = TextBlob(tweet)
        # print(blob.noun_phrases)
        noun_phrases = [x for x in blob.noun_phrases if x not in unwanted_words]
        tags.append(noun_phrases)
        print(noun_phrases)
        print(tweet)
        noun_phrases = []
        print("--------------------------")

    print("Testing")
    return clean_tweets, tags


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
    print(tags_with_tokens)
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

    # channel = sys.argv[1]
    consumer_key = 'LlLt6OUZ012REwcTTH4nFSNvp'
    consumer_secret = 'ULz858otJGEcOmuiqLp5h8r7pNuYC1eu9jj4BoxOBeDFC4uZF0'
    access_token = '799649676580376576-ibNJTR9rhiZAhXerDR9Uc8I5njv2XYu'
    access_token_secret = 'cVC0IwQ7KRBRzMBlTc2I7b8nPjLAcOVQkV1RL4JZxQ2aM'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True)

    webhose_tokens = [# "ecd3d983-093a-4d8d-a7bd-71207dad85a9",
                      "e6c1084e-8b63-42cf-bfe3-8ccd24a3a9b1",
                      "cb5edba5-48ad-4afa-8d69-ab1ff1092835",
                      "de684b78-5b7e-4c6a-a3d4-4efe80f3e1de",
                      "39d754b3-64c2-48a2-ba0e-5d147168bda7",
                      "191c39da-2f67-4af6-9608-460cc6293108",
                      "a4423ef6-f4a3-4231-a0e0-2aa38546facf",
                      "e25db40a-f3c3-4d12-92f0-73251732b389"
                      ]

    tweets_ANI, tags_ANI = get_all_tweets(api, "ANI_news")

    print("Done")
    f = open('Tweets and summary.txt', 'w')

    # for every tweet
    for i in range(0, len(tags_ANI)):


        complete_query, similar_articles = extract_articles(tags_ANI[i], webhose_tokens)

        if similar_articles == "@@NO_DOCS_AVAILABLE@@":
            f.write(tweets_ANI[i] + "\n")
            f.write(complete_query + "\n")
            f.write("ERROR: Could not extract articles for the given tweet"+ "\n")
            f.close()
            continue

        final_articles = bm25.bm25(complete_query, similar_articles)
        summary_breaking_news = summary.bm25(complete_query, final_articles)
        f.write(tweets_ANI[i] + "\n")
        f.write(complete_query + "\n")
        f.write(summary_breaking_news + "\n")
        f.write("----------------------------------------------------\n")
        print("----------------------------------------------------\n")
        print(tweets_ANI[i])
        print(summary_breaking_news)
        # break
    print("DOne summarizing")
    f.close()

# @PTI_News
