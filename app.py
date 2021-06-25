# from bs4 import BeautifulSoup
# import requests
import re
from selenium import webdriver
import selenium
from selenium.webdriver.chrome.options import Options
import csv
# import os
# import time

FILE = 'ozon.csv'

msg = {
    'error': """
Неправильный формат данных, делай так:
---------------
Поисковая фраза
ID продукта 
---------------
"""
}


# services = ['ozon', 'wildberries']

def parser():
    print(greet())
    action = input().strip().lower()
    if action == 'создать':
        create_file(FILE)
    print('Можешь вводить запросы ')
    while True:
        start()


def greet():
    return """
    Вводи сообщение в следующем формате:
    ---------------
    Поисковая фраза
    ID продукта 
    ---------------
    Чтобы создать новый файл набери "Создать"
    Чтобы записывать в существующий просто нажми "Enter"
    
    Для выхода нажми Ctrl-C
    """

def start():
    try:
        query = input('Запрос: \n').strip()
        product = int(input('\nКод товара: \n'))
    except ValueError:
        return msg.get('error')

    if key_is_valid(product):
        result = open_page(1, query, product)
        try:
            writer(result, FILE)
        except PermissionError:
            return 'Нужно закрыть файл Excel. Закрой Excel и повтори запрос'
        except TypeError:
            writer({'Артикул': product, 'Ключ': query, 'Страница': f'Страница: Товар не найден',
                  'Позиция': ''}, FILE)
        # os.startfile(FILE)
        return result
    else:
        return 'По данному коду товар не найден'


def key_is_valid(product):
    # Настройки для оптимизации
    options = Options()
    # options.add_argument("--window-size=1440, 900")
    # options.add_argument("--headless")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-software-rasterizer")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--disable-crash-reporter")
    # options.add_argument("--disable-extensions")
    # options.add_argument("--disable-in-process-stack-traces")
    # options.add_argument("--disable-logging")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    # options.add_argument("--output=/dev/null")

    driver = webdriver.Chrome(options=options)

    try:
        url = f'https://www.ozon.ru/search/?from_global=true&text={product}'
        driver.get(url)
        driver.find_element_by_class_name("b6r7")
        driver.close()
        return True
    except selenium.common.exceptions.NoSuchElementException:
        return False


def open_page(num, query, product):

    # ___________________________ Wildberries ___________________________   Оставил на всякий случай
    # if shop == 'Wildberries':
    #     url = f'https://www.wildberries.ru/catalog/0/search.aspx?search={query}&xsearch=true&page={num}'
    #     data = requests.get(url)
    #     soup = BeautifulSoup(''.join(data.text), features="lxml")
    #
    #     total_pages = round(int(re.sub('\D', '', soup.find('span', {'class': 'goods-count'}).text.strip())) / 100 - 0.51)
    #     print(total_pages, num)
    #
    #     current_position = 0
    #
    #     if type(total_pages) == int and total_pages > -1:
    #         result = soup.findAll('div', {'class': 'dtList-inner'})
    #         for index, r in enumerate(result):
    #             if product == r.find('a', {'class': 'ref_goods_n_p'})['href'].split('/')[2]:
    #                 current_position = index + 1
    #                 break
    #
    #         if current_position:
    #             print(current_position)
    #             return f"Страница: {num}\nПозиция: {current_position}"
    #         elif total_pages + 1 == num:
    #             return 'Товар не найден'
    #         else:
    #             return open_page(num + 1, query, product, shop)
    #     else:
    #         return 'Нет товаров по данному запросу'
    # else:
    # ________________________________Ozon_______________________________
    options = Options()
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=options)
    url = f'https://www.ozon.ru/search/?from_global=true&page={num}&text={query}'
    driver.get(url)
    try:
        products_total = int(''.join(re.findall(r'\d+', str(driver.find_element_by_class_name("b6r7").text))))
    except selenium.common.exceptions.NoSuchElementException:
        return 'Нет товаров по данному запросу'

    if products_total <= 36:
        total_pages = 1
    else:
        total_pages = products_total // 36 + 1

    print(f'Поиск {num} из {total_pages}')

    current_position = 0

    result = driver.find_elements_by_css_selector(".a0y9:nth-child(2)")
    print(f'Найдено элементов {len(result)}') # должно быть 36. Если 4 нужно добавить wait так как дожидается пока подгрузится js


    for index, r in enumerate(result):
        if r.get_attribute('href') and str(product) in r.get_attribute('href'):
            current_position = index + 1
            break
    # driver.close()
    if current_position:
        result = {'Артикул': product, 'Ключ': query, 'Страница': f'Страница: {num}',
                  'Позиция': f'Позиция: {current_position + 1}'}
        print(f'Страница: {num}, Позиция: {current_position + 1}')
        return result
    elif total_pages + 1 == num:
        return "Нет товаров по данному запросу"

    else:
        return open_page(num + 1, query, product)

def create_file(filename):
    with open(filename, "w", newline="") as file:
        write = csv.writer(file, delimiter=';')
        write.writerow(['Артикул', 'Ключ', 'Страница', 'Позиция'])
        print('Новый файл создан')

def writer(items, filename):
    with open(filename, "a", newline="") as file:
        write = csv.writer(file, delimiter=';')
        write.writerow([items['Артикул'], items['Ключ'], items['Страница'], items['Позиция']])



parser()
