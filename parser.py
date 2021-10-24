import openpyxl
import roseltorg_parser as ros_pars
import zakupki_parser as zk_pars

WORKBOOK = 'parser.xlsx'

def excel(request_items):
    wb = openpyxl.load_workbook(WORKBOOK)
    sheet = wb['Лист1']

    sheet.delete_rows(2, sheet.max_row)

    for item in request_items:
        sheet.append([
            item['card_id'],
            item['section'],
            item['title'],
            item['organization'],
            item['price'],
            item['date_end'],
            item['platform'],
            item['link']
            ])
        
    wb.save(WORKBOOK)

def main():
    request_items = ros_pars.parse()
    request_items += zk_pars.parse()

    excel(request_items)
    print('Парсинг прошел успешно!')
    print('Количество найденых записей: {0}'.format(len(request_items)))

if __name__ == '__main__':
    main()
