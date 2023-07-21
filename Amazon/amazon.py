import os
import time
import chromedriver_binary
import pandas as pd
from selenium import webdriver 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from os.path import join

# ** If you do not have an .csv created by this script **
# master_df = pd.DataFrame(None, columns=["title"])

# ** If you already have one **
master_df = pd.read_csv(os.path.join(os.getcwd(), "amazon", f"amazon_data.csv"))
TODAY = datetime.now().strftime('%Y-%m-%d')

def save_scrape():
    path = os.path.join(os.getcwd(), "amazon", f"amazon_data.csv")
    master_df.to_csv(path, index=False)

def script(path):
    script = ""
    with open(path, "r", encoding="utf-8") as f:
        script = f.read()
    
    return script

def scrape(url):
    # global master_df
    driver = webdriver.Chrome()
    driver.get(url)

    element_present = EC.presence_of_element_located((By.CLASS_NAME, 'a-price-fraction'))
    WebDriverWait(driver, timeout=30).until(element_present)

    # Execute the binding of helper functions to handle the amazon site
    driver.execute_script(script(join("amazon", "amazon.js")))

    # to scroll till page bottom
    for _ in range(5):
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(3)

    # get the products and prices in an array
    data = driver.execute_script("return getData();")

    # Remove the index and title columns from the count
    length = len(master_df.columns.to_list()) - 1
    for title, price in data:
        result = master_df.loc[master_df['title'] == title]
        
        # It means that the product with this title is not in the dataframe
        if result.shape[0] == 0:
            new_title = [title]
            [new_title.append(-1.00) for _ in range(length)]
            new_title[-1] = price
            master_df.loc[len(master_df)] = new_title
        else:
            master_df.loc[master_df['title'] == title, [TODAY]] = price

    print(data)

    save_scrape()


def send_email():
    pass

def alert_goodprices():
    pass


if __name__ == "__main__":
    urls = [
        "https://www.amazon.com.br/hz/wishlist/ls/ILDOZFXMON1K", # Novels
        "https://www.amazon.com.br/hz/wishlist/ls/DFQMDLRX9QLC", # Mangas 
        "https://www.amazon.com.br/hz/wishlist/ls/2T9KJKD2CTGOG", # Livros
    ]

    placeholder = [-1.00 for _ in range(master_df.shape[0])]
    master_df[TODAY] = placeholder

    for url in urls:
        scrape(url)

    alert_goodprices()