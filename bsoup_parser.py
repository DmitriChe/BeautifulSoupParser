# ICO_infobot
# ICO_infobot_bot

from bs4 import BeautifulSoup
from time import sleep
import requests
import telebot
import pprint
import json
import os


with open('bot_info', 'r') as f:
    BOT_TOKEN = f.readline().strip()
    print(BOT_TOKEN)

proxies = {
 'http': 'http://167.86.96.4:3128',
 'https': 'http://167.86.96.4:3128',
}

bot = telebot.TeleBot(BOT_TOKEN)

def get_icos(page_num):
    domain = 'https://icobench.com'
    url = f'{domain}/icos?'
    html_doc = requests.get(url).text

    soup = BeautifulSoup(html_doc, 'html.parser')
    # print(soup.prettify())
    max_page_num = max([int(num.text) for num in soup.find_all('a', class_='num')])
    print(f'number of pages: {max_page_num}')

    if page_num > max_page_num:
        page_num = max_page_num

    icos_data = {}

    for i in range(page_num):
        sleep(1)
        next_page_url = f'{url}page={i + 1}'
        print(f'current page url: {next_page_url}\n')
        html_doc = requests.get(next_page_url).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        ico_list = soup.find('div', class_='ico_list').find_all_next('tr')[1:-1]
        for item in ico_list:
            ico_name = item.find('div', class_='content').a.text
            ico_link = f"{domain}{item.find('div', class_='content').a.get('href')}"
            ico_description = item.find('p', class_='notranslate').text
            ico_dates = item.find_all('td', class_='rmv')
            ico_start_date = ico_dates[0].text
            ico_end_date = ico_dates[1].text
            ico_rating = item.find('div', class_='rate').text
            icos_data[ico_name] = {
                'url': ico_link,
                'description': ico_description,
                'start_date': ico_start_date,
                'end_date': ico_end_date,
                'rating': ico_rating
            }
            print(f'{ico_name}: {ico_link}\n{ico_description}')
            print(f'start date: {ico_start_date}\nend date: {ico_end_date}\nrating: {ico_rating}\n')

    return icos_data


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет, человек!\nЯ чат-бот для парсинга инфы об ICO с сайта icobench.com!\n"
                          "Готов служить тебе всеми своими функциями и декораторами.\n\n"
                          "Для парсинга введи команду /parseico")


@bot.message_handler(commands=['parseico'])
def send_welcome(message):
    bot.reply_to(message, "Сколько страниц хотите спарсить?\n"
                          "(Для пробы введите небольшое число: 1-2 страницы, чтобы не пришлось долго ждать)")
    # num_pages = int(input('Сколько страниц хотите спарсить?'))


@bot.message_handler(commands=['file'])
def send_file(message):
    chat_id = message.chat.id

    if os.path.exists('ico_data.json'):
        with open('ico_data.json', 'r') as f_data:
            bot.send_document(chat_id, f_data)
    else:
        sticker_id = 'CAADAgADFgADwDZPE2Ah1y2iBLZnFgQ'
        bot.send_message(chat_id=chat_id, text='Увы, файла с данными нет на сервере...')
        bot.send_sticker(chat_id, sticker_id)


@bot.message_handler(commands=['sticker'])
def no_file_sticker(message):
    chat_id = message.chat.id
    sticker_id = 'CAADAgADFgADwDZPE2Ah1y2iBLZnFgQ'
    bot.send_sticker(chat_id, sticker_id)


@bot.message_handler(content_types='sticker')
def get_sticker_number(message):
    chat_id = message.chat.id
    print(message.sticker.file_id)
    bot.send_message(chat_id, f'This sticker ID is: {message.sticker.file_id}')


@bot.message_handler(content_types='text')
def answer_user(message):
    print(message)
    chat_id = message.chat.id

    if not message.text.isnumeric():
        bot.reply_to(message, 'Пишите, пишите...')
        sleep(2)
        print(chat_id)
        bot.send_message(chat_id, text='Но лучше по делу!')
        sleep(2)
        bot.send_message(chat_id, text='Для справки введите /help')
    else:
        num_pages = int(message.text.strip())
        data = get_icos(num_pages)
        with open('ico_data.json', 'w', encoding='utf-8') as f_data:
            f_data.write(json.dumps(data))
        bot.send_message(chat_id=chat_id, text='Для получения файла с данными введите команду /file')


telebot.apihelper.proxy = proxies
bot.polling()
