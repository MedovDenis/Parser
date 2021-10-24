import requests
from bs4 import BeautifulSoup
import datetime as DT

HOST = 'https://www.roseltorg.ru'
URL = 'https://www.roseltorg.ru/procedures/search?sale=0&source%5B%5D=2&status%5B%5D=0&region%5B%5D=63&end_price=2+500+000&currency=all'
PAGE = '&page='
FROM = '&from='
HEADERS = { 'user-agent': 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'accept':
                '*/*'
            }

def get_html(url, params = None):
    return requests.get(url, headers=HEADERS, params=params)

def get_next_url(html, _page, _from):
    soup = BeautifulSoup(html, 'html.parser')
    next_page = soup.find('a', class_='pagination__btn--next')
    if next_page:
        url = URL + PAGE + str(_page) + FROM + str(_from)
        print('[{0}] {1}'.format(_page,url))
    else: 
        url = 'None'
    return url

def get_id(card_id):
    return card_id[0:11]

def get_price(price):
    price = price.replace(' ','')
    price = price.replace(',','.')
    return float(price)

def get_date(date):
    date = date[0:10]
    date = date.replace('.', '/')
    date = DT.datetime.strptime(date, "%d/%m/%Y").date()
    return date

def get_section(section):
    if section.find('44-ФЗ') != -1:
        section = '44-ФЗ'
    elif  section.find('223-ФЗ') != -1:
        section = '223-ФЗ'
    else:
        section = section.strip()
    return section

def get_content(html, _page, _from):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='search-results__item')

    request_items = []
    for item in items:
        request_items.append({
            'card_id': get_id(item.find('div', class_='search-results__header').find('a', class_='search-results__link').get_text(strip=True)),
            'section': get_section(item.find('div', class_='search-results__header').find('div', class_='search-results__section').find('p').get_text(strip=True)),
            'title': item.find('div', class_='search-results__subject').find('a', class_='search-results__link').get_text(strip=True),
            'organization': item.find('div', class_='search-results__customer').find('p', class_='search-results__tooltip').get_text(strip=True),
            'price': get_price(item.find('div', class_='search-results__sum').find('p').get_text(strip=True)),
            'date_end': get_date(item.find('time', class_='search-results__time').get_text(strip=True)),
            'link': HOST + item.find('div', class_='search-results__header').find('a', class_='search-results__link').get('href'),
            'platform' : 'Росельторг'
        })
    
    _page += 1
    _from += 10
    next_pages = get_next_url(html, _page, _from)

    if next_pages != 'None':
        next_html = get_html(next_pages)
        if next_html.status_code == 200:
            request_items += get_content(next_html.text, _page, _from)
        else:
            print('Error')

    return request_items

def parse():
    _page = 0
    _from = 0
    url = URL + PAGE + str(_page) + FROM + str(_from)
    html = get_html(url)
    request_items = []
    if html.status_code == 200:
        request_items = get_content(html.text, _page, _from)
    else:
        print('Error')
    
    return request_items
    