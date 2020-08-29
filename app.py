import struct
from io import BytesIO

import pandas as pd
from flask import Flask, render_template, url_for, request, flash, session, send_file
import mysql.connector
import re
from wordcloud import WordCloud, STOPWORDS, wordcloud
import matplotlib.pyplot as plt
import  collections
from collections import Counter

from collections import Counter




from flask_mysqldb import MySQL
from mysqlx.protobuf.mysqlx_datatypes_pb2 import Object
from sklearn.feature_extraction.text import CountVectorizer
from werkzeug.debug import console

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'covidtweets'

mysql = MySQL(app)



@app.route('/')
def home():
	return render_template('index.html')


@app.route('/usa',methods=['POST'])
def usaload():
	stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
				  "you'd", 'your', 'yours', 'yourself',
				  'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
				  'its', 'itself', 'they', 'them', 'their',
				  'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
				  'am', 'is', 'are',
				  'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
				  'a', 'an', 'the', 'and', 'but', 'if',
				  'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
				  'between', 'into', 'through', 'during', 'before',
				  'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
				  'again', 'further', 'then', 'once', 'here',
				  'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
				  'some', 'such', 'no', 'nor', 'not', 'only',
				  'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
				  "should've", 'now', 'd', 'll', 'm', 'o',
				  're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't",
				  'hadn', "hadn't", 'hasn', "hasn't", 'haven',
				  "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan',
				  "shan't", 'shouldn', "shouldn't", 'wasn',
				  "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
	if request.method == "POST":
		countryname = 'USA'

	cur = mysql.connection.cursor()

	# getting tweets related to country
	cur.execute(
		"SELECT  tweet_without_stopwords from tweetss WHERE user_location LIKE %s ", (countryname,))

	alltweets = cur.fetchall()
	alltweets_size = len(alltweets)

	# Initializing Dictionary
	d = {}

	# Count number of times each word comes up in list of words (in dictionary)
	for word in alltweets:
		d[word] = 0,

		if word not in d:
			d[word] += 1

	word_freq = []

	for key, value in d.items():
		word_freq.append((value, key))
	word_freq.sort(reverse=True)

	def Extract(lst):
		return [item[0] for item in lst]

	def Extract1(lst):
		return [item[1] for item in lst]

	word_frequency = Extract(word_freq)
	word = Extract1(word_freq)

	li = re.sub(r"[()]", " ", str(alltweets))

	# generate word cloud
	stripped_text = [word for word in str(li).split() if word not in stop_words and len(word) >= 2]

	word_freqs = Counter(stripped_text)
	word_freqs = dict(word_freqs)

	word_freqs_js = []

	for key, value in word_freqs.items():
		temp = {"text": key, "size": value}
		word_freqs_js.append(temp)

	max_freq = max(word_freqs.values())

	# getting positive tweets related to country
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE'", (countryname,))

	positiveTweets = cur.fetchall()
	positiveTweets_size = len(positiveTweets)

	# getting negative tweets related to country
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE positive_tweet='FALSE' AND user_location LIKE %s", (countryname,))

	negativeTweets = cur.fetchall()
	negativeTweets_size = len(negativeTweets)

	# for display :positive tweets
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE' LIMIT 5", (countryname,))

	positiveTweetsDisplay = cur.fetchall()

	posUnedited = re.sub(r"[(),""]", "", str(positiveTweetsDisplay))

	posEditedTweet = re.split(r"['']", str(posUnedited))

	# for display :negative tweets
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='FALSE' LIMIT 5", (countryname,))
	negativeTweetsDisplay = cur.fetchall()

	negUnedited = re.sub(r"[(),""]", "", str(negativeTweetsDisplay))
	negEditedTweet = re.split(r"['']", str(negUnedited))

	return render_template('display.html',positiveTweetsDisplay=posEditedTweet,positiveTweets_size=positiveTweets_size,negativeTweetsDisplay=negEditedTweet,
						   negativeTweets_size=negativeTweets_size,countryname=countryname,alltweets_size=alltweets_size,word=word,
						   word_frequency=word_frequency,alltweets=alltweets,word_freq=word_freq,word_freqs=word_freqs_js, max_freq=max_freq)


@app.route('/uk',methods=['POST'])
def ukload():
	stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
				  "you'd", 'your', 'yours', 'yourself',
				  'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
				  'its', 'itself', 'they', 'them', 'their',
				  'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
				  'am', 'is', 'are',
				  'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
				  'a', 'an', 'the', 'and', 'but', 'if',
				  'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
				  'between', 'into', 'through', 'during', 'before',
				  'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
				  'again', 'further', 'then', 'once', 'here',
				  'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
				  'some', 'such', 'no', 'nor', 'not', 'only',
				  'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
				  "should've", 'now', 'd', 'll', 'm', 'o',
				  're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't",
				  'hadn', "hadn't", 'hasn', "hasn't", 'haven',
				  "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan',
				  "shan't", 'shouldn', "shouldn't", 'wasn',
				  "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
	if request.method == "POST":
		countryname = 'UK'

	cur = mysql.connection.cursor()

	# getting tweets related to country
	cur.execute(
		"SELECT  tweet_without_stopwords from tweetss WHERE user_location LIKE %s ", (countryname,))

	alltweets = cur.fetchall()
	alltweets_size = len(alltweets)

	# Initializing Dictionary
	d = {}

	# Count number of times each word comes up in list of words (in dictionary)
	for word in alltweets:
		d[word] = 0,

		if word not in d:
			d[word] += 1

	word_freq = []

	for key, value in d.items():
		word_freq.append((value, key))
	word_freq.sort(reverse=True)

	def Extract(lst):
		return [item[0] for item in lst]

	def Extract1(lst):
		return [item[1] for item in lst]

	word_frequency = Extract(word_freq)
	word = Extract1(word_freq)

	li = re.sub(r"[()]", " ", str(alltweets))

	# generate word cloud
	stripped_text = [word for word in str(li).split() if word not in stop_words and len(word) >= 2]

	word_freqs = Counter(stripped_text)
	word_freqs = dict(word_freqs)

	word_freqs_js = []

	for key, value in word_freqs.items():
		temp = {"text": key, "size": value}
		word_freqs_js.append(temp)

	max_freq = max(word_freqs.values())

	# getting positive tweets related to country
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE'", (countryname,))

	positiveTweets = cur.fetchall()
	positiveTweets_size = len(positiveTweets)

	# getting negative tweets related to country
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE positive_tweet='FALSE' AND user_location LIKE %s", (countryname,))

	negativeTweets = cur.fetchall()
	negativeTweets_size = len(negativeTweets)

	# for display :positive tweets
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE' LIMIT 5", (countryname,))

	positiveTweetsDisplay = cur.fetchall()

	posUnedited = re.sub(r"[(),""]", "", str(positiveTweetsDisplay))

	posEditedTweet = re.split(r"['']", str(posUnedited))

	# for display :negative tweets
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='FALSE' LIMIT 5", (countryname,))
	negativeTweetsDisplay = cur.fetchall()

	negUnedited = re.sub(r"[(),""]", "", str(negativeTweetsDisplay))
	negEditedTweet = re.split(r"['']", str(negUnedited))

	return render_template('display.html',positiveTweetsDisplay=posEditedTweet,positiveTweets_size=positiveTweets_size,negativeTweetsDisplay=negEditedTweet,
						   negativeTweets_size=negativeTweets_size,countryname=countryname,alltweets_size=alltweets_size,word=word,
						   word_frequency=word_frequency,alltweets=alltweets,word_freq=word_freq,word_freqs=word_freqs_js, max_freq=max_freq)


@app.route('/france',methods=['POST'])
def franceload():
	stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
				  "you'd", 'your', 'yours', 'yourself',
				  'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
				  'its', 'itself', 'they', 'them', 'their',
				  'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
				  'am', 'is', 'are',
				  'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
				  'a', 'an', 'the', 'and', 'but', 'if',
				  'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
				  'between', 'into', 'through', 'during', 'before',
				  'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
				  'again', 'further', 'then', 'once', 'here',
				  'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
				  'some', 'such', 'no', 'nor', 'not', 'only',
				  'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
				  "should've", 'now', 'd', 'll', 'm', 'o',
				  're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't",
				  'hadn', "hadn't", 'hasn', "hasn't", 'haven',
				  "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan',
				  "shan't", 'shouldn', "shouldn't", 'wasn',
				  "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
	if request.method == "POST":
		countryname = 'France'

	cur = mysql.connection.cursor()

	# getting tweets related to country
	cur.execute(
		"SELECT  tweet_without_stopwords from tweetss WHERE user_location LIKE %s ", (countryname,))

	alltweets = cur.fetchall()
	alltweets_size = len(alltweets)

	# Initializing Dictionary
	d = {}

	# Count number of times each word comes up in list of words (in dictionary)
	for word in alltweets:
		d[word] = 0,

		if word not in d:
			d[word] += 1

	word_freq = []

	for key, value in d.items():
		word_freq.append((value, key))
	word_freq.sort(reverse=True)

	def Extract(lst):
		return [item[0] for item in lst]

	def Extract1(lst):
		return [item[1] for item in lst]

	word_frequency = Extract(word_freq)
	word = Extract1(word_freq)

	li = re.sub(r"[()]", " ", str(alltweets))

	# generate word cloud
	stripped_text = [word for word in str(li).split() if word not in stop_words and len(word) >= 2]

	word_freqs = Counter(stripped_text)
	word_freqs = dict(word_freqs)

	word_freqs_js = []

	for key, value in word_freqs.items():
		temp = {"text": key, "size": value}
		word_freqs_js.append(temp)

	max_freq = max(word_freqs.values())

	# getting positive tweets related to country
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE'", (countryname,))

	positiveTweets = cur.fetchall()
	positiveTweets_size = len(positiveTweets)

	# getting negative tweets related to country
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE positive_tweet='FALSE' AND user_location LIKE %s", (countryname,))

	negativeTweets = cur.fetchall()
	negativeTweets_size = len(negativeTweets)

	# for display :positive tweets
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE' LIMIT 5", (countryname,))

	positiveTweetsDisplay = cur.fetchall()

	posUnedited = re.sub(r"[(),""]", "", str(positiveTweetsDisplay))

	posEditedTweet = re.split(r"['']", str(posUnedited))

	# for display :negative tweets
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='FALSE' LIMIT 5", (countryname,))
	negativeTweetsDisplay = cur.fetchall()

	negUnedited = re.sub(r"[(),""]", "", str(negativeTweetsDisplay))
	negEditedTweet = re.split(r"['']", str(negUnedited))

	return render_template('display.html',positiveTweetsDisplay=posEditedTweet,positiveTweets_size=positiveTweets_size,negativeTweetsDisplay=negEditedTweet,
						   negativeTweets_size=negativeTweets_size,countryname=countryname,alltweets_size=alltweets_size,word=word,
						   word_frequency=word_frequency,alltweets=alltweets,word_freq=word_freq,word_freqs=word_freqs_js, max_freq=max_freq)

@app.route('/spain',methods=['POST'])
def spainload():
	stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
				  "you'd", 'your', 'yours', 'yourself',
				  'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
				  'its', 'itself', 'they', 'them', 'their',
				  'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
				  'am', 'is', 'are',
				  'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
				  'a', 'an', 'the', 'and', 'but', 'if',
				  'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
				  'between', 'into', 'through', 'during', 'before',
				  'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
				  'again', 'further', 'then', 'once', 'here',
				  'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
				  'some', 'such', 'no', 'nor', 'not', 'only',
				  'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
				  "should've", 'now', 'd', 'll', 'm', 'o',
				  're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't",
				  'hadn', "hadn't", 'hasn', "hasn't", 'haven',
				  "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan',
				  "shan't", 'shouldn', "shouldn't", 'wasn',
				  "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
	if request.method == "POST":
		countryname = 'Spain'

	cur = mysql.connection.cursor()

	# getting tweets related to country
	cur.execute(
		"SELECT  tweet_without_stopwords from tweetss WHERE user_location LIKE %s ", (countryname,))

	alltweets = cur.fetchall()
	alltweets_size = len(alltweets)

	# Initializing Dictionary
	d = {}

	# Count number of times each word comes up in list of words (in dictionary)
	for word in alltweets:
		d[word] = 0,

		if word not in d:
			d[word] += 1

	word_freq = []

	for key, value in d.items():
		word_freq.append((value, key))
	word_freq.sort(reverse=True)

	def Extract(lst):
		return [item[0] for item in lst]

	def Extract1(lst):
		return [item[1] for item in lst]

	word_frequency = Extract(word_freq)
	word = Extract1(word_freq)

	li = re.sub(r"[()]", " ", str(alltweets))

	# generate word cloud
	stripped_text = [word for word in str(li).split() if word not in stop_words and len(word) >= 2]

	word_freqs = Counter(stripped_text)
	word_freqs = dict(word_freqs)

	word_freqs_js = []

	for key, value in word_freqs.items():
		temp = {"text": key, "size": value}
		word_freqs_js.append(temp)

	max_freq = max(word_freqs.values())

	# getting positive tweets related to country
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE'", (countryname,))

	positiveTweets = cur.fetchall()
	positiveTweets_size = len(positiveTweets)

	# getting negative tweets related to country
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE positive_tweet='FALSE' AND user_location LIKE %s", (countryname,))

	negativeTweets = cur.fetchall()
	negativeTweets_size = len(negativeTweets)

	# for display :positive tweets
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE' LIMIT 5", (countryname,))

	positiveTweetsDisplay = cur.fetchall()

	posUnedited = re.sub(r"[(),""]", "", str(positiveTweetsDisplay))

	posEditedTweet = re.split(r"['']", str(posUnedited))

	# for display :negative tweets
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='FALSE' LIMIT 5", (countryname,))
	negativeTweetsDisplay = cur.fetchall()

	negUnedited = re.sub(r"[(),""]", "", str(negativeTweetsDisplay))
	negEditedTweet = re.split(r"['']", str(negUnedited))

	return render_template('display.html',positiveTweetsDisplay=posEditedTweet,positiveTweets_size=positiveTweets_size,negativeTweetsDisplay=negEditedTweet,
						   negativeTweets_size=negativeTweets_size,countryname=countryname,alltweets_size=alltweets_size,word=word,
						   word_frequency=word_frequency,alltweets=alltweets,word_freq=word_freq,word_freqs=word_freqs_js, max_freq=max_freq)

@app.route('/italy',methods=['POST'])
def italyload():
	stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll",
				  "you'd", 'your', 'yours', 'yourself',
				  'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
				  'its', 'itself', 'they', 'them', 'their',
				  'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those',
				  'am', 'is', 'are',
				  'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
				  'a', 'an', 'the', 'and', 'but', 'if',
				  'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
				  'between', 'into', 'through', 'during', 'before',
				  'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under',
				  'again', 'further', 'then', 'once', 'here',
				  'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other',
				  'some', 'such', 'no', 'nor', 'not', 'only',
				  'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should',
				  "should've", 'now', 'd', 'll', 'm', 'o',
				  're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't",
				  'hadn', "hadn't", 'hasn', "hasn't", 'haven',
				  "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan',
				  "shan't", 'shouldn', "shouldn't", 'wasn',
				  "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
	if request.method == "POST":
		countryname = 'Italy'

	cur = mysql.connection.cursor()

	# getting tweets related to country
	cur.execute(
		"SELECT  tweet_without_stopwords from tweetss WHERE user_location LIKE %s ", (countryname,))

	alltweets = cur.fetchall()
	alltweets_size = len(alltweets)

	# Initializing Dictionary
	d = {}

	# Count number of times each word comes up in list of words (in dictionary)
	for word in alltweets:
		d[word] = 0,

		if word not in d:
			d[word] += 1

	word_freq = []

	for key, value in d.items():
		word_freq.append((value, key))
	word_freq.sort(reverse=True)

	def Extract(lst):
		return [item[0] for item in lst]

	def Extract1(lst):
		return [item[1] for item in lst]

	word_frequency = Extract(word_freq)
	word = Extract1(word_freq)

	li = re.sub(r"[()]", " ", str(alltweets))

	# generate word cloud
	stripped_text = [word for word in str(li).split() if word not in stop_words and len(word) >= 2]

	word_freqs = Counter(stripped_text)
	word_freqs = dict(word_freqs)

	word_freqs_js = []

	for key, value in word_freqs.items():
		temp = {"text": key, "size": value}
		word_freqs_js.append(temp)

	max_freq = max(word_freqs.values())

	# getting positive tweets related to country
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE'", (countryname,))

	positiveTweets = cur.fetchall()
	positiveTweets_size = len(positiveTweets)

	# getting negative tweets related to country
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE positive_tweet='FALSE' AND user_location LIKE %s", (countryname,))

	negativeTweets = cur.fetchall()
	negativeTweets_size = len(negativeTweets)

	# for display :positive tweets
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE' LIMIT 5", (countryname,))

	positiveTweetsDisplay = cur.fetchall()

	posUnedited = re.sub(r"[(),""]", "", str(positiveTweetsDisplay))

	posEditedTweet = re.split(r"['']", str(posUnedited))

	# for display :negative tweets
	cur.execute(
		"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='FALSE' LIMIT 5", (countryname,))
	negativeTweetsDisplay = cur.fetchall()

	negUnedited = re.sub(r"[(),""]", "", str(negativeTweetsDisplay))
	negEditedTweet = re.split(r"['']", str(negUnedited))

	return render_template('display.html',positiveTweetsDisplay=posEditedTweet,positiveTweets_size=positiveTweets_size,negativeTweetsDisplay=negEditedTweet,
						   negativeTweets_size=negativeTweets_size,countryname=countryname,alltweets_size=alltweets_size,word=word,
						   word_frequency=word_frequency,alltweets=alltweets,word_freq=word_freq,word_freqs=word_freqs_js, max_freq=max_freq)

@app.route('/result',methods=['POST'])
def result():
	pat_1 = r"(?:\@|https?\://)\S+"
	pat_2 = r'#\w+ ?'
	combined_pat = r'|'.join((pat_1, pat_2))
	www_pat = r'www.[^ ]+'
	html_tag = r'<[^>]+>'
	stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself',
				  'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their',
				  'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
				  'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
				  'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before',
				  'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here',
				  'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
				  'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 'o',
				  're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven',
				  "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn',
				  "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"]
	if request.method == "POST":

		countryname = request.form['name']
		cur = mysql.connection.cursor()


       #getting tweets related to country
		cur.execute(
			"SELECT  tweet_without_stopwords from tweetss WHERE user_location LIKE %s ",(countryname,))

		alltweets = cur.fetchall()
		alltweets_size=len(alltweets)



		# Initializing Dictionary
		d = {}

		# Count number of times each word comes up in list of words (in dictionary)
		for word in alltweets:
			d[word] = 0,

			if word not in d:
			    d[word] += 1

		word_freq = []

		for key, value in d.items():
			word_freq.append((value, key))
		word_freq.sort(reverse=True)

		def Extract(lst):
			return [item[0] for item in lst]

		def Extract1(lst):
			return [item[1] for item in lst]

		word_frequency = Extract(word_freq)
		word = Extract1(word_freq)

		li= re.sub(r"[()]", " ", str(alltweets))



		#generate word cloud
		stripped_text = [word for word in str(li).split() if word not in stop_words and len(word)>=2]

		word_freqs = Counter(stripped_text)
		word_freqs = dict(word_freqs)

		word_freqs_js = []

		for key, value in word_freqs.items():
			temp = {"text": key, "size": value}
			word_freqs_js.append(temp)

		max_freq = max(word_freqs.values())

		#getting positive tweets related to country
		cur.execute(
			"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE'", (countryname,))

		positiveTweets = cur.fetchall()
		positiveTweets_size=len(positiveTweets)

        #getting negative tweets related to country
		cur.execute(
			"SELECT  displayTweets from tweetss WHERE positive_tweet='FALSE' AND user_location LIKE %s", (countryname,))

		negativeTweets = cur.fetchall()
		negativeTweets_size = len(negativeTweets)



	    #for display :positive tweets
		cur.execute(
			"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='TRUE' LIMIT 4", (countryname,))

		positiveTweetsDisplay = cur.fetchall()

		posUnedited = re.sub(r"[(),""]", "", str(positiveTweetsDisplay))

		posEditedTweet = re.split(r"['']", str(posUnedited))


		# for display :negative tweets
		cur.execute(
			"SELECT  displayTweets from tweetss WHERE user_location LIKE %s AND positive_tweet='FALSE' LIMIT 4", (countryname,))
		negativeTweetsDisplay = cur.fetchall()

		negUnedited = re.sub(r"[(),""]","", str(negativeTweetsDisplay))
		negEditedTweet = re.split(r"['']", str(negUnedited))

	return render_template('display.html',positiveTweetsDisplay=posEditedTweet,positiveTweets_size=positiveTweets_size,negativeTweetsDisplay=negEditedTweet,
						   negativeTweets_size=negativeTweets_size,countryname=countryname,alltweets_size=alltweets_size,word=word,
						   word_frequency=word_frequency,alltweets=alltweets,word_freq=word_freq,word_freqs=word_freqs_js, max_freq=max_freq)


if __name__ == '__main__':
	app.run(debug=True)