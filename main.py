from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import requests
import time
import json
import datetime


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


def login(config: Config) -> tuple:
    # Browser option
    options = ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Lunch a Chrome
    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
    browser.get(config.url_login)

    # Fill in username/password, login
    browser.find_element(By.NAME, value="user").send_keys(config.username)
    browser.find_element(By.NAME, value="pass").send_keys(config.password)
    browser.find_element(By.ID, value="login_btn").click()
    time.sleep(1)

    # Get and set cookies
    cookies = browser.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # Check connection status
    response_index = session.get(config.url_main)

    if response_index.status_code != 200:
        print('Response Status', response_index.status_code)
        raise Exception("Ayo something goes wrong homie")
    else:
        print("We are up!")

    return browser, session


def parse_time(browser):
    available_time = []

    # Drop down list
    date_form = Select(browser.find_element(By.NAME, value="date"))
    for element in date_form.options:
        year, month, day = element.get_attribute("value").split()
        available_time.append(datetime.datetime(int(year), int(month), int(day)))

    return available_time


def parse_court_table(browser):
    # xpath for table header <tr>
    header_column_xpath = '//*[@id="grid_box"]/div[1]/table/tbody/tr[2]'
    header_column = browser.find_elements(By.XPATH, header_column_xpath)[0]
    header_column_element_list = header_column.find_elements(By.XPATH, 'td')
    header_column_text_list = []
    for index in range(0, len(header_column_element_list)):
        final_xpath = f"{header_column_xpath}/td[{index + 1}]/div"
        cell_text = browser.find_elements(By.XPATH, final_xpath)[0].text
        header_column_text_list.append(cell_text)


def main():
    config = load_config()
    browser, session = login(config)
    available_time = parse_time(browser)
    parse_court_table(browser)
    # TODO:
    # Get available dates
    # Generate time table of that date
    # Make a booking
    # Balances check
    # etc.
    browser.close()


if __name__ == "__main__":
    main()
