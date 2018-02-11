import telegram, logging, json, requests, datetime, os
from telegram.ext import Updater, CommandHandler, InlineQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent
from uuid import uuid4

token = os.environ.get('token')
aqiToken = os.environ.get('aqiToken')
GmapToken = os.environ.get('GmapToken')
aqiUrl = 'https://api.waqi.info/'
GmapUrl = 'https://maps.googleapis.com/maps/api/geocode/json?address='
bot = telegram.Bot(token)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(bot, update):
    text = "Check AQI: /aqi beijing\nSet daily notification: /daily beijing 13:01\nDisable daily notification: /disable\nAqi data form aqicn.org"
    bot.send_message(chat_id=update.message.chat_id, text=text)

start_handler = CommandHandler('start', start)

def getAqiByCity(bot, update, args):
    # get latitude and longitude
    param = {'key': GmapToken}
    resp = requests.get(url = GmapUrl + ' '.join(args), params = param)
    if resp.json()['results'] == []:
        update.message.reply_text('Wanna get high?')
    else:
        location = resp.json()['results'][0]['geometry']['location']
        getAqiByLocation(str(location['lat']), str(location['lng']), update)

aqiCity_handler = CommandHandler('aqi', getAqiByCity, pass_args=True)

def getAqiByLocation(lat, lng, update):
    param = {'token': aqiToken}
    resp = requests.get(url = aqiUrl + 'feed/geo:' + lat + ';' + lng + '/', params=param)
    data = resp.json()['data']
    level = getLevel(data['aqi'])
    time = getUpdateTime(data['time']['s'])
    update.message.reply_text(data['city']['name'] + '\naqi: ' + str(data['aqi']) + level + time)

def inline_search(bot, update):
    query = update.inline_query.query
    if not query:
        return
    param = {'token': aqiToken, 'keyword': query}
    resp = requests.get(url = aqiUrl + 'search/', params=param)
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

def dailyCallback(bot, job):
    param = {'key': GmapToken}
    resp = requests.get(url = GmapUrl + ' '.join(job.context[0]), params = param)
    if resp.json()['results'] == []:
        bot.send_message(chat_id=job.context[1], text = 'Wanna get high?')
    else:
        location = resp.json()['results'][0]['geometry']['location']
        param = {'token': aqiToken}
        resp = requests.get(url = aqiUrl + 'feed/geo:' + str(location['lat']) + ';' + str(location['lng']) + '/', params=param)
        data = resp.json()['data']
        level = getLevel(data['aqi'])
        time = getUpdateTime(data['time']['s'])
        bot.send_message(chat_id=job.context[1], text= data['city']['name'] + '\naqi: ' + str(data['aqi']) + level + time)

def dailyNotification(bot, update, args, job_queue):
    context = []
    context.append(args[:-1])
    context.append(update.message.chat_id)
    global job_daily
    job_daily = job_queue.run_daily(dailyCallback, datetime.datetime.strptime(args[-1], '%H:%M').time(), context=context)
    update.message.reply_text('Success!')

daily_handler = CommandHandler('daily', dailyNotification, pass_args=True, pass_job_queue=True)

def disableDaily(bot, update):
    if 'job_daily' in globals():
        job_daily.schedule_removal()
        update.message.reply_text('Success!')
    else:
        update.message.reply_text('No daily notification to disable')

disableDaily_handler = CommandHandler('disable', disableDaily)

def help(bot, update):
    text = "Usage example: /start\nReport bug: [issue](https://github.com/xxyzz)"
    bot.send_message(chat_id=update.message.chat_id, text=text, parse_mode=telegram.ParseMode.MARKDOWN)

help_handler = CommandHandler('help', help)

def main():
    updater = Updater(token)
    dispatcher = updater.dispatcher
    job = updater.job_queue

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(aqiCity_handler)
    dispatcher.add_handler(inline_search_handler)
    dispatcher.add_handler(daily_handler)
    dispatcher.add_handler(disableDaily_handler)
    dispatcher.add_handler(help_handler)

    updater.start_polling()
    updater.idle()

main()