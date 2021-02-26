# Twitter Scraper

A proof of concept project with clean(ish)-architecture implementation and Django. It uses Twitter API v1.1 as a backend.

## Installation
You can start the app using docker.

## Configuration
Settings are parsed from environment variables in compliance with 12-factor app rules. Run the app with an .env file. All required settings are given in .env.example file so you can create your own by copying and modifying it.

Twitter API v1.1 backend works with Oauth 1.0. You should change the below settings in your .env file with your own credentials;

```
SEARCH_TWEETS_API_V1_1_CONSUMER_KEY=your-consumer-key
SEARCH_TWEETS_API_V1_1_CONSUMER_SECRET=your-consumer-secret
SEARCH_TWEETS_API_V1_1_ACCESS_TOKEN=your-access-token
SEARCH_TWEETS_API_V1_1_ACCESS_TOKEN_SECRET=your-access-token-secret
```

## Usage
You need the create your ***.env*** file in the same directory with ***docker-compose.yml*** file. After that;
```shell
$docker-compose up

```
Run tests:
```shell
$docker-compose run web python manage.py test
```

## API Docs

You can access the docs by:

`
http://0.0.0.0:8000/docs
`

## Healthcheck

To check health:

`
http://0.0.0.0:8000/health
`
