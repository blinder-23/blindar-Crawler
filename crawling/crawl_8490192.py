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
from urllib.parse import urlencode, urlunparse
from Logger import myLogger
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


LOG_FILE = '../log/crawl-schedules.log'

logger = myLogger.set_logger(LOG_FILE)

school_code = 8490192


def get_month_raw_data(year: int, month: int):
    # 청주맹학교 학사일정 크롤링

    # Chrome 웹 드라이버 옵션 설정
    options = Options()
    options.add_argument('--headless')  # headless 모드 활성화
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')

    school_schedule_url = make_url(year, month)

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.implicitly_wait(10)
    driver.get(school_schedule_url)

    schedules = []

    floatL_element = driver.find_element(By.CLASS_NAME, "floatL")

    span_elements = floatL_element.find_elements(By.TAG_NAME, "span")

    if len(span_elements) >= 2:
        span_elements[1].click()
    wait = WebDriverWait(driver, 10)

    schedules = click_next_page(driver, 0, schedules)

    logger.info(
        f'📑{school_code} {year}-{month} has {len(schedules)} schedules')

    return schedules


def click_next_page(driver: WebDriver, page_num: int, schedules: list):
    wiz_paging_element = driver.find_element(By.ID, "wizPaging")

    ul_element = wiz_paging_element.find_element(By.TAG_NAME, "ul")
    li_elements = ul_element.find_elements(By.TAG_NAME, "li")

    li_element = li_elements[page_num]
    li_element.click()
    wait = WebDriverWait(driver, 100)
    schedules = parse_schedule(driver, schedules, page_num)
    if (len(li_elements) > page_num+1):
        return click_next_page(driver, page_num+1, schedules)
    else:
        return schedules


def parse_schedule(driver: WebDriver, schedules: list, page_num: int):

    list_day_element = driver.find_element(By.CLASS_NAME, "listDay")

    # listDay 요소의 하위 ul 및 li 목록 선택
    ul_element = list_day_element.find_element(By.TAG_NAME, "ul")
    li_elements = ul_element.find_elements(By.TAG_NAME, "li")

    # 한 li의 하위 dl 중 date 클래스 찾아 텍스트 출력
    for idx, li in enumerate(li_elements):
        date_element = li.find_element(By.CLASS_NAME, "date")
        schedule = li.find_element(By.TAG_NAME, "a")
        modified_date = date_element.text.replace("-", "")
        print(modified_date)
        sId = modified_date+str(page_num*10)+str(idx)
        schedules.append(
            Schedule(school_code, sId, modified_date,
                     schedule.text, schedule.text)
        )
    return schedules


def make_url(year: int, month: int):
    school_schedule_url = f"{school_website_pairs[school_code]}"

    query_params = {
        'codyMenuSeq': '122236359',
        'siteId': 'eungwang21',
        'menuUIType': 'sub',
        'dum': 'dum',
        'command': '',
        'handle': '7908964',
        'imp': 'A',
        'year': str(year),
        'month': str(month),
    }

    query_string = urlencode(query_params)

    return f'{school_schedule_url}?{query_string}'


if __name__ == '__main__':
    if len(sys.argv) < 3:
        year = 2023
        month = 9
    else:
        year, month = map(int, sys.argv[1:])

    print(get_month_raw_data(year, month))
