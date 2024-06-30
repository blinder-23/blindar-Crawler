import gc
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import time
import src.crawl_schedules as crawl_schedules
import src.fetch_meals as remote_meals
import datetime
from Logger import myLogger
from util import DateUtils

LOG_FILE = '../log/fetch-data.log'

logger = myLogger.set_logger(LOG_FILE)
sys.excepthook = myLogger.handle_exception


def fetch_schedules(year: int, month: int):
    crawl_schedules.crawl_and_save(year, month)
    gc.collect()


def fetch_schedules_with_execution_time(year: int, month: int):
    logger.info(f'🚀Schedule crawling started. {year}-{month}')
    schedule_time = calculate_time(fetch_schedules, year, month)
    logger.info(
        f'👋Schedule crawling finished. {year}-{month} Taken: {schedule_time} seconds.')


def fetch_meals(year: int, month: int):
    remote_meals.fetch_and_store_meals(year, month)
    gc.collect()


def fetch_meals_with_execution_time(year: int, month: int):
    logger.info(f'🚀Meal fetching started. {year}-{month}')
    meal_time = calculate_time(fetch_meals, year, month)
    logger.info(f'👋Meal fetching finished. Taken: {meal_time} seconds.')


def calculate_time(function, arg1, arg2):
    # returns the execution time of function, in seconds
    start_time = time.time()
    try:
        function(arg1, arg2)
    except Exception as e:
        logger.warning(f'🚨Exception while executing {function.__name__}: {e}')
    finally:
        finish_time = time.time()
    return round(finish_time-start_time, 2)


if __name__ == '__main__':
    os.environ['WDM_LOG'] = '0'

    if len(sys.argv) < 3:
        print(
            'Usage 1: python3 fetch_data.py [start_year] [start_month] [end_year] [end_month]\nUsage 2: python3 fetch_data.py [year] [month]')
    elif len(sys.argv) == 3:
        year, month = map(int, sys.argv[1:])
        DateUtils.check_args(year, month)
        fetch_schedules_with_execution_time(year, month)
        fetch_meals_with_execution_time(year, month)

    elif len(sys.argv) == 5:
        start_year, start_month, end_year, end_month = map(int, sys.argv[1:5])

        DateUtils.check_args_range(
            start_year, start_month, end_year, end_month)

        current_year, current_month = start_year, start_month

        while (current_year, current_month) <= (end_year, end_month):
            fetch_schedules_with_execution_time(current_year, current_month)
            fetch_meals_with_execution_time(current_year, current_month)
            # Increment month and year
            current_month += 1
            if current_month > 12:
                current_month = 1
                current_year += 1
    else:
        print(
            'Usage 1: python3 fetch_data.py [start_year] [start_month] [end_year] [end_month]\nUsage 2: python3 fetch_data.py [year] [month]')
