from datetime import datetime
import os
import time
from selenium import webdriver 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_binary
import pandas as pd

def save_scrape(df, url):
    crab = url.split("/")[-1]
    title = datetime.now().strftime('%Y-%m-%d')
    # Create the wishlist directory if not existent
    if not os.path.isdir(os.path.join(os.getcwd(), crab)):
        os.mkdir(os.path.join(os.getcwd(), crab))

    path = os.path.join(os.getcwd(), crab, f"{title}.json")
    df.to_json(path)

def script(path):
    script = ""
    with open(path, "r", encoding="utf-8") as f:
        script = f.read()
    
    return script


def scrape(url):
    driver = webdriver.Chrome()
    driver.get(url)

    element_present = EC.presence_of_element_located((By.CLASS_NAME, 'a-price-fraction'))
    WebDriverWait(driver, timeout=30).until(element_present)

    # Execute the binding of helper functions to handle the amazon site
    driver.execute_script(script("amazon.js"))

    # to scroll till page bottom
    for _ in range(5):
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(3)

    # get the products and prices in an array
    data = driver.execute_script("return getData();")

    # Create a dataframe
    df = pd.DataFrame(data=data, columns=["Título", "Preço"])

    print(df)

    save_scrape(df, url)


def analysis(urls):
    for url in urls:
        print(url)

if __name__ == "__main__":
    urls = [
        "https://www.amazon.com.br/hz/wishlist/ls/ILDOZFXMON1K", # Novels
        "https://www.amazon.com.br/hz/wishlist/ls/DFQMDLRX9QLC", # Mangas 
        "https://www.amazon.com.br/hz/wishlist/ls/2T9KJKD2CTGOG", # Livros
    ]

    for url in urls:
        scrape(url)

    analysis(urls)