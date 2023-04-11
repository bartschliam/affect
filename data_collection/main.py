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
import statistics
import random
import math
import pandas as pd


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
    with open('titles_and_emojis.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    # barchart_subreddit(data)
    average_subreddit(data)
    # heatmap(data, 'compound', 'Compound')
    # heatmap(data, 'pos', 'Positive')
    # heatmap(data, 'neg', 'Negative')
    # heatmap(data, 'neu', 'Neutral')
    # topemoji_sub_table(data)

    return


def heatmap(data, trait, title):
    new_data = dict(list(data.items())[2:])
    emoji_labels = []
    emoji_sizes = []
    emoji_colors = []
    emoji_trait_avgs = []
    subreddit_modes = {}
    subreddit_color_map = {}

    for emoji, sentiment in new_data.items():
        subreddits = []
        for s in sentiment["subreddits"]:
            subreddits.append(s)
        subreddit_mode = statistics.mode(subreddits)
        trait_avg = sum([s[trait] for s in sentiment["sentiment"]]) / len(sentiment["sentiment"])
        emoji_labels.append(emoji)
        emoji_sizes.append(trait_avg * 1000)
        emoji_trait_avgs.append(trait_avg)
        if subreddit_mode not in subreddit_color_map:
            color = f"C{len(subreddit_color_map)}"
            subreddit_color_map[subreddit_mode] = color
        else:
            color = subreddit_color_map[subreddit_mode]
        subreddit_modes[emoji] = subreddit_mode
        emoji_colors.append(color)
    size = 40
    num_graphs = math.ceil(len(new_data) / size)

    for i in range(num_graphs):
        fig, ax = plt.subplots(figsize=(5, 5))
        start_idx = i * size
        end_idx = min(start_idx + size, len(new_data))
        sub_keys = list(new_data.keys())[start_idx:end_idx]
        sub_data = {k: new_data[k] for k in sub_keys}
        emoji_labels = []
        emoji_sizes = []
        emoji_colors = []
        emoji_trait_avgs = []
        subreddit_modes = {}
        subreddit_color_map = {}
        for emoji, sentiment in sub_data.items():
            subreddits = []
            for s in sentiment["subreddits"]:
                subreddits.append(s)
            subreddit_mode = statistics.mode(subreddits)
            trait_avg = sum([s[trait] for s in sentiment["sentiment"]]) / len(sentiment["sentiment"])
            emoji_labels.append(emoji)
            emoji_sizes.append(trait_avg * 1000)
            emoji_trait_avgs.append(trait_avg)
            if subreddit_mode not in subreddit_color_map:
                color = f"C{len(subreddit_color_map)}"
                subreddit_color_map[subreddit_mode] = color
            else:
                color = subreddit_color_map[subreddit_mode]
            subreddit_modes[emoji] = subreddit_mode
            emoji_colors.append(color)
        scatter = ax.scatter(x=emoji_trait_avgs, y=range(len(emoji_labels)), s=emoji_sizes, c=emoji_colors, alpha=0.7,
                             cmap=subreddit_color_map)
        handles = []
        labels = []
        for subreddit, color in subreddit_color_map.items():
            handles.append(ax.scatter([], [], c=color, alpha=0.7, label=subreddit))
            labels.append(subreddit)
        ax.legend(handles, labels, loc='lower right', title='Subreddits')
        ax.set_yticks(range(len(emoji_labels)))
        ax.set_yticklabels(emoji_labels)
        ax.set_xlabel(f"Average {title} Score, Graph {i + 1}")
        ax.set_ylabel("Emoji")
        plt.show()

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
    sorted_subreddits = sorted(subreddits,
                               key=lambda x: neg_scores[x] + neu_scores[x] + pos_scores[x] + compound_scores[x])
    plt.bar(sorted_subreddits, [neg_scores[subreddit] for subreddit in sorted_subreddits], color='r', label='Negative')
    plt.bar(sorted_subreddits, [neu_scores[subreddit] for subreddit in sorted_subreddits], color='b',
            bottom=[neg_scores[subreddit] for subreddit in sorted_subreddits], label='Neutral')
    plt.bar(sorted_subreddits, [pos_scores[subreddit] for subreddit in sorted_subreddits], color='g', bottom=[
        neg_scores[subreddit] + neu_scores[subreddit] for subreddit in sorted_subreddits], label='Positive')
    plt.bar(sorted_subreddits, [compound_scores[subreddit] for subreddit in sorted_subreddits], color='orange', bottom=[
        neg_scores[subreddit] + neu_scores[subreddit] + pos_scores[subreddit] for subreddit in sorted_subreddits],
        label='Compound')
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
    colors = []
    for i in range(len(sorted_data)):
        colors.append('#%06X' % random.randint(0, 0xFFFFFF))

    plt.bar(sorted_data.keys(), sorted_data.values(), color=colors)
    plt.xticks(rotation=45)
    plt.title('Subreddit Emoji Frequency')
    plt.ylabel('Emoji Count')
    plt.show()
    return


def emoji_number():
    with open('titles_and_emojis.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        count = []
        for key, value in data.items():
            if key not in ['searched_subs', 'searched_posts']:
                count.append(value["frequency"])
        print(count)


def topemoji_sub_table(data):
    subreddits = {}
    for key, data in data.items():
        if key not in ['searched_subs', 'searched_posts']:
            for subreddit in data['subreddits']:
                if subreddit not in subreddits:
                    subreddits[subreddit] = {}
                if key not in subreddits[subreddit]:
                    subreddits[subreddit][key] = 1
                else:
                    subreddits[subreddit][key] += 1

    top_emoji = {}
    rare_emoji = {}

    for key in subreddits:
        min = 10000
        max = 0
        top_emoji[key] = {}
        rare_emoji[key] = {}
        for emoji in subreddits[key]:
            if subreddits[key][emoji] < min:
                min = subreddits[key][emoji]
                rare_emoji[key]["rare_emoji"] = emoji
                rare_emoji[key]["count"] = min

            if subreddits[key][emoji] > max:
                max = subreddits[key][emoji]
                top_emoji[key]["top_emoji"] = emoji
                top_emoji[key]["count"] = max

    df = pd.DataFrame.from_dict(top_emoji, orient='index')
    # add the row index as a column in the dataframe
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'subreddit'}, inplace=True)
    print(df)
    df.to_csv('../graphs/top_emoji_table.csv', index_label='index', index=False)

    df2 = pd.DataFrame.from_dict(rare_emoji, orient='index')
    df2.reset_index(inplace=True)
    df2.rename(columns={'index': 'subreddit'}, inplace=True)
    print(df2)
    df2.to_csv('../graphs/rare_emoji_table.csv', index=False)


def main():
    # query_api()
    visualize()
    # emoji_number()

    return


if __name__ == '__main__':
    main()
