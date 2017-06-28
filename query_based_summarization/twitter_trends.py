import tweepy
import sys

# reload(sys)

# sys.setdefaultencoding('utf-8')

consumer_key = 'FnJharJ4P6stzrEvBiYcbsaIf'
consumer_secret = '7dNH82HRru5Tluci22vp4hhAPVb0zvaFCMq8JymO9fHmzH3ueg'
access_token = '4468198941-pe6NFcLPQNsvpa4Makb5qcmQVhBI6dNwcSxdqwL'
access_token_secret = 'VtXRkUeEyuEb0t5SSR7s4JTO14944Ps05XdbYJsebI8UC'
# OAuth process, using the keys and tokens
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
trends1 = api.trends_place(23424848)
# trends1 = api.trends_place(29229014)
data = trends1[0]
# grab the trends
trends = data['trends']
# grab the name from each trends
names = [trend['name'] for trend in trends]
# put all the names together with a ' ' separating them


ipl_teams = ["MI",
             "GL",
             "RCB",
             "KKR",
             "KXIP",
             "SRH",
             "DD",
             "RPS",
             ]

for name in names:
    flag = False
    for team in ipl_teams:
        if team in name:
            print(team, end=' ')
            flag = True
    if not flag:
        name = name.replace('#', '')
        try:
            print(name, end='~~ ')
        except:
            continue
    else:
        print("", end="~~ ")
    # print "TRENDS:",trends1

#
# terms = []
# for index, t in enumerate(trends1):
#     # print "t:",t
#     for key, value in t.items():
#         for v in value:
#             # print "type of :",type(v)
#             if type(v) is dict:
#                 # print "v:",v
#                 for k1, v1 in v.items():
#                     k1 = k1.encode('ascii', 'ignore').decode('ascii')
#                     if k1 == "name":
#                         if v1 is not None:
#                             print(v1)
#
#                             v1 = v1.encode('ascii', 'ignore').decode('ascii')
#
#                             v1 = v1.encode('utf-8')
#                             # print("v1:", type(v1))
#                             terms.append(v1)
#
# print(terms)
"""for t in trends:
    for key in t:
        if key=="" """
# from the end of your code
# trends1 is a list with only one element in it, which is a 
# dict which we'll put in data.

"""
data = trends1[0] 
# grab the trends
trends = data['trends']
# grab the name from each trend
names = [trend['name'] for trend in trends]
# put all the names together with a ' ' separating them
trendsName = ' '.join(names)
print trendsName
"""
