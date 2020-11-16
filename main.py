import re
import os
import time
import nltk
import spacy
import requests
import numpy as np
import pandas as pd
import seaborn as sns
import lxml.html as html
from selenium import webdriver
from collections import Counter
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from bs4 import BeautifulSoup as bs
from nltk.stem.snowball import SnowballStemmer


nltk.download('stopwords')
nlp = spacy.load("en_core_web_sm")

search_object = ''
names = []
prices = []
sales = []
url = 'https://www.amazon.com'
XPATH_NAME = ('.//a/span[@class="a-size-base-plus a-color-base a-text-normal" or @class="a-size-medium a-color-base a-text-normal"]/text()')
XPATH_PRICE = './/span[@class="a-offscreen" or class="a-color-base"]/text()'#XPATH_PRICE = '//span[@class="a-price-whole"]/text()'
XPATH_SALES = './/span[@class="a-size-base"]/text()'
XPATH_CARD = '//span[contains(@class, "template=SEARCH_RESULTS")]'
search_button_xpath = '/html/body/div[1]/header/div/div[1]/div[2]/div/form/div[3]/div/span/input'
search_field_id ='twotabsearchtextbox'
next_button_css_selector = '.a-last > a:nth-child(1)'
wait = 2                    #seconds
english_stopwords = set(stopwords.words('english'))

def tokenize_phrase(phrase):
    parsed_phrase = nlp(str(phrase))

    for token in parsed_phrase:
        if token.is_punct or token.is_stop or token.text.lower() in english_stopwords:
            continue
        yield token.lemma_.lower()


def word_most_use():
    word_counter = Counter()

    for name in names:
        word_counter.update(tokenize_phrase(name))
    fig = plt.figure(figsize=(10,5))
    ax = fig.gca()

    labels, values = zip(*word_counter.most_common(20))

    indexes = np.arange(len(labels))
    width = 1

    ax.bar(indexes, values, 0.5)
    ax.set_xticks(indexes)
    ax.set_xticklabels( labels, rotation=90, fontsize=15)
    ax.set_title("Words most frecuently use in Amazon product", fontsize=15)
    plt.show()
    search_file = search_object.replace(' ', '_')
    fig.savefig(f'{search_file}.png')# save the figure to file
    plt.close(fig)



def search_from_amazon():
    driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(url)
    search_button = driver.find_element_by_xpath(search_button_xpath)
    search_field = driver.find_element_by_id(search_field_id)
    search_field.send_keys(search_object)
    search_button.click()
    time.sleep(wait)
    while len(prices)< 100:
        page_object = driver.page_source
        parsed = html.fromstring(page_object)
        card_object = parsed.xpath(XPATH_CARD)
        for card in card_object:
            names.append(card.xpath(XPATH_NAME))
            prices.append(card.xpath(XPATH_PRICE))
            sales.append(card.xpath(XPATH_SALES))
        time.sleep(wait)
        driver.execute_script("window.scrollTo(0, 9500)")
        next_button = driver.find_element_by_css_selector(next_button_css_selector)
        next_button.click()
        time.sleep(wait)
    driver.quit()


def create_search_file():
    search_file = search_object.replace(' ', '_')+'.txt'
    print('Your data: ',search_file)
    with open(search_file, 'w') as products_file:
        for name, price in zip(names,prices):
            if len(price)<1:
                price = 'Not Aviable'
            products_file.write(f'{name} - {price}\n')
    wait = input("PRESS ENTER TO CONTINUE.")


def fix_price():
    global prices
    data_prices = prices
    for price in data_prices:
        for element in price:
            try:
                element = float(element.replace("$", ""))
            except ValueError as err:
                sub_chain = element.replace(",", "")
                element = float(sub_chain.replace("$", ""))
    print(data_prices)
    time.sleep(5)

def menu():
    os.system('clear')
    print('Select an option')
    print('\t1 - Basic mode')
    print('\t2 - Pro mode')
    print('\t3 - Exit')

def get_info_user():
    while True:
        global search_object
        search_object = input("What product are you looking for?: ")
        if len(search_object) > 2:
            return(search_object)
        else:
            print('Search no valid!! try again with a long word')
            time.sleep(wait)


def run():
    while True:
        menu()
        option_menu = input("Choose an option >> ")
        if option_menu=="1":
            print ("")
            print("You select opction 1...")
            get_info_user()
            search_from_amazon()
            #fix_price()
            create_search_file()
        elif option_menu=="2":
            print ("")
            print("You select opction 2...")
            get_info_user()
            search_from_amazon()
            #fix_price()
            create_search_file()
            word_most_use()
        elif option_menu=="3":
            break
        else:
            print ("")
            print("You do not select any valid option...")



if __name__ == '__main__':
    run()
