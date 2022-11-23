from helper_classes import *

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import requests
import time
import json


def load_config(config_path="./config.json") -> Config:
    with open(config_path, "r") as file:
        data = json.load(file)
    url_login = data.get("url_login")
    url_main = data.get("url_main")
    username = data.get("username")
    password = data.get("password")
    preferences_list = []
    for preference in data.get("preference"):
        week = int(preference.get("week"))
        duration_min = int(preference.get("duration_min"))
        start_time = int(preference.get("start_time"))
        court = int(preference.get("court"))
        priority = int(preference.get("priority"))
        preferences_list.append(Preference(week, duration_min, start_time, court, priority))
    return Config(url_login, url_main, username, password, preferences_list)


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


def parse_available_date(browser):
    available_time = []

    # Drop down list
    date_form = Select(browser.find_element(By.NAME, value="date"))
    for element in date_form.options:
        year, month, day = element.get_attribute("value").split()
        available_time.append(datetime.datetime(int(year), int(month), int(day)))

    return available_time


def parse_court_table(browser):
    # Getting table header
    header_column_xpath = '//*[@id="grid_box"]/div[1]/table/tbody/tr[2]'
    header_column = browser.find_elements(By.XPATH, header_column_xpath)[0]
    header_column_element_list = header_column.find_elements(By.XPATH, 'td')
    header_column_text_list = []
    for element in header_column_element_list:
        cell_text = element.find_elements(By.XPATH, 'div')[0].text
        header_column_text_list.append(cell_text)

    # Getting timetable content
    timetable_content_xpath = '//*[@id="grid_box"]/div[2]/table/tbody'
    timetable_content = browser.find_elements(By.XPATH, timetable_content_xpath)[0]
    timetable_content_row_list = timetable_content.find_elements(By.XPATH, 'tr')
    time_index = 1  # const int

    # Skip the first line for style setting :)
    for element in timetable_content_row_list[time_index:]:
        row_list = element.find_elements(By.XPATH, 'td')
        time_str = ""
        for index, row in enumerate(row_list):
            style = row.get_attribute("style")
            # Assume time element doesn't have background-color
            if "background-color" in style:
                if any(value in style for value in TimeSlotStatus.Available.value):
                    print(f"{time_str} is available for {header_column_text_list[index]}")
            else:
                time_str = row.text


def main():
    config = load_config()
    browser, session = login(config)
    available_dates = parse_available_date(browser)
    parse_court_table(browser)
    # TODO:
    # Navigate to that date
    # Parse the timetable
    # Match timetable with preference
    # Make a booking '/html/body/form/div/div/div/div[3]/div[2]/button' '//*[@id="modal_next"]
    # Balances check
    # etc.
    browser.close()


if __name__ == "__main__":
    main()
