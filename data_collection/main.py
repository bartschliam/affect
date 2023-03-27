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
    num_posts = 100
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
            titles_and_emojis['searched_subs'][subreddit] = 0
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
                            titles_and_emojis['searched_subs'][subreddit] += 1
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

    fig, ax = plt.subplots()

    # Add a Unicode emoji using the Text method
    ax.text(0.5, 0.5, '\U0001F600', fontsize=50, ha='center')

    # Customize the plot
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()

    # Show the plot
    plt.show()
    return


def main():
    # query_api()
    visualize()
    return


if __name__ == '__main__':
    main()
