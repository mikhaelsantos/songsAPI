import datetime
import re

from http import HTTPStatus

from flask import request, jsonify
from flask_api import FlaskAPI
from pymongo import MongoClient

# local import
from instance.config import app_config

client = MongoClient('mongodb://admin:password@localhost')
db = client['song_list']
col_songs = db.songs
col_ratings = db.ratings


def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    @app.route('/songs', methods=['POST', 'GET'])
    def songs():
        """
        GET:
        - Returns a list of songs with some details on them
        - Possibility to paginate songs with:
            - page: (int) Page number
            - page_size: (int) Number of results per page
        POST: Adds an array of songs
        :return: GET: (APIResponse) api response to the request with list containing songs
                 POST: (APIResponse) api response with success of 201
        """
        if request.method == "POST":
            songlist = request.get_json(force=True)
            mongo_response = col_songs.insert_many(songlist)
            if mongo_response.acknowledged is True:
                response = jsonify({})
                response.status_code = HTTPStatus.CREATED
            return response
        else:
            # GET
            page = request.args.get('page')
            page_size = request.args.get('page_size')
            if page_size is None or (page_size is not None and int(page_size) >= 11):
                limit = 11
            else:
                limit = int(page_size)
            if page is None or (page is not None and int(page) <= 1):
                skip = 0
            else:
                skip = int(page_size) * (int(page) - 1)
            results = list(col_songs.find({}, {"_id": 0}).skip(skip).limit(limit))
            response = jsonify(results)
            return response

    @app.route('/songs/<operation>')
    def search(operation):
        """
        GET:
        - Takes in parameter a 'message' string to search.
        - Search takes into account song's artist, title and is case insensitive.
        :return: (APIResponse) api response to the request with a list of songs.
        """
        if operation == 'search':
            message = str(request.args.get('message'))
            if message is not None and re.match("^[a-zA-Z0-9_]*$", message):
                results = list(col_songs.find({"$or": [{'artist': re.compile(message, re.IGNORECASE)},
                                                       {'title': re.compile(message, re.IGNORECASE)}]}, {"_id": 0}))
                response = jsonify(results)
                return response
            else:
                response = jsonify({})
                response.status_code = HTTPStatus.BAD_REQUEST
                return response

    @app.route('/songs/avg/difficulty')
    def avg():
        """
        GET:
        - Returns the average difficulty for songs.
        - Takes an optional parameter "level" to select only songs from a specific level.
        :return: (APIResponse) api response to the request with a dict containing average difficulty.
        """
        level = request.args.get('level')
        if level is not None and level.isnumeric():
            match = {"level": int(level)}
        elif level is not None:
            response = jsonify({})
            response.status_code = HTTPStatus.BAD_REQUEST
            return response
        else:
            match = {}
        results = col_songs.aggregate([
            {
                "$match": match
            },
            {
                "$group": {
                    "_id": 0,
                    "average_difficulty": {"$avg": "$difficulty"}
                }
            }
        ])
        response = jsonify(list(results)[0])
        return response

    @app.route('/songs/rating', methods=['POST'])
    def rating():
        """
        POST:
        - Takes in parameter a (str) "song_id" and a (int) "rating" from 1 to 5
        - Adds a rating to the song.
        :return: POST: (APIResponse) api response with success of 201
        """
        if request.method == "POST":
            valid_rating = set([1, 2, 3, 4, 5])

            try:
                rating = int(request.args.get('rating'))
                song_id = str(request.args.get('song_id'))
                if rating not in valid_rating:
                    raise ValueError
            except ValueError:
                response = jsonify({})
                response.status_code = HTTPStatus.BAD_REQUEST
                return response

            post = {
                "song_id": song_id,
                "rating": rating,
                "timestamp": datetime.datetime.utcnow()
            }
            mongo_response = col_ratings.insert_one(post)
            if mongo_response.acknowledged is True:
                response = jsonify({})
                response.status_code = HTTPStatus.CREATED
            return response

    @app.route('/songs/avg/rating/<song_id>')
    def max_min_avg_rating(song_id):
        """
        GET:
        - Returns the average, the lowest and the highest rating of the given song_id.
        :return: (APIResponse) api response to the request with a dict containing min, max and average rating
        """
        match = {"song_id": str(song_id)}

        results = col_ratings.aggregate([
            {
                "$match": match
            },
            {
                "$group": {
                    "_id": 0,
                    "min": {"$min": "$rating"},
                    "max": {"$max": "$rating"},
                    "avg": {"$avg": "$rating"}
                }
            }
        ])
        response = jsonify(list(results)[0])
        return response

    return app
