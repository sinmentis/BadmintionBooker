from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
import requests
import time
import json


@dataclass
class Config:
    url_login: str
    url_main: str
    username: str
    password: str


def load_config(config_path="./config.json") -> Config:
    with open(config_path, "r") as file:
        data = json.load(file)
    url_login = data.get("url_login")
    url_main = data.get("url_main")
    username = data.get("username")
    password = data.get("password")

    return Config(url_login, url_main, username, password)


def login(config: Config):
    # Browser option
    options = ChromeOptions()
    options.add_argument("--headless")

    # Lunch a Chrome
    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    browser.get(config.url_login)

    # Fill in username/password, login
    browser.find_element(by="name", value="user").send_keys(config.username)
    browser.find_element(by="name", value="pass").send_keys(config.password)
    browser.find_element(by="id", value="login_btn").click()
    time.sleep(1)

    # Get and set cookies
    cookies = browser.get_cookies()
    print('Cookies', cookies)
    browser.close()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # Check connection status
    response_index = session.get(config.url_main)
    print('Response Status', response_index.status_code)
    print('Response URL', response_index.url)

    if response_index.status_code != 200:
        raise Exception("Ayo something goes wrong homie")

    return session


def main():
    config = load_config()
    session = login(config)
    # TODO:
    # Get available dates
    # Generate time table of that date
    # Make a booking
    # Balances check
    # etc.


if __name__ == "__main__":
    main()
