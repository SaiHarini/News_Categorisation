import tweepy
import sys
import re
import html


def get_all_tweets(api, screen_name):
    # Twitter only allows access to a users most recent 3240 tweets with this method
    # initialize a list to hold all the tweepy Tweets
    all_tweets = []
    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=25, include_rts=True, tweet_mode="extended")
    

    for tweet in new_tweets:

        clean_tweet = html.unescape(tweet.full_text) 
        if clean_tweet.startswith("RT"):
            clean_tweet = clean_tweet.split(' ', 2)[2]

        clean_tweet = clean_tweet.replace("Read @ANI_news story", '')
        clean_tweet = clean_tweet.replace("Update", '')
        clean_tweet = clean_tweet.replace("UPDATE", '')
        clean_tweet = clean_tweet.replace("WATCH", '')

        clean_tweet = clean_tweet.replace('\n', '')
        clean_tweet = clean_tweet.replace('@', '')
        clean_tweet = clean_tweet.replace('#', '')
        clean_tweet = re.sub(r'https\S+', '', clean_tweet)
        clean_tweet = clean_tweet.replace('&', ' and ')

        clean_tweet = clean_tweet.replace(':', ' ')
        clean_tweet = clean_tweet.replace('-', ' ')
        clean_tweet = clean_tweet.replace('.', ' ')
        clean_tweet = clean_tweet.replace(',', ' ')
        clean_tweet = re.sub("\\'s", '', clean_tweet)
        clean_tweet = re.sub("\\'", '', clean_tweet)

        
        clean_tweet = re.sub(r'[^\x00-\x7f]', '', clean_tweet)
        all_tweets.append(clean_tweet)
    # [all_tweets.append(''.join([i if ord(i) < 128 else ' ' for i in html.unescape(i.full_text)])) for i in new_tweets]
    
    return all_tweets

if __name__ == "__main__":

    channel = sys.argv[1]
    consumer_key = 'LlLt6OUZ012REwcTTH4nFSNvp'
    consumer_secret = 'ULz858otJGEcOmuiqLp5h8r7pNuYC1eu9jj4BoxOBeDFC4uZF0'
    access_token = '799649676580376576-ibNJTR9rhiZAhXerDR9Uc8I5njv2XYu'
    access_token_secret = 'cVC0IwQ7KRBRzMBlTc2I7b8nPjLAcOVQkV1RL4JZxQ2aM'

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth, wait_on_rate_limit=True) 

    tweets_ANI = get_all_tweets(api, channel)
    for tweet in tweets_ANI:
      print(tweet, end="~~ ")