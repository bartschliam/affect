import json
import pandas as pd
import requests
import requests.auth

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



def get_subreddit_flairs(subreddit):
    flairs_list = []
    # set the API endpoint
    url = f"https://oauth.reddit.com/r/{subreddit}/api/link_flair.json"
    # set custom user agent for the request (recommended)
    headers = {'User-Agent': 'MyBot/0.0.1'}
    # set your Reddit app client ID and client secret
    client_id = "MXJ1QjAMttFlr1kG28r9Pg"
    client_secret = "9RGxuefg5rnP79oZYGtO84wAYrMOPg"
    # set your Reddit account username and password
    username = "Guesstrinityboy9356"
    password = "!Bengaluru123"
    # authenticate using the OAuth2 authentication flow
    client_auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    post_data = {"grant_type": "password", "username": username, "password": password}
    headers = {"User-Agent": "MyBot/0.0.1"}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data,
                             headers=headers)
    access_token = response.json()["access_token"]
    headers["Authorization"] = f"bearer {access_token}"
    # send GET request to the API endpoint
    response = requests.get(url, headers=headers)
    # check if the request was successful
    if response.status_code == 200:
        # extract the JSON data from the response
        json_data = json.loads(response.text)

        for item in json_data:
            flairs_list.append(item['text'])
    return flairs_list

json_file = open("titles_and_emojis.json", "r")
file_data = json.load(json_file)
json_file.close()

for i in subreddits:
    file_data["searched_subs"][i]["topics"] = f_list = get_subreddit_flairs(i)
    print(file_data["searched_subs"][i])

jsonFile = open("titles_and_emojis.json", "w+")
jsonFile.write(json.dumps(file_data))
jsonFile.close()
