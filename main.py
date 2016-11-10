import Tkinter as tk
import os
from finalCode import *
from PR import *

APP_WIDTH = 1000
APP_HEIGHT = 500

topics = []
max_tweets_by_user = 5  #Above this value, user tweets removed
minReputationRatio = 0.01
minUserAge = 2  #In days
maxHashTags = 3
maxURLs = 2
selected_topic = None
with open('Final Trends.txt', 'r') as f:
    for line in f:
        topics.append(line)

class MainApplication(tk.Frame):
    def __init__(self, master):
        self.w = []
        self.mainPage()

    def mainPage(self):
        global topics
        w = self.w
        for i in range(len(w)):
            w[i].destroy()
        del w[:]

        w.append(tk.Label(text = 'Select one of the topics to summarize from the drop-down menu',font = 'bold 13'))
        w[-1].place(x=int(APP_WIDTH/2) - 220, y=10)
        w.append(tk.Label(text = 'These trending topics along with the raw tweets are stored offline. This data was collected over the past week.'))
        w[-1].place(x=int(APP_WIDTH/2) - 285, y=40)

        topics_len = len(topics)
        k = 0
        flag = 0
        for i in xrange(4):
            for j in xrange(4):
                if k == topics_len:
                    flag = 1
                    break

                w.append(tk.Button(text = topics[k],command = lambda t=topics[k]: self.fillTopic(t),height = 1, width = 17, justify = 'center', pady = 5))
                w[-1].place(x = 160*(j)+180,y = 80*(i+1))
                w[-1].myname = topics[k]
                k+=1
            if flag == 1:
                break
        w.append(tk.Button(text = 'Summarize', command = self.openFrame2, state =  'disabled'))
        w[-1].place(x=int(APP_WIDTH/2) - 15, y = APP_HEIGHT - 50)
        w.append(tk.Entry(width=20))
        w[-1].place(x=int(APP_WIDTH/2) - 40, y= 400)

    def fillTopic(self, t):
        global selected_topic
        selected_topic = t.rstrip()
        w = self.w
        w[-1].delete(0,'end')
        w[-1].insert(0,t)
        w[-2].config(state = 'normal')

    def openFrame2(self):
        global selected_topic
        w = self.w
        for i in range(len(w)):
            w[i].destroy()
        del w[:]

        w.append(tk.Label(text = 'Summary of topic: '+selected_topic, font='bold 14'))
        w[-1].place(x=30, y=11)

        w.append(tk.Button(text = 'Back', command = self.mainPage))
        w[-1].place(x=APP_WIDTH-70, y=APP_HEIGHT-50)

        public_tweets = readTweets(selected_topic)
        raw_length = len(public_tweets)
        public_tweets,spam_stats,spam_tweets = preprocess(public_tweets,selected_topic)
        final_length = len(public_tweets)
        res = computeStuff(selected_topic)
        print res

        w.append(tk.Label(text = 'Tweet Statistics',font = 'bold 12'))
        w[-1].place(x=30, y=40)

        w.append(tk.Label(text = 'Total Tweets Retrieved: '+str(raw_length), font = 'bold 10'))
        w[-1].place(x=40, y=65)

        w.append(tk.Label(text = 'Tweets Removed:', font = 'bold 10'))
        w[-1].place(x=40, y=85)

        w.append(tk.Label(text = '- Users with Tweets exceeding maximum allowed Tweets ('+str(max_tweets_by_user)+'): '+str(spam_stats['Users_maxTweets'])))
        w[-1].place(x=50, y=105)

        w.append(tk.Label(text = 'Number of Tweets removed: '+str(spam_stats['Tweets_maxTweets'])))
        w[-1].place(x=64, y=125)

        w.append(tk.Label(text = '- Users with Reputation below minimum required reputation ('+str(minReputationRatio)+'): '+str(spam_stats['Users_lowRep'])))
        w[-1].place(x=50, y=145)

        w.append(tk.Label(text = 'Number of Tweets removed: '+str(spam_stats['Tweets_lowRep'])))
        w[-1].place(x=64, y=165)

        w.append(tk.Label(text = '- Users with age less than minimum required age ('+str(minUserAge)+' days): '+str(spam_stats['Users_minAge'])))
        w[-1].place(x=50, y=185)

        w.append(tk.Label(text = 'Number of Tweets removed: '+str(spam_stats['Tweets_minAge'])))
        w[-1].place(x=64, y=205)

        w.append(tk.Label(text = '- Tweets with more #tags than allowed ('+str(maxHashTags)+'): '+str(spam_stats['hashtags'])))
        w[-1].place(x=50, y=225)

        w.append(tk.Label(text = '- Tweets with more URLs than allowed ('+str(maxURLs)+'): '+str(spam_stats['url'])))
        w[-1].place(x=50, y=245)

        w.append(tk.Label(text = '- Tweets with more #tags + URLs than allowed ('+str(maxHashTags-1)+', '+str(maxURLs)+'): '+str(spam_stats['hash+url'])))
        w[-1].place(x=50, y=265)

        w.append(tk.Label(text = '- Duplicate Tweets removed: '+str(spam_stats['duplicate'])))
        w[-1].place(x=50, y=285)

        w.append(tk.Label(text = 'Tweets left after pre-processing: '+str(final_length), font = 'bold 10'))
        w[-1].place(x=40, y=305)

        w.append(tk.Label(text = 'Summary Generated:', font = 'bold 12'))
        w[-1].place(x=40, y=335)

        w.append(tk.Label(text = res[0], font = 'bold 10'))
        w[-1].place(x=45, y=360)

        w.append(tk.Label(text = res[1], font = 'bold 10'))
        w[-1].place(x=45, y=380)

        gt = []
        with open('GT.txt') as f:
            for line in f:
                gt.append(line)

        for line in gt:
            if selected_topic in line:
                st, GrT,Sco = line.split('\t')

        w.append(tk.Label(text = 'Ground Truth:', font = 'bold 12'))
        w[-1].place(x=40, y=405)

        w.append(tk.Label(text = GrT, font = 'bold 10'))
        w[-1].place(x=45, y=430)

        w.append(tk.Label(text = 'Score: '+Sco, font = 'bold 12'))
        w[-1].place(x=480, y=460)

root = tk.Tk()
root.resizable(width=False,height=False)
root.geometry('{}x{}'.format(APP_WIDTH,APP_HEIGHT))
root.title('Twitter Topics Summarization v0.3b')

MainApplication(root)
root.mainloop()
