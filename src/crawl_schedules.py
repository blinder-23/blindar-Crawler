from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from pyvirtualdisplay import Display
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from config.school_websites import school_website_pairs
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import sql as sql
import gc
from domain.schedule import Schedule
from crawling.crawl_1342098 import get_month_raw_data as crawl_1342098
from crawling.crawl_7010578 import get_month_raw_data as crawl_7010578
from crawling.crawl_7310156 import get_month_raw_data as crawl_7310156
from crawling.crawl_7310155 import get_month_raw_data as crawl_7310155
from crawling.crawl_7801213 import get_month_raw_data as crawl_7801213
from crawling.crawl_8000157 import get_month_raw_data as crawl_8000157
from crawling.crawl_8000161 import get_month_raw_data as crawl_8000161
from crawling.crawl_8320214 import get_month_raw_data as crawl_8320214
from crawling.crawl_8490192 import get_month_raw_data as crawl_8490192
from Logger import myLogger


LOG_FILE = '../log/crawl-schedules.log'

logger = myLogger.set_logger(LOG_FILE)


def crawl(year: int, month: int):
    datas = []
    crawl_functions = [
        crawl_1342098,
        crawl_7010578,
        crawl_7310155,
        crawl_7310156,
        crawl_7801213,
        crawl_8000157,
        crawl_8000161,
        crawl_8320214,
        # crawl_8490192
    ]

    for crawl_function in crawl_functions:
        try:
            datas.append(crawl_function(year, month))
        except Exception as e:
            logger.warn(f"{e} occured when crawling {crawl_function}")
            datas.append(None)

    return datas


def crawl_and_save(year: int, month: int):
    datas = crawl(year, month)
    for data in datas:
        sql.insert_schedules(data, year, month)


def save(datas: dict):
    for (year, month), data in datas.items():
        sql.insert_schedules(data, year, month)


def crawl_then_save(years: range, months: range):
    # 모든 데이터를 가져온 후 저장
    # crawl_and_save()는 가져온 데이터를 즉시 저장
    datas = {}
    for year in years:
        for month in months:
            data = crawl(year, month)
            datas[(year, month)] = data
    gc.collect()
    save(datas)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python3 crawl_schedules.py [year] [month]')

        exit(0)
    year, month = map(int, sys.argv[1:])

    print(crawl(year, month))
