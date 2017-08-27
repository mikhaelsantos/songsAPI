import json
import re

from pymongo import MongoClient

client = MongoClient('mongodb://admin:password@localhost')
db = client['song_list']
songs = db.songs
data = []
with open('./tests/songs.json') as f:
    for line in f:
        data.append(json.loads(line))

songs.insert_many(data)