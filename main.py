import datetime
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from slugify import slugify
import requests

username = "asdwww416925"
password = "19961217aA"
max_tweets = 100
topic = "from:freya7974"

def scroll_down(browser):
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument("user-data-dir=selenium")

def login(username, password, topic, browser, wait):
    login_button = wait.until(EC.presence_of_element_located((By.XPATH, '//a[@href="/login"]')))
    login_button.click()

    username_input = wait.until(EC.presence_of_element_located((By.XPATH, './/input[@name="text"]')))
    username_input.send_keys(username)
    username_input.send_keys(Keys.RETURN)

    time.sleep(3)

    password_input = wait.until(EC.presence_of_element_located((By.XPATH, './/input[@name="password"]')))
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

with webdriver.Chrome(options=options) as browser:
    url = 'https://twitter.com/'
    browser.get(url)

    wait = WebDriverWait(browser, 10)

    try:
        login(username, password, topic, browser, wait)
    except TimeoutException:
        pass

    wait.until(EC.presence_of_element_located((By.XPATH, '//input[@enterkeyhint="search"]')))

    search_input = browser.find_element(By.XPATH, '//input[@enterkeyhint="search"]')
    search_input.send_keys(topic)
    search_input.send_keys(Keys.RETURN)

    current_tweets = 0
    user_data = []
    text_data = []
    time_data = []

    while current_tweets < max_tweets:

        for _ in range(5):
            scroll_down(browser)

        tweets = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//article[@role="article"]')))
        
        for tweet in tweets:
            try:
                user = tweet.find_element(By.XPATH, './/span[contains(text(), "@")]').text
                text = tweet.find_element(By.XPATH, ".//div[@lang]").text
                tweet_time = tweet.find_element(By.XPATH, ".//time").get_attribute("datetime")

                tweets_data = [user, text, tweet_time]
            except Exception as e:
                print(f"Error extracting tweet: {e}")
                tweets_data = ['user', 'text', "time"]

            user_data.append(tweets_data[0])
            text_data.append(" ".join(tweets_data[1].split()))
            time_data.append(tweets_data[2])

            current_tweets += 1

        for img in browser.find_elements(By.XPATH, '//img[@alt="Image"]'):
            url = img.get_attribute("src")
            img_blob = requests.get(url).content
            path = os.path.join(os.getcwd(), slugify(url) + ".jpg")
            if os.path.exists(path):
                continue
            with open(path, "wb") as f:
                f.write(img_blob)

        print(f"Scraped {current_tweets} tweets")

        if current_tweets >= max_tweets:
            break

    df = pd.DataFrame({'user': user_data, 'text': text_data, 'time': time_data})
    ts = datetime.strftime(datetime.now(), "%Y-%m-%d")
    df.to_csv(f'tweets_{ts}.csv', index=False)
    print(f"Total {current_tweets} tweets scraped")
