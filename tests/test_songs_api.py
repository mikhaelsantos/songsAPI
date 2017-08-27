import json
import unittest
from functools import reduce
from http import HTTPStatus

from pymongo import MongoClient

from app import create_app

# CONSTANTS FOR VARS
PAGE_SIZE = 3
PAGE = 2
LEVEL = 13
INVALID_LEVEL = "Im()"
SEARCH_MESSAGE = "finger"
INCORRECT_SEARCH_MESSAGE = "öä()89¶\{"
RATINGS = [1, 3, 5]

# CONSTANTS FOR FILED MAPPING
TITLE_FIELD = "title"
DIFFICULTY_FIELD = "difficulty"
LEVEL_FIELD = "level"
SONG_ID_FIELD = "song_id"
ID_FIELD = "_id"
RATING_FIELD = "rating"
MIN_FIELD = "min"
MAX_FIELD = "max"
AVG_FIELD = "avg"


class SongsApiTestCase(unittest.TestCase):
    """
    This class represents the songs api test case
    """

    def setUp(self):
        """
        Define test variables and initialize app.
        """
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.song_list = []
        self.clean_song_list = []
        with open('songs.json') as f:
            for line in f:
                self.song_list.append(json.loads(line))
                self.clean_song_list.append(json.loads(line))
        db_client = MongoClient(self.app.config.get("MONGODB_URI"))
        db = db_client['song_list']
        self.col_songs = db.songs
        self.col_ratings = db.ratings
        self.col_songs.insert_many(self.song_list)

    def test_songs_post_single(self):
        """
        Test API can create a single song (POST request)
        """
        self.col_songs.delete_many({})
        res = self.client().post('/songs', data=json.dumps([self.clean_song_list[0]]), content_type='application/json')
        self.assertEqual(res.status_code, HTTPStatus.CREATED)

    def test_songs_post_batch(self):
        """
        Test API can create multiple songs (POST request)
        """
        self.col_songs.delete_many({})
        res = self.client().post('/songs', data=json.dumps(self.clean_song_list), content_type='application/json')
        self.assertEqual(res.status_code, HTTPStatus.CREATED)

    def test_songs_get_batch(self):
        """
        Test API can get a batch of songs (GET request)
        """

        result = self.client().get('/songs')
        self.assertEqual(result.status_code, HTTPStatus.OK)
        self.assertEqual(len(json.loads(result.data)), len(self.song_list))

    def test_songs_get_batch_with_pagination(self):
        """
        Test API can get a batch of songs by page (GET request)
        """

        result = self.client().get('/songs?page=' + str(PAGE) + '&page_size=' + str(PAGE_SIZE))
        self.assertEqual(result.status_code, HTTPStatus.OK)
        data = json.loads(result.data)
        self.assertEqual(len(data), PAGE_SIZE)
        self.assertEqual(data[0][TITLE_FIELD], self.song_list[3][TITLE_FIELD])
        self.assertEqual(data[1][TITLE_FIELD], self.song_list[4][TITLE_FIELD])
        self.assertEqual(data[2][TITLE_FIELD], self.song_list[5][TITLE_FIELD])

    def test_songs_get_by_search(self):
        """
        Test API can get a batch of songs (GET request)
        """
        result = self.client().get('/songs/search?message=' + SEARCH_MESSAGE)
        self.assertEqual(len(json.loads(result.data)), 2)

    def test_songs_get_by_search_invalid_parenthesis(self):
        """
        Test API can get a batch of songs (GET request)
        """

        result = self.client().get('/songs/search?message="{}"'.format(INCORRECT_SEARCH_MESSAGE))
        self.assertEqual(result.status_code, HTTPStatus.BAD_REQUEST)

    def test_songs_get_average_no_option(self):
        """
        Test API can get a average of songs difficulty with no level (GET request)
        """
        result = self.client().get('/songs/avg/difficulty')
        self.assertEqual(result.status_code, HTTPStatus.OK)
        data = json.loads(result.data)
        average = 0
        for song in self.song_list:
            average += song[DIFFICULTY_FIELD]
        average = average / len(self.song_list)
        self.assertEqual(data["average_difficulty"], average)

    def test_songs_get_average_with_level(self):
        """
        Test API can get a average of songs difficulty with level option (GET request)
        """

        result = self.client().get('/songs/avg/difficulty?level=' + str(LEVEL))
        self.assertEqual(result.status_code, HTTPStatus.OK)

        data = json.loads(result.data)
        average = 0
        song_level = [song for song in self.song_list if song[LEVEL_FIELD] == LEVEL]
        for song in song_level:
            average += song[DIFFICULTY_FIELD]
        average = average / len(song_level)
        self.assertEqual(data["average_difficulty"], average)

    def test_songs_get_average_with_level_non_decimal(self):
        """
        Test API can get a average of songs difficulty with level option (GET request)
        """

        result = self.client().get('/songs/avg/difficulty?level=' + str(INVALID_LEVEL))
        self.assertEqual(result.status_code, HTTPStatus.BAD_REQUEST)

    def test_songs_post_rating(self):
        """
        Test API can post a rating of a songs (POST request)
        """

        rating = 5
        id = str(self.song_list[0][ID_FIELD])
        result = self.client().post('/songs/rating?song_id=' + id + '&rating=' + str(rating), data={},
                                    content_type='application/json')
        self.assertEqual(result.status_code, HTTPStatus.CREATED)
        data = list(self.col_ratings.find({SONG_ID_FIELD: id}))
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0][RATING_FIELD], rating)

        # Insert 2 ratings for the same song

        result = self.client().post('/songs/rating?song_id=' + id + '&rating=' + str(rating), data={},
                                    content_type='application/json')
        self.assertEqual(result.status_code, HTTPStatus.CREATED)
        data = list(self.col_ratings.find({SONG_ID_FIELD: id}))
        self.assertEqual(len(data), 2)

    def test_songs_post_invalid_non_numeric_rating(self):
        """
        Test API can post a rating of a songs (POST request)
        """

        rating = "asdjh"
        id = str(self.song_list[0][ID_FIELD])
        result = self.client().post('/songs/rating?song_id=' + id + '&rating=' + str(rating), data={},
                                    content_type='application/json')
        self.assertEqual(result.status_code, HTTPStatus.BAD_REQUEST)

    def test_songs_post_invalid_out_of_bound_numeric_rating(self):
        """
        Test API can post a rating of a songs (POST request)
        """

        rating = 6
        id = str(self.song_list[0][ID_FIELD])
        result = self.client().post('/songs/rating?song_id=' + id + '&rating=' + str(rating), data={},
                                    content_type='application/json')
        self.assertEqual(result.status_code, HTTPStatus.BAD_REQUEST)

    def test_songs_post_invalid_non_song_id_rating(self):
        """
        Test API can post a rating of a songs (POST request)
        """

        rating = 6
        id = str(self.song_list[0][ID_FIELD])
        result = self.client().post('/songs/rating?rating=' + str(rating), data={}, content_type='application/json')
        self.assertEqual(result.status_code, HTTPStatus.BAD_REQUEST)

    def test_songs_get_low_high_avg(self):
        """
        Test API can get low high and average rating of a song (GET request)
        """
        id = str(self.song_list[0][ID_FIELD])
        for rating in RATINGS:
            post = {
                SONG_ID_FIELD: str(self.song_list[0][ID_FIELD]),
                RATING_FIELD: rating
            }
            self.col_ratings.insert_one(post)

        result = self.client().get('/songs/avg/rating/' + id)
        self.assertEqual(result.status_code, HTTPStatus.OK)
        data = json.loads(result.data)
        self.assertEqual(data[MIN_FIELD], min(RATINGS))
        self.assertEqual(data[MAX_FIELD], max(RATINGS))
        self.assertEqual(data[AVG_FIELD], reduce(lambda x, y: x + y, RATINGS) / len(RATINGS))

    def tearDown(self):
        """
        teardown all initialized variables.
        """
        with self.app.app_context():
            self.col_songs.delete_many({})
            self.col_ratings.delete_many({})


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
