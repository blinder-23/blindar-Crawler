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
from Logger import myLogger
import requests
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


LOG_FILE = '../log/crawl-schedules.log'

logger = myLogger.set_logger(LOG_FILE)

school_code = 7801213


def get_month_raw_data(year: int, month: int):
    # 인천혜광학교 학사일정 크롤링

    # Chrome 웹 드라이버 옵션 설정
    options = Options()
    options.add_argument('--headless')  # headless 모드 활성화
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')

    # Chrome 웹 드라이버 시작, 학사일정 페이지에 접속
    school_schedule_url = school_website_pairs[school_code]
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.implicitly_wait(10)
    driver.get(school_schedule_url)

    if (month < 3):
        table_xpath = "//ul[@class='calendar_btn']/li[2]"
        driver.find_element(By.XPATH, table_xpath).click()
    elif (month < 9):
        table_xpath = "//ul[@class='calendar_btn']/li[1]"
        driver.find_element(By.XPATH, table_xpath).click()
    else:
        table_xpath = "//ul[@class='calendar_btn']/li[2]"
        element = driver.find_element(By.XPATH, table_xpath)
        driver.execute_script("arguments[0].click();", element)

    calendar_elements = driver.find_elements(By.CLASS_NAME, "calendar")
    schedules = []
    for calendar_element in calendar_elements:
        date_element = calendar_element.find_element(By.CLASS_NAME, "date")
        span_element = date_element.find_element(
            By.TAG_NAME, "span")  # date 클래스를 가진 요소 하위의 span 요소
        date_text = span_element.text  # span 요소의 텍스트 추출

        parts = date_text.split()
        if len(parts) == 2:
            targetYear = parts[0].replace("년", "")  # "2023"
            raw_month = parts[1].replace("월", "")  # "9"
            targetMonth = raw_month.zfill(2)  # "09"
            month_str = str(month).zfill(2)
            if (targetMonth == month_str and targetYear == str(year)):
                event_dl = calendar_element.find_element(
                    By.CLASS_NAME, "event")
                dd_element = event_dl.find_element(By.TAG_NAME, 'dd')
                ul_element = dd_element.find_element(By.TAG_NAME, 'ul')
                li_elements = ul_element.find_elements(By.TAG_NAME, 'li')

                for li in li_elements:
                    schedule_id, title, content, start_date, end_date = parse_schedule(
                        driver, li)

                    for i in range(start_date, end_date+1):
                        day = str(i)
                        date = f'{year}{month_str}{day.zfill(2)}'
                        schedules.append(
                            Schedule(school_code, schedule_id, date, title, content))

        else:
            print("올바른 형식의 날짜 문자열이 아닙니다.")

    logger.info(
        f'📑{school_code} {year}-{month} has {len(schedules)} schedules')

    return schedules


def parse_schedule(driver: WebDriver, li: WebElement):

    li_id = li.get_attribute('id')
    schedule_id = li_id.split("e")[1]  # "date1234567" -> "1234567"

    text = li.text
    parts = text.split(":")
    date_range = parts[0].replace("일", "").split("~")

    if len(date_range) == 1:
        start_date = int(date_range[0])
        end_date = int(date_range[0])
    else:
        start_date = int(date_range[0])
        end_date = int(date_range[1])

    schedule_text = parts[1]

    return [schedule_id, schedule_text, schedule_text, start_date, end_date]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        year = 2023
        month = 9
    else:
        year, month = map(int, sys.argv[1:])

    print(get_month_raw_data(year, month))
