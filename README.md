# Choke

Choke is a telegram bot([@getAqiBot](https://t.me/getAqiBot)) that can check AQI and send daily notification. Choke uses [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

## Requirments

* Python 3
* [pipenv](https://pipenv.readthedocs.io)
* [Telegram bot token](https://core.telegram.org/bots#3-how-do-i-create-a-bot)
* [aqicn API key](https://aqicn.org/data-platform/token/)
* [Heroku account(optional)](https://www.heroku.com)

## Usefull Docs

- [Getting Started on Heroku with Python](https://devcenter.heroku.com/articles/getting-started-with-python)

- [Air Quality Programmatic APIs](https://aqicn.org/json-api/doc/)

- [Nominatim](https://wiki.openstreetmap.org/wiki/Nominatim)

## Installation

Create your .env file first.

```
runLocally = true
telegramToken = 'your telegram bot token'
aqiToken = 'your aqicn API key'
herokuURL = 'your Heroku app's name like lit-bastion-5032'
```

Then run locally:

```
$ pipenv --three
$ pipenv run pip install pip==18.0
$ pipenv install
$ pipenv shell
// test locally
$ heroku local
// deploy changes
$ git push heroku master
```