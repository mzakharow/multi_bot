import telebot
import requests, bs4
from telebot.types import Message
from Task import Task

TOKEN = ''

bot = telebot.TeleBot(TOKEN)
task = Task()


@bot.message_handler(commands=['weather'])
def command_handler(message: Message):
    task.is_weather = True
    task.is_tracking = False
    bot.send_message(message.chat.id, 'Введите название города.')


@bot.message_handler(commands=['tracking'])
def command_handler(message: Message):
    task.is_tracking = True
    task.is_weather = False
    bot.send_message(message.chat.id, 'Введите номер почтового отправления.')


@bot.message_handler(commands=['help'])
def command_handler(message: Message):
    bot.reply_to(message, 'Для начала работы с ботом выберите одну из следующих комманд: \n'
                          ' - для получения прогноза погоды /weather \n'
                          ' - для поиска почтового отправления /tracking'
                 )


@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types='text')
def return_message(message: Message):
    if task.is_weather:
        try:
            city = message.text.replace(' ', '-')
            source = requests.get(f'https://sinoptik.com.ru/погода-{city}')
            bs = bs4.BeautifulSoup(source.text, "html.parser")
            p1 = bs.select('.temperature .p1')
            night_from = p1[0].getText()
            p2 = bs.select('.temperature .p2')
            night_to = p2[0].getText()
            p5 = bs.select('.temperature .p5')
            day_from = p5[0].getText()
            p6 = bs.select('.temperature .p6')
            day_to = p6[0].getText()

            weather_list = ['Ночь :' + night_from + ' ' + night_to, 'День :' + day_from + ' ' + day_to]

            info_day_light = bs.select('.infoDaylight')
            sunrise_sunset = info_day_light[0].getText()
            weather_list.append(sunrise_sunset.strip())

            forecast = bs.select('.rSide .description')
            weather = forecast[0].getText()
            weather_list.append(weather.strip())

            bot.send_message(message.chat.id, '\n'.join(weather_list))
        except Exception:
            bot.send_message(message.chat.id, 'Для выбранного города прогноз не составлялся.')
    elif task.is_tracking:
        try:
            api_key = ''
            track = message.text.upper()
            domain = 'demo.track24.ru'
            request = requests.get(f'https://api.track24.ru/tracking.json.php?apiKey={api_key}&domain={domain}&pretty=true&code={track}')
            data = request.json()
            event = data["data"]["events"][0]

            service_name = event.get('serviceName')
            # print(service_name)
            if service_name == 'Track24':
                bot.send_message(message.chat.id, 'Проблема в получении данных об отправлении, попробуйте позже.')
                return

            event_list = ['Дата: ' + event.get('operationDateTime'),
                          'Событие: ' + event.get('operationAttribute'),
                          'Место: ' + event.get('operationPlaceNameOriginal'),
                          'Почтовая служба: ' + service_name
                          ]

            bot.send_message(message.chat.id, '\n'.join(event_list))
        except Exception:
            bot.send_message(message.chat.id, 'Почтовое отправление не найдено.')
    else:
        bot.send_message(message.chat.id, 'Для работы с ботом выберите комманду: /weather или /tracking')


bot.polling(timeout=60)
