import praw
import re
from dotenv import load_dotenv
import os
import emoji
import time
import json

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
        'gaming',
        'funny',
        'aww',
        'bunnies', 
        'lgbt',
        'socialskills',
        'movies', 
        'facepalm',
    ]
    num_posts = 100
    found = False
    last_request_time = time.time()
    titles_and_emojis = []
    for subreddit in subreddits:
        print(f'Subreddit: {subreddit}')
        for i, post in enumerate(reddit.subreddit(subreddit).new(limit=num_posts)):
            print(f"Index: {i}, Post: {post.title}")
            if last_request_time is not None and time.time() - last_request_time < 1:
                time_to_wait = 1 - (time.time() - last_request_time)
                #print(f"Waiting for {time_to_wait:.1f} seconds before next request...")
                time.sleep(time_to_wait)
            title = post.title
            emojis = [c for c in title if c in emoji.EMOJI_DATA]
            if emojis:
                #titles_and_emojis.append((title, emojis))
                if emoji in titles_and_emojis:
                    titles_and_emojis[emojis]['frequency'] += 1
                else:
                    titles_and_emojis[emojis] = {}
                    titles_and_emojis[emojis]['frequency'] = 1
                titles_and_emojis[emojis]['subreddits'].add(subreddit)
                found = True
            last_request_time = time.time()
            if found:
                break
        if found:
            break
    with open('titles_and_emojis.json', 'w') as f:
        json.dump(titles_and_emojis, f)
    return

def format_json():
    with open('titles_and_emojis.json', 'r') as f:
        data = json.load(f)
    formatted_data = {}
    for item in data:
        formatted_data[item[0]] = item[1]

    print(formatted_data)
    return

def main():
    #query_api()
    format_json()
    return

if __name__ == '__main__':
    main()

