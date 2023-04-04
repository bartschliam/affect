import praw
import re
from dotenv import load_dotenv
import os
import emoji
import time
import json
from pprint import pprint
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from json.decoder import JSONDecodeError
import matplotlib.pyplot as plt
from itertools import zip_longest
from matplotlib.font_manager import FontProperties
import numpy as np


def load_credentials():
    load_dotenv()
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')
    password = os.getenv('password')
    reddit_username = os.getenv('reddit_username')
    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent='Affect Analysis Bot for various subreddits v1.0 by u/username',
        password=password,
        username=reddit_username)
    return reddit


def query_api():
    reddit = load_credentials()
    subreddits = [
        'cloudwater',
        'aww',
        'beauty',
        'bunnies',
        'comics',
        'design',
        'facepalm',
        'fashion',
        'funny',
        'gaming',
        'gardening',
        'hiking',
        'lgbt',
        'music',
        'skateboarding',
        'snowboarding',
        'spirituality',
        'travel',
        'emojipasta'
    ]
    num_posts = 1
    found = False
    last_request_time = time.time()
    sentiment = SentimentIntensityAnalyzer()
    nltk.download('stopwords')
    nltk.download('punkt')
    stop_words = set(stopwords.words('english'))
    try:
        with open('titles_and_emojis.json', 'r') as f:
            titles_and_emojis = json.load(f)
    except JSONDecodeError:
        titles_and_emojis = {}
        pass
    if 'searched_subs' not in titles_and_emojis:
        titles_and_emojis['searched_subs'] = {
            'count': 0
        }
    if 'searched_posts' not in titles_and_emojis:
        titles_and_emojis['searched_posts'] = {
            'count': 0,
            'found': 0
        }
    for subreddit in subreddits:
        print(f'Subreddit: {subreddit}')
        if subreddit not in titles_and_emojis['searched_subs']:
            titles_and_emojis['searched_subs'][subreddit] = {}
            titles_and_emojis['searched_subs'][subreddit]['count'] = 0
            titles_and_emojis['searched_subs'][subreddit]['topics'] = []
            titles_and_emojis['searched_subs']['count'] += 1

        for post_index, post in enumerate(reddit.subreddit(subreddit).new(limit=num_posts)):
            print(f"Number: {post_index}, Post: {post.title}")
            titles_and_emojis['searched_posts']['count'] += 1
            if last_request_time is not None and time.time() - last_request_time < 1:
                time_to_wait = 1 - (time.time() - last_request_time)
                time.sleep(time_to_wait)
            title = post.title
            title = ' '.join([word for word in word_tokenize(title) if word.lower() not in stop_words])
            emojis = [c for c in title if c in emoji.EMOJI_DATA]
            if emojis:
                post_id = post.id
                for emoji_code in emojis:
                    if emoji_code in titles_and_emojis:
                        if post_id not in titles_and_emojis[emoji_code]['ids']:
                            titles_and_emojis[emoji_code]['frequency'] += 1
                            titles_and_emojis[emoji_code]['subreddits'].append(subreddit)
                            titles_and_emojis[emoji_code]['ids'].append(post_id)
                            titles_and_emojis[emoji_code]['sentiment'].append(sentiment.polarity_scores(title))
                            titles_and_emojis['searched_posts']['found'] += 1
                            titles_and_emojis['searched_subs'][subreddit]['count'] += 1
                    else:
                        titles_and_emojis[emoji_code] = {}
                        titles_and_emojis[emoji_code]['frequency'] = 1
                        titles_and_emojis[emoji_code]['subreddits'] = [subreddit]
                        titles_and_emojis[emoji_code]['ids'] = [post_id]
                        titles_and_emojis[emoji_code]['sentiment'] = [sentiment.polarity_scores(title)]
                        titles_and_emojis['searched_posts']['found'] += 1
                        titles_and_emojis['searched_subs'][subreddit] += 1
                # found = True
            last_request_time = time.time()
            if found:
                break
        if found:
            break
    with open('titles_and_emojis.json', 'w') as f:
        json.dump(titles_and_emojis, f)
    return


def visualize():
    with open('titles_and_emojis.json', 'r') as f:
        data = json.load(f)
    # barchart_subreddit(data)
    # average_subreddit(data)
    heatmap(data)
    return


def heatmap(data):

    return


def average_subreddit(data):
    neg_scores, neu_scores, pos_scores, compound_scores = {}, {}, {}, {}
    for key, value in data.items():
        if key not in ['searched_subs', 'searched_posts']:
            for i, subreddit in enumerate(value["subreddits"]):
                if subreddit not in neg_scores:
                    neg_scores[subreddit] = 0
                if subreddit not in neu_scores:
                    neu_scores[subreddit] = 0
                if subreddit not in pos_scores:
                    pos_scores[subreddit] = 0
                if subreddit not in compound_scores:
                    compound_scores[subreddit] = 0
                neg_scores[subreddit] += value["sentiment"][i]["neg"]
                neu_scores[subreddit] += value["sentiment"][i]["neu"]
                pos_scores[subreddit] += value["sentiment"][i]["pos"]
                compound_scores[subreddit] += value["sentiment"][i]["compound"]
    subreddits = list(neg_scores.keys())
    sorted_subreddits = sorted(subreddits, key=lambda x: neg_scores[x] + neu_scores[x] + pos_scores[x] + compound_scores[x])
    plt.bar(sorted_subreddits, [neg_scores[subreddit] for subreddit in sorted_subreddits], color='r', label='Negative')
    plt.bar(sorted_subreddits, [neu_scores[subreddit] for subreddit in sorted_subreddits], color='b', bottom=[neg_scores[subreddit] for subreddit in sorted_subreddits], label='Neutral')
    plt.bar(sorted_subreddits, [pos_scores[subreddit] for subreddit in sorted_subreddits], color='g', bottom=[
            neg_scores[subreddit] + neu_scores[subreddit] for subreddit in sorted_subreddits], label='Positive')
    plt.bar(sorted_subreddits, [compound_scores[subreddit] for subreddit in sorted_subreddits], color='orange', bottom=[
            neg_scores[subreddit] + neu_scores[subreddit] + pos_scores[subreddit] for subreddit in sorted_subreddits], label='Compound')
    plt.xlabel('Subreddits')
    plt.ylabel('Sentiment Scores')
    plt.title('Sentiment Scores by Subreddit')
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()
    return


def barchart_subreddit(data):
    sorted_data = {}
    for subreddit, data in data["searched_subs"].items():
        if subreddit != "count":
            sorted_data[subreddit] = data['count']
    sorted_data = dict(sorted(sorted_data.items(), key=lambda item: item[1]))
    plt.bar(sorted_data.keys(), sorted_data.values())
    plt.xticks(rotation=45)
    plt.title('Subreddit Emoji Frequency')
    plt.ylabel('Emoji Count')
    plt.show()
    return


def main():
    # query_api()
    visualize()
    return


if __name__ == '__main__':
    main()
