from Logger import myLogger
import requests
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from config.school_websites import school_website_pairs
import re
import src.sql as sql
import gc
from domain.schedule import Schedule
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


LOG_FILE = '../log/crawl-schedules.log'

logger = myLogger.set_logger(LOG_FILE)

school_code = 8000161


def get_month_raw_data(year: int, month: int):
    # 청주맹학교 학사일정 크롤링

    # Chrome 웹 드라이버 옵션 설정
    options = Options()
    options.add_argument('--headless')  # headless 모드 활성화
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')

    school_schedule_url = f"{school_website_pairs[school_code]}?y={year}&m={month}"

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.implicitly_wait(10)
    driver.get(school_schedule_url)

    schedules = []
    month_str = str(month).zfill(2)
    ul_element = driver.find_element(By.CLASS_NAME, "tch-sch-lst")
    li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

    for addNum, li in enumerate(li_elements):
        schedule_id, title, content, start_date, end_date = parse_schedule(
            driver, li, year, month, addNum)

        for i in range(start_date, end_date+1):
            day = str(i)
            date = f'{year}{month_str}{day.zfill(2)}'
            schedules.append(
                Schedule(school_code, schedule_id, date, title, content))

    logger.info(
        f'📑{school_code} {year}-{month} has {len(schedules)} schedules')

    return schedules


def parse_schedule(driver: WebDriver, li: WebElement, year: int, month: int, addNum: int):

    date = li.find_element(By.TAG_NAME, 'dt').text
    schedule_text = li.find_element(By.CLASS_NAME, "tch-tit-wrap").text

    date = date.split("~")
    if (len(date) > 1):
        start_date = int(date[0].split('.')[2])
        end_date = int(date[1].split('.')[2])
    else:
        start_date = int(date[0].split('.')[2])
        end_date = int(date[0].split('.')[2])

    day = str(start_date)
    date = f'{year}{month}{day.zfill(2)}{addNum}'
    schedule_id = int(date)

    content = li.find_element(By.CLASS_NAME, "tch-ctnt").text
    if (content == ""):
        content = schedule_text

    return [schedule_id, schedule_text, content, start_date, end_date]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        year = 2023
        month = 9
    else:
        year, month = map(int, sys.argv[1:])

    print(get_month_raw_data(year, month))
