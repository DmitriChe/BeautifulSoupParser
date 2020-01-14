import requests
from bs4 import BeautifulSoup
import vk_api
from time import sleep
import json


DOMAIN = 'https://icobench.com'
url = f'{DOMAIN}/icos?'
html_doc = requests.get(url).text

soup = BeautifulSoup(html_doc, 'html.parser')
# print(soup.prettify())
max_page_num = max([int(num.text) for num in soup.find_all('a', class_='num')])
print(f'number of pages: {max_page_num}')

icos_data = {}

for i in range(max_page_num):
    sleep(1)
    next_page_url = f'{url}page={i + 1}'
    print(f'current page url: {next_page_url}\n')
    html_doc = requests.get(next_page_url).text
    soup = BeautifulSoup(html_doc, 'html.parser')
    ico_list = soup.find('div', class_='ico_list').find_all_next('tr')[1:-1]
    for item in ico_list:
        ico_name = item.find('div', class_='content').a.text
        ico_link = f"{DOMAIN}{item.find('div', class_='content').a.get('href')}"
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

with open('ico_data.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(icos_data))
