# Simple Flask API for Songs

## Index

* Description
* Features
* Example calls
* Dependencies
* How to Run
  * Docker (MongoDB + API + Data) -> Fastest way to get up and running
  * Development environment (Tested on macOS)
* How to Test
  * Docker setup
  * Own setup
* FAQ

## Description

Flask API which operates over a Song list and allows users to rate each song from 1 to 5.
The project was developed with a mongodb running on a docker container.

For ease of testing the **Docker (MongoDB + API + Data)** step by step should be pretty much bullet proof and was tested with Docker version 17.06.0-ce.

## Features

* Returns a list of songs with some details on them with optional pagination.
* Returns the average difficulty for all songs or, optionaly, songs of a specific level
* Searches songs based of a string and is case insensitive.
* Adds ratings to song from 1 to 5
* Returns the min, max and avg rating of a given song.

**Routes:**

GET:

* /songs?page=*optional*&page_size=*optional*
* /songs/search?message=*mandatory*
* /songs/avg/difficulty?level=*optional*
* /songs/avg/rating/<song_id>

POST:

* /songs
* /songs/rating?song_id=*mandatory*&rating=*mandatory*

## Example calls

```
curl 'http://<localhost>:<port>/songs?page=10&page_size=1'
```

```
curl 'http://<localhost>:<port>/songs/search?message=finger'
```

```
curl 'http://<localhost>:<port>/songs/avg/difficulty?level=13'
```

```
curl 'http://<localhost>:<port>/songs/avg/rating?song_id=59a2829a32c87b8a8736ba40&rating=3'
```

## Dependencies

* Python 3.6.1
* pymongo
* flask
* Flask-API
* markdown
* Docker
* virtualenv

## How to run

**Note:** Beware of port availability

### Start API

Service can be launched through docker containers or setting up a development enviroment

**Docker (MongoDB + API + Data)**

```
git clone https://github.com/mikhaelsantos/songsAPI.git
cd songsAPI
docker run --name some-mongo -p 27017:27017 -d mongo
docker exec -it some-mongo mongo admin
db.createUser({ user: "admin", pwd: "password", roles: [ { role: "userAdminAnyDatabase", db: "admin" } ] });
<CTRL+C>
docker build -t flask:latest .
docker run -d --rm --name flask-api -p 5000:5000 --link some-mongo:localhost flask:latest
docker exec -it flask-api python3.5 push_data.py
curl http://localhost:5000/songs
```

**Set up development environment (Tested on macOS)**

**Note:**
 * If you are running your own mongodb instance change **MONGODB_URI** in .env to correct value
 * Populate the database

Setup mongodb docker container

**Note:** If your running your own instance you can skip this part.

```
docker run --name some-mongo -p 27017:27017 -d mongo
docker exec -it some-mongo mongo admin
db.createUser({ user: "admin", pwd: "password", roles: [ { role: "userAdminAnyDatabase", db: "admin" } ] });
```
Run the api
```
source .env
flask run
```

## How to Test

Tests can be run with a newly created mongodb docker container or a already available mongodb instance

#### Setup mongodb docker container

**Note:** If your running your own instance you can skip this part.

Setup mongodb

```
docker run --name some-mongo -p 27017:27017 -d mongo
docker exec -it some-mongo mongo admin
db.createUser({ user: "admin", pwd: "password", roles: [ { role: "userAdminAnyDatabase", db: "admin" } ] });
```
Run python command

```
source .env
python3 -m unittest -v tests.test_songs_api
```

#### Already have a mongoDB instance up and running

Change mongodb URI at ./instance/config **Class TestingConfig**

```
MONGODB_URI = 'mongodb://<username>:<password>@<host>'
```

Run python command

```
source .env
python3 -m unittest -v tests.test_songs_api
```

## FAQ

**Shouldn't you have a class for songs and rating models and why?**

For production grade code I would have, here it was just because of the time restraint.
The advantage of having specific models is for business logic and  data sensitization but the disadvantage is that changing the schema involves more work.

**Think what will happen when the collection of songs grow to millions of documents.**

If the collection grows to millions of documents the utilization of indexes will be the minimum requirement which would be based on the most frequent queried fields.
Also sharding the song collection to multiple shard servers based on a key would also reduce query times.

**Wouldn't a frontend be nice?**

Yes, but it seems out of the scope of this homework.

## Maintainers
1. Mikhael Santos

