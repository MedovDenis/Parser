import requests
from bs4 import BeautifulSoup
import datetime as DT

HOST = 'https://zakupki.gov.ru'
URL_FIRST = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?searchString=&morphology=on&search-filter=%D0%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F'
URL_LAST = '&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&savedSearchSettingsIdHidden=&sortBy=UPDATE_DATE&fz44=on&fz223=on&af=on&placingWayList=&selectedLaws=&priceFromGeneral=&priceFromGWS=&priceFromUnitGWS=&priceToGeneral=2500000&priceToGWS=&priceToUnitGWS=&currencyIdGeneral=-1&publishDateFrom=&publishDateTo=&applSubmissionCloseDateFrom=&applSubmissionCloseDateTo=&customerIdOrg=&customerFz94id=&customerTitle=&customerPlace=5277374&customerPlaceCodes=63000000000&delKladrIds=5277374&delKladrIdsCodes=63000000000&okpd2Ids=&okpd2IdsCodes=&OrderPlacementSmallBusinessSubject=on&OrderPlacementRnpData=on&OrderPlacementExecutionRequirement=on&orderPlacement94_0=0&orderPlacement94_1=0&orderPlacement94_2=0'
PAGE = '&pageNumber='
HEADERS = { 'user-agent': 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'accept':
                '*/*'
            }

def get_html(url, params = None):
    return requests.get(url, headers=HEADERS, params=params)

def get_next_url(html, _page):
    soup = BeautifulSoup(html, 'html.parser')
    next_page = soup.find('a', class_='paginator-button-next')
    if next_page:
        url = URL_FIRST + PAGE + str(_page) + URL_LAST
        print('[{0}] {1}'.format(_page,url))
    else: 
        url = 'None'
    return url

def get_id(card_id):
    card_id = card_id.replace(' ', '')
    card_id = card_id.replace('№', '')
    return card_id

def get_price(price):
    price = price.replace(' ','')
    price = price.replace(u'\xa0', '')
    price = price.replace('₽','')
    price = price.replace(',','.')
    return float(price)

def get_date(date):
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

def get_content(html, _page):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='search-registry-entry-block')

    request_items = []
    for item in items:

        date_end = item.find_all('div', class_='data-block__value')
        if len(date_end) > 2:
            date_end = get_date(date_end[2].get_text(strip=True))
        else: 
            date_end = 'none'

        section = item.find('div', class_='registry-entry__header-top__title').get_text(strip=True)
        link = ''
        if section.find('44-ФЗ') != -1:
            link = HOST + item.find('div', class_='registry-entry__header-mid__number').find('a').get('href')
        else:
            link = item.find('div', class_='registry-entry__header-mid__number').find('a').get('href')


        # 44-ФЗ Электронный аукцион


        request_items.append({
            'card_id': get_id(item.find('div', class_='registry-entry__header-mid__number').find('a').get_text(strip=True)),
            'section': get_section(section),
            'title': item.find('div', class_='registry-entry__body-value').get_text(strip=True),
            'organization': item.find('div', class_='registry-entry__body-href').find('a').get_text(strip=True),
            'price': get_price(item.find('div', class_='price-block__value').get_text(strip=True)),
            'date_end': date_end,
            'link': link,
            'platform' : 'ЕИС'
        })
    
    _page += 1
    next_pages = get_next_url(html, _page)

    if next_pages != 'None':
        next_html = get_html(next_pages)
        if next_html.status_code == 200:
            request_items += get_content(next_html.text, _page)
        else:
            print('Error')

    return request_items

def parse():
    _page = 1
    url = url = URL_FIRST + PAGE + str(_page) + URL_LAST
    html = get_html(url)
    request_items = []
    if html.status_code == 200:
        request_items = get_content(html.text, _page)
    else:
        print('Error')
    
    return request_items
