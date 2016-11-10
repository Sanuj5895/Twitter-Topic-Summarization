import tweepy
import json
import operator
from operator import itemgetter
from datetime import datetime
import re
import os

def setAPI():
    # Consumer keys and access tokens, used for OAuth.
##    consumer_key =
##    consumer_secret =
##    access_token =
##    access_token_secret =

    # OAuth process, using the keys and tokens
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth),auth

def getTrends(method):
##      print api.trends_closest(lat=tweet_location_lat,long=tweet_location_long) #WOEID
##    DELHI (20070458) - tweet_location_lat=28.7041
##    tweet_location_long=77.1025
    global api
    tweet_location_lat=40.7128 #NYC
    tweet_location_long=-74.0059

    if method == 1: #Get from API and write to file
        trends = api.trends_place(2459115) #returned from prev comand
        with open('newtrends.txt', 'w') as f:
            json.dump(trends, f)
        #print trends
    with open('newtrends.txt') as infile:
        trends = json.load(infile)
    trends = trends[0]
    trending_topics = {}
    for k in trends['trends']:
        #print k['name']
        if k['name'][0] == '#':
            continue
        if k['tweet_volume'] == None:
            k['tweet_volume'] = 0
        trending_topics[k['name']] = k['tweet_volume']

    #print trending_topics
    sorted_tt = sorted(trending_topics.items(), key=operator.itemgetter(1),reverse = True)

    final_topics = []
    j=0
    for key,value in sorted_tt:
        final_topics.append(str(key))
        #print key
        j+=1
        if j==num_topics:
            break

    return final_topics

def getTweets():
    global auth, final_topics, topic_index, number_of_calls
    api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())
    public_tweets = api.search(q=final_topics[topic_index], lang='en', result_type='recent',count=100) #1-recent

    with open(str(final_topics[topic_index])+'0.txt', 'w') as f:
        json.dump(public_tweets, f)

    #queries and write to file
    for i in xrange(number_of_calls):
        id_list = []
        for k in public_tweets['statuses']:
            id_list.append(k['id'])
        id_list = sorted(id_list)
        public_tweets = api.search(q=final_topics[topic_index], lang='en', result_type='recent',count=100, max_id=id_list[0]) #2-recent
        with open(str(final_topics[topic_index])+str(i+1)+'.txt', 'w') as f:
            json.dump(public_tweets, f)

    public_tweets = api.search(q=final_topics[0], lang='en', result_type='popular',count=100) #3-popular
    with open(str(final_topics[topic_index])+str(i+2)+'.txt', 'w') as f:
        json.dump(public_tweets, f)

def readTweets(selected_topic):
    #read all tweets from file
    dirname = './Outputs/'+selected_topic+'/'
    public_tweets = []
    files = [os.path.join(dirname, f) for f in os.listdir(dirname) if os.path.isfile(os.path.join(dirname, f)) and '.txt' in f]
    for i in xrange(len(files)-1):
        with open('./Outputs/'+selected_topic+'/'+selected_topic+str(i)+'.txt') as infile:
            temp_tweets = json.load(infile)['statuses']
        for k in temp_tweets:
            public_tweets.append(k)
    return public_tweets

def preprocess(public_tweets,selected_topic):
    #Start Preprocessing
    max_tweets_by_user = 5  #Above this value, user tweets removed
    minReputationRatio = 0.01
    minUserAge = 2  #In days
    maxHashTags = 3
    maxURLs = 2
    spam_tweets = []
    user_dict = {}
    #1. Check for spam-bot like users
    currentTime = datetime.now()
    spam_stats = {'hashtags':0,'url':0,'hash+url':0}
    for i in xrange(len(public_tweets)):
        user_id = public_tweets[i]['user']['id']
        if user_id in user_dict:
            k = user_dict[user_id]
            k.append(i)
            user_dict[user_id] = k
        else:
            verification = public_tweets[i]['user']['verified']
            reputation = public_tweets[i]['user']['followers_count']/float(public_tweets[i]['user']['followers_count'] + float(public_tweets[i]['user']['friends_count'])+0.00001)
            creationDate = public_tweets[i]['user']['created_at']
            creationDate = creationDate[0:-11] + creationDate[-5:]
            creationDate = datetime.strptime(creationDate,'%a %b %d %H:%M:%S %Y')
            user_dict[user_id] = [[verification,reputation,creationDate],i]

        #Also check tweets for too many #tags or urls
        hashtags = len(public_tweets[i]['entities']['hashtags'])
        URLs = len(public_tweets[i]['entities']['urls'])
        if hashtags > maxHashTags:
            spam_stats['hashtags']+=1
            spam_tweets.append(public_tweets[i])
            public_tweets[i] = 0
            continue
        if URLs > maxURLs:
            spam_stats['url']+=1
            spam_tweets.append(public_tweets[i])
            public_tweets[i] = 0
            continue
        if URLs == maxURLs and hashtags == maxHashTags-1:
            spam_stats['hash+url']+=1
            spam_tweets.append(public_tweets[i])
            public_tweets[i] = 0
            continue

    a=0
    b=0
    c=0
    a1,b1,c1 = 0,0,0
    for k in user_dict:
        if len(user_dict[k]) - 1 > max_tweets_by_user:
            a1+=1
            for i in user_dict[k][1:]:
                a+=1
                spam_tweets.append(public_tweets[i])
                public_tweets[i] = 0
            continue
        if user_dict[k][0][1] < minReputationRatio:
            b1+=1
            for i in user_dict[k][1:]:
                b+=1
                spam_tweets.append(public_tweets[i])
                public_tweets[i] = 0
            continue
        if (currentTime - user_dict[k][0][2]).days < minUserAge:
            c1+=1
            for i in user_dict[k][1:]:
                c+=1
                spam_tweets.append(public_tweets[i])
                public_tweets[i] = 0

    spam_stats['Users_maxTweets'] = a1
    spam_stats['Users_lowRep'] = b1
    spam_stats['Users_minAge'] = c1

    spam_stats['Tweets_maxTweets'] = a
    spam_stats['Tweets_lowRep'] = b
    spam_stats['Tweets_minAge'] = c

    public_tweets = [x for x in public_tweets if x!=0]

    #2. Remove URLs
    for i in xrange(len(public_tweets)):
        urls = public_tweets[i]['entities']['urls']
        if len(urls) == 0:
            continue
        len_prev = 0    #length of previous URL
        for k in urls:
            k['indices'][0]-=len_prev
            k['indices'][1]-=len_prev
            len_prev+= k['indices'][1] - k['indices'][0]
            public_tweets[i]['text'] =  public_tweets[i]['text'][0:k['indices'][0]] + public_tweets[i]['text'][k['indices'][1]:]

    for i in xrange(len(public_tweets)):
        url_index = public_tweets[i]['text'].find('http')
        if url_index != -1:
            public_tweets[i]['text'] = public_tweets[i]['text'][0:url_index-1]

    for k in public_tweets:
        new = str()
        for l in k['text']:
            if l!='\n':
                new+=l
        k['text'] = new

    #3. Remove @, RT @:
    for k in public_tweets:
        k['text'] = k['text'].rstrip().lstrip()
        while '@' in k['text']:
            pos_start = k['text'].find('@')
            pos_end = pos_start+1
            while True:
                if pos_end == len(k['text']):
                    break
                elif k['text'][pos_end] != ' ':
                    pos_end+=1
                else:
                    break
            k['text'] = k['text'][0:pos_start] + k['text'][pos_end+1:]

        myre = re.compile(u'('
            u'\ud83c[\udf00-\udfff]|'
            u'\ud83d[\udc00-\ude4f\ude80-\udeff]|'
            u'[\u2600-\u26FF\u2700-\u27BF])+',
            re.UNICODE)
        k['text'] = myre.sub(r'', k['text']) # no emoji

        while u'\u2026' in k['text']:
            pos_start = k['text'].find(u'\u2026')
            k['text'] = k['text'][0:pos_start] + k['text'][pos_start+1:]

        while '...' in k['text']:
            pos_start = k['text'].find('...')
            k['text'] = k['text'][0:pos_start] +' '+ k['text'][pos_start+3:]

        if k['text'][0:3] == 'RT ' or k['text'][0:3] == 'rt ':
            k['text'] = k['text'][3:]

        k['text'] = k['text'].rstrip().lstrip()

    #3. Check for Duplicate Tweets
    public_tweets = sorted(public_tweets, key=lambda k: k['text'])  #sorting the list of dictionaries by the tweet text
    spam_stats['duplicate'] = 0
    i=0
    while True:
        if i == len(public_tweets) - 1:
            break
        tweet = public_tweets[i]['text']
        if tweet == public_tweets[i+1]['text']:
            spam_stats['duplicate']+=1
            public_tweets[i+1]['text'] = ''
            for j in xrange(i+2,len(public_tweets)):
                if public_tweets[j]['text'] == tweet:
                    spam_stats['duplicate']+=1
                    public_tweets[j]['text'] = ''
                else:
                    break
            i=j-1
        i+=1

    public_tweets = [x for x in public_tweets if x['text'] != '']

    with open('./Outputs/'+selected_topic+'/Output_'+selected_topic+'.txt', 'w') as text_file:
        for k in public_tweets:
            text_file.write(str((currentTime - user_dict[k['user']['id']][0][2]).days) +'\t'+ str(user_dict[k['user']['id']][0][1]) +'\t'+ str(k['user']['statuses_count']) +'\t'+ str(k['retweet_count']) +'\t'+ k['text'].encode('utf-8') + '\n') #[age,reputation,statuses_count,retweet_count,text]

    return public_tweets,spam_stats,spam_tweets
