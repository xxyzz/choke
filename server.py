import telegram, logging, json, requests, os, re, time
from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4
from pytz import timezone, utc
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

runLocally = os.environ.get('runLocally')
telegramToken = os.environ.get('telegramToken')
aqiToken = os.environ.get('aqiToken')
aqiURL = 'https://api.waqi.info/'
openstreetmapURL = 'https://nominatim.openstreetmap.org/search?format=json&q='
bot = telegram.Bot(telegramToken)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

scheduler = BackgroundScheduler()
scheduler.configure(timezone = utc)

def start(bot, update):
    text = "Check AQI: /aqi eiffel tower\nSet daily notification: /daily eiffel tower 13:01\nDisable daily notification: /disable\nAqi data form aqicn.org"
    bot.send_message(chat_id=update.message.chat_id, text=text)

start_handler = CommandHandler('start', start)

def getLocation(address):
    """Using openStreetMap API get latitude and longitude"""
    resp = requests.get(url = openstreetmapURL + ' '.join(address))
    if resp.json() == []:
        return False
    else:
        return resp.json()[0]

def getAqiByCity(bot, update, args):
    if args == []:
        update.message.reply_text('Please add a address after the command\nE.g. /aqi eiffel tower')
        return
    location = getLocation(args)
    if not location:
        update.message.reply_text('Please enter a valide address')
    else:
        getAqiByLocation(location['lat'], location['lon'], update)

aqiCity_handler = CommandHandler('aqi', getAqiByCity, pass_args=True)

def getAqiByLocation(lat, lng, update):
    param = {'token': aqiToken}
    resp = requests.get(url = aqiURL + 'feed/geo:' + lat + ';' + lng + '/', params=param)
    data = resp.json()['data']
    level = getLevel(data['aqi'])
    time = getUpdateTime(data['time']['s'])
    update.message.reply_text(data['city']['name'] + '\naqi: ' + str(data['aqi']) + level + time)

def inline_search(bot, update):
    query = update.inline_query.query
    if not query:
        return
    param = {'token': aqiToken, 'keyword': query}
    resp = requests.get(url = aqiURL + 'search/', params=param)
    results = list()
    for station in resp.json()['data']:
        level = getLevel(station['aqi'])
        time = getUpdateTime(station['time']['stime'])
        results.append(
            InlineQueryResultArticle(
                id=uuid4(),
                title=station['station']['name'],
                input_message_content=InputTextMessageContent(station['station']['name'] + '\naqi: ' + station['aqi'] + level + time)
            )
        )
    update.inline_query.answer(results)

inline_search_handler = InlineQueryHandler(inline_search)

def getLevel(aqi):
    if aqi == "" or aqi == "-":
        return '\nNo aqi data\n'
    elif int(aqi) <= 50: 
        return ' 😀\nGood\n'
    elif int(aqi) <= 100:
        return ' 🙂\nModerate\n'
    elif int(aqi) <= 150:
        return ' 😐\nUnhealthy for Sensitive Groups\n'
    elif int(aqi) <= 200:
        return ' 😷\nUnhealthy\n'
    elif int(aqi) <= 300:
        return ' 🤢\nVery Unhealthy\n'
    elif int(aqi) > 300:
        return ' 😵\nHazardous\n'

def getUpdateTime(time):
    if time == "":
        return 'No update time data'
    else:
        return 'Updated on ' + time[11:16]

def dailyNotification(bot, update, args):
    # check input formate
    # if len(args) <= 1 or not re.match('\\d{2}:\\d{2}$', args[-1]):
    #     update.message.reply_text('Please use the right formate\nE.g. /daily eiffel tower 13:01')
    #     return
    # location = getLocation(args[:-1])
    # get timezone info
    # param = {'location': str(location['lat']) + ',' + str(location['lng']), 'timestamp': str(time.time()),'key': GmapTimezoneToken}
    # resp = requests.get(url = GmapTimezoneUrl, params = param)
    # timeZone = resp.json()['timeZoneId']
    # set notification time. I hate timezone.
    # notificationTime = timezone(timeZone).localize(datetime.strptime(datetime.now().strftime('%Y%m%d') + args[-1], '%Y%m%d%H:%M')).astimezone(utc)
    # scheduler.add_job(getAqiByLocation, 'cron', [str(location['lat']), str(location['lng']), update], hour = notificationTime.hour, minute = notificationTime.minute)
    update.message.reply_text('Not work yet.')

daily_handler = CommandHandler('daily', dailyNotification, pass_args=True)

def disableDaily(bot, update):
    # if scheduler.get_jobs() == []:
    #     update.message.reply_text('No daily notification to disable')
    # else:
    #     scheduler.remove_all_jobs()
    #     update.message.reply_text('Success!')
    update.message.reply_text('Not work yet.')

disableDaily_handler = CommandHandler('disable', disableDaily)

def help(bot, update):
    text = "Usage example: /start\n[Report bug](https://github.com/xxyzz/choke/issues)"
    bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)

help_handler = CommandHandler('help', help)

def main():
    updater = Updater(telegramToken)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(aqiCity_handler)
    dispatcher.add_handler(inline_search_handler)
    dispatcher.add_handler(daily_handler)
    dispatcher.add_handler(disableDaily_handler)
    dispatcher.add_handler(help_handler)

    scheduler.start()

    if runLocally:
        updater.start_polling()
    else:
        updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get('PORT', '8443')), url_path=telegramToken)
        updater.bot.set_webhook('https://' + os.environ.get('herokuURL') + '.herokuapp.com/' + telegramToken)

    updater.idle()

main()