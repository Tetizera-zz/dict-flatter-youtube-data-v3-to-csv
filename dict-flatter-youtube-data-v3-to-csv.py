'''This code uses the Youtube Data v3 API to fetch ALL videos uploaded by a Youtube channel and creates a CSV with all the metadata available, like thumbnails, when it was uploaded, title, etc.
It might be useful to upload the metadata to Wikidata, by first getting the .csv file and then using openRefine, another free software tool, to upload new data to Wikidata.

Copyright (c) 2021 Tet (https://github.com/Tetizera) and mahousenshi (https://gitlab.com/mahousenshi)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
from apiclient.discovery import build

import csv
import json
import secret

## Variables ##
CHANNEL_ID = 'UCUcyEsEjhPEDf69RRVhRh4A' # The Great War Channel by default. Get the CHANNEL ID by going here and pasting the channel's link: https://commentpicker.com/youtube-channel-id.php
CSV_NAME = 'nome_da_saida' # name of the csv file
##########

### Code from
### https://github.com/sathes/Nested-JSON-or-Dictionary-to-CSV

def is_dict(item, ans=[]):
    tree = []
    for k,v in item.items():
        if isinstance(v,dict):
            ans.append(str(k))
            tree.extend(is_dict(v, ans))
            ans=[]
        else:
            if ans:
                ans.append(str(k))
                key = ','.join(ans).replace(',','.')
                tree.extend([(key, str(v))])
                ans.remove(str(k))
            else:
                tree.extend([(str(k),str(v))])
    return tree

def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except (ValueError,TypeError) as e:
        return False
    return True

def get_tree(item):
    tree = []

    if isinstance(item, dict):
        tree.extend(is_dict(item, ans=[]))
        return tree
    
    elif isinstance(item, list):
        tree = []
        for i in item:
            if is_json(i) == True:
                i = json.loads(i)
            tree.append(get_tree(i))
        return tree
    
    elif isinstance(item, str):
        if is_json(item) == True:
            item = json.loads(item)
            tree.extend(is_dict(item, ans=[]))
            return tree
    
    else:
        tree.extend([(key, item)])
    
    return tree

def render_csv(header, data, out_path=f'{CSV_NAME}.csv'):
    input = []

    with open(out_path, 'w', newline='', encoding="utf-8") as f:
        dict_writer = csv.DictWriter(f, fieldnames=header)
        dict_writer.writeheader()

        if not isinstance(data[0],list):
            input.append(dict(data))
        else:
            for i in data:
                input.append(dict(i))

        dict_writer.writerows(input)
    return
## End Code


youtube = build("youtube", "v3", developerKey=secret.API_KEY)
res = youtube.channels().list(id=CHANNEL_ID, part='contentDetails').execute()

playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']

videos = []
next_page_token = None

while True:
    res = youtube.playlistItems().list(playlistId=playlist_id, part='snippet', maxResults=50, pageToken=next_page_token).execute()
    
    videos += res['items']
    next_page_token = res.get('nextPageToken')
    
    if next_page_token is None:
        break

tree = get_tree(videos)

if isinstance(videos, list):
    header = [i[0] for i in tree[0]]
else:
    header = [i[0] for i in tree]

render_csv(header, tree)
