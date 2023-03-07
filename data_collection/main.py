import praw
import re
from dotenv import load_dotenv
import os
import emoji
import time
import json
from pprint import pprint


def query_api():
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
    subreddits = [
        'cloudwater',
        'gaming',
        'funny',
        'aww',
        'bunnies',
        'lgbt',
        # 'socialskills',
        # 'movies',
        'facepalm',
    ]
    num_posts = 100
    found = False
    last_request_time = time.time()
    try:
        with open('titles_and_emojis.json', 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = {}
    titles_and_emojis = data
    if 'searched_subs' not in titles_and_emojis:
        titles_and_emojis['searched_subs'] = {
            'list': [],
            'count': 0
        }
    if 'searched_posts' not in titles_and_emojis:
        titles_and_emojis['searched_posts'] = {
            'count': 0,
            'found': 0
        }
    for subreddit in subreddits:
        print(f'Subreddit: {subreddit}')
        titles_and_emojis['searched_subs']['list'].append(subreddit)
        titles_and_emojis['searched_subs']['count'] += 1
        for post_index, post in enumerate(reddit.subreddit(subreddit).new(limit=num_posts)):
            print(f"Number: {post_index}, Post: {post.title}")
            titles_and_emojis['searched_posts']['count'] += 1
            if last_request_time is not None and time.time() - last_request_time < 1:
                time_to_wait = 1 - (time.time() - last_request_time)
                time.sleep(time_to_wait)
            title = post.title
            emojis = [c for c in title if c in emoji.EMOJI_DATA]
            if emojis:
                titles_and_emojis['searched_posts']['found'] += 1
                for item in emojis:
                    emoji_hex = item
                    if emoji_hex in titles_and_emojis:
                        titles_and_emojis[emoji_hex]['frequency'] += 1
                        titles_and_emojis[emoji_hex]['subreddits'].append(subreddit)
                    else:
                        titles_and_emojis[emoji_hex] = {}
                        titles_and_emojis[emoji_hex]['frequency'] = 1
                        titles_and_emojis[emoji_hex]['subreddits'] = [subreddit]
                # found = True
            last_request_time = time.time()
            if found:
                break
        if found:
            break
    with open('titles_and_emojis.json', 'w') as f:
        json.dump(titles_and_emojis, f)
    return


def format_json():
    try:
        with open('titles_and_emojis.json', 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        data = {}
    pprint(data)
    return


def main():
    query_api()
    format_json()
    return


if __name__ == '__main__':
    main()
