# Simple Flask API for Songs

* Description
* Dependencies
* How to Run
* How to test
* FAQ

## Description

Flask API which operates over a Song list and allows users to rate each song from 1 to 5.

**Routes:**

GET:

* /songs?page=*optional*&page_size=*optional*
* /songs/search?message=*mandatory*
* /songs/avg/difficulty?level=*optional*
* /songs/avg/rating/<song_id>

POST:

* /songs
* /songs/rating?song_id=*mandatory*&rating=*mandatory*

## Dependencies

* Python 3.6.1
* pymongo
* flask
* Flask-API
* markdown
* Docker
* virtualenv

## How to run

One common step to both testing and and running the app is setting up the mongodb instance and credentials:

#### Set up a new Docker Container (No mongodb instance running)

Note: If your running your own instance you can skip this part.

1. Setup docker container

```
docker run --name some-mongo -p 27017:27017 -d mongo
```

NOTE: Beware of port availability

2. Enter container

```
docker exec -it some-mongo mongo admin
```

3. Run command to create user

```
db.createUser({ user: "admin", pwd: "password", roles: [ { role: "userAdminAnyDatabase", db: "admin" } ] });
```

### Start API

1. Set up development environment (Tested on macOS)

Note: If you are running your own mongodb instance change **MONGODB_URI** in .env to correct value

```
source .env
```


2. Run it

```
flask run
```

## How to Test

#### If you followed the steps in **Set up a new Docker Container (No mongodb instance running)**

1. Run python command

```
python3 -m unittest -v tests.test_songs_api
```

#### Already have a mongoDB instance up and running

1. Change mongodb URI at ./instance/config **Class TestingConfig**

```
MONGODB_URI = 'mongodb://<username>:<password>@<host>'
```

2. Run python command

```
python3 -m unittest -v tests.test_songs_api
```

## FAQ

**Shouldn't you have a class for songs and rating models and why?**

For production grade code I would have, here it was just because of the time restraint.
The advantage of having specific models is for business logic and sensitization of the data the disadvantage is that then changing the schema involves more work


## Maintainers
1. Mikhael Santos

