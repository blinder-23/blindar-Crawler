import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from domain.schedule import Schedule
import gc
import src.sql as sql
import re
from config.school_websites import school_website_pairs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from pyvirtualdisplay import Display
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from Logger import myLogger


LOG_FILE = '../log/crawl-schedules.log'


school_code = 1342098

logger = myLogger.set_logger(LOG_FILE)


def get_month_raw_data(year: int, month: int):

    # 서울 맹학교 학사일정 크롤링

    # Chrome 웹 드라이버 옵션 설정
    options = Options()
    options.add_argument('--headless')  # headless 모드 활성화
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    options.add_argument('--disable-loging')

   # 현재 스크립트 파일의 위치를 가져옴
    current_dir = os.path.dirname(__file__)

    # 상위 폴더에 있는 chromedriver 파일을 가리키는 상대 경로 설정
    chrome_driver_path = os.path.join(current_dir, '../etc/', 'chromedriver')

    # Chrome 웹 드라이버 시작, 학사일정 페이지에 접속
    school_schedule_url = school_website_pairs[school_code]

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

    _ = driver.get_log('browser')
    driver.implicitly_wait(10)
    driver.get(school_schedule_url)

    year_button = Select(driver.find_element(By.ID, 'srhSchdulYear'))
    year_button.select_by_value(str(year))
    month_button = Select(driver.find_element(By.ID, 'srhSchdulMonth'))
    month_button.select_by_value(str(month).zfill(2))

    # 년, 월 학사일정 페이지 로드
    button_xpath = "//button[@value='선택확인']"
    select_button = driver.find_element(By.XPATH, button_xpath)
    select_button.click()

    # 달력의 각 행을 찾음
    calendar = driver.find_element(By.CLASS_NAME, 'calendar_schedule')
    tbody = calendar.find_element(
        By.TAG_NAME, 'table').find_element(By.TAG_NAME, 'tbody')
    trs = tbody.find_elements(By.TAG_NAME, 'tr')

    month_str = str(month).zfill(2)
    schedules = []

    for tr in trs:
        # 각 날짜에 대해 학사일정을 파싱
        tds = tr.find_elements(By.CSS_SELECTOR, 'td')
        for td in filter(lambda td: '\n' in td.text, tds):
            day = td.text.split('\n')[0]
            ul = td.find_element(By.TAG_NAME, 'ul')
            lis = ul.find_elements(By.TAG_NAME, 'li')
            day = td.text.split('\n')[0]
            date = f'{year}{month_str}{day.zfill(2)}'
            # 각 학사일정에 대해 제목과 내용을 파싱
            for li in lis:
                schedule_id, title, content = parse_schedule(driver, li)
                schedules.append(
                    Schedule(school_code, schedule_id, date, title, content))
    logger.info(
        f'📑{school_code} {year}-{month} has {len(schedules)} schedules')
    return schedules


def parse_schedule(driver: WebDriver, li: WebElement):
    # get title
    a = li.find_element(By.TAG_NAME, 'a')
    # get id
    onclick = a.get_attribute('onclick')
    schedule_id = re.findall('[0-9]+', onclick)[0]
    # get contents
    driver.execute_script("arguments[0].scrollIntoView();", li)

    driver.execute_script("arguments[0].click();", li)
    try:
        table_xpath = "//div[@class='popup_contents']//table/tbody/tr[position()=5]"
        schedule_td = driver.find_elements(By.XPATH, table_xpath)
        schedule_text = schedule_td.text
        # close popup
        close_xpath = "//div[@class='popup_bottom']//button"
        close_button = driver.find_element(By.XPATH, close_xpath)
        close_button.click()
    except Exception as e:
        schedule_text = a.text
    return [schedule_id, a.text, schedule_text]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 crawl_schedules.py [year] [month]')

        exit(0)
    year, month = map(int, sys.argv[1:])

    print(get_month_raw_data(year, month))
