# Choke

Choke is a telegram bot([@getAqiBot](https://t.me/getAqiBot)) that can check AQI and send daily notification. Choke uses [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot).

## Requirments

* Python 3
* pipenv
* Telegram bot token
* [aqicn API key](https://aqicn.org/data-platform/token/)
* [Google Maps Geocoding API](https://developers.google.com/maps/documentation/geocoding/start)
* [Google Maps Time Zone API](https://developers.google.com/maps/documentation/timezone/start)
* Heroku account(optional)

## Installation

Create your .env file first

```
token = 'your telegram bot token'
aqiToken = 'your aqicn API key'
GmapToken = 'your Google Maps Geocoding API key'
GmapTimezoneToken = 'your Google Maps Time Zone API key'
herokuUrl = 'your Heroku app's name like lit-bastion-5032'
```

Then run locally

```
pipenv --three
pipenv install
pipenv shell
heroku local
```