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
    bot.send_message(message.chat.id, 'Прогноз погоды в каком городе будем смотреть?')


@bot.message_handler(commands=['tracking'])
def command_handler(message: Message):
    print(message)
    bot.reply_to(message, 'There is no answer')


@bot.message_handler(commands=['licence_plate'])
def command_handler(message: Message):
    print(message)
    bot.reply_to(message, 'There is no answer')


@bot.message_handler(commands=['help'])
def command_handler(message: Message):
    print(message)
    bot.reply_to(message, 'There is no answer')


@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types='text')
def echo_gigits(message: Message):
    if task.is_weather:
        # bot.reply_to(message, 'сам ищи')

        # city = input('Введите название города: ').replace(' ', '-')
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
        bot.send_message(message.chat.id, 'Ночь :' + night_from + ' ' + night_to)
        bot.send_message(message.chat.id, 'День :' + day_from + ' ' + day_to)

        info_day_light = bs.select('.infoDaylight')
        sunrise_sunset = info_day_light[0].getText()
        bot.send_message(message.chat.id, sunrise_sunset.strip())

        forecast = bs.select('.rSide .description')
        weather = forecast[0].getText()
        bot.send_message(message.chat.id, weather.strip())


    # Exception



bot.polling(timeout=60)
