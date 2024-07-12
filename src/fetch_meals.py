import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import requests
import re
from domain.meal import Meal
import src.sql as sql
from config.school_codes import school_code_pairs
import src.meal_sql as db

from Logger import myLogger


LOG_FILE = '../log/meals.log'

logger = myLogger.set_logger(LOG_FILE)


def get_api_key():
    with open('../etc/neis-key', 'r') as f:
        return f.read().strip()


def load_meals(year: int, month: int):
    url = 'https://open.neis.go.kr/hub/mealServiceDietInfo'
    api_key = get_api_key()

    all_data = []

    for office_code, school_code in school_code_pairs:
        try:
            params = {'KEY': api_key, 'Type': 'json', 'pIndex': 1, 'pSize': 100,
                      'ATPT_OFCDC_SC_CODE': office_code, 'SD_SCHUL_CODE': school_code, 'MLSV_YMD': f'{year}{month:02}'}
            response = requests.get(url, params=params)
            data = parse(response.json(), school_code, year, month)

            logger.info(
                f'🍚{school_code} {year} {month} has {len(data)} meals.')
            school_info = {'office_code': office_code,
                           'school_code': school_code}
            labeled_data = {'school_info': school_info, 'data': data}
            all_data.append(labeled_data)
        except:
            logger.warn(
                f'🚨Error occured while fetching meals for {school_code} {year} {month}.')
            continue

    return all_data


def parse(json, school_code: int, year: int, month: int):
    if 'RESULT' in json.keys():
        _, code = json['RESULT']['CODE'].split('-')
        return on_request_error(code, school_code, year, month)

    response = json['mealServiceDietInfo']
    code = parse_header(response[0])
    if code == '000':
        # 정상
        meals = parse_body(response[1])
        return meals
    else:
        # 에러
        return on_request_error(code, school_code, year, month)


def on_request_error(code: str, school_code: int, year: int, month: int):
    if code == '200':
        return []
    else:
        logger.warn(
            f'🚨Error {code} occured while fetching meals for {school_code} {year} {month}.')
        return []


def parse_header(header):
    head = header['head']
    # count = head[0]['list_total_count']
    _, code = head[1]['RESULT']['CODE'].split('-')
    return code


def parse_body(body: dict):
    return [Meal(ymd=meal['MLSV_YMD'],
                 dishes=parse_dishes(meal['DDISH_NM']),
                 origins=parse_origins(meal['ORPLC_INFO']),
                 nutrients=parse_nutrients(meal['NTR_INFO']),
                 calorie=parse_calorie(meal['CAL_INFO']),
                 meal_time=parse_meal_time(meal['MMEAL_SC_NM'])) for meal in body['row']]


def parse_dishes(dishes):
    menus = parse_br(dishes)
    menu_allergies = map(parse_menu_allergies, menus)
    return list(menu_allergies)


def parse_menu_allergies(menus: str):
    splitted = menus.strip().split(' ')
    menu_name = splitted[0]
    if len(splitted) == 1:
        allergies = []
    else:
        allergies = re.findall('[0-9]+', splitted[1])
    return [menu_name, allergies]


def parse_origins(origins):
    origin_list = parse_br(origins)
    return {ingredient: origin for ingredient, origin in map(lambda x: x.split(' : '), origin_list)}


def parse_nutrients(nutrients):
    nutrient_pattern = r'(?P<nutrient>[가-힣A-Z]+)'
    unit_pattern = r'\((?P<unit>.*?)\)'
    amount_pattern = r'(?P<amount>[0-9.]+)'
    pattern = f'{nutrient_pattern}{unit_pattern} : {amount_pattern}'

    nutrient_list = parse_br(nutrients)
    return [list(re.match(pattern, nutrient).groups()) for nutrient in nutrient_list]


def parse_calorie(calorie):
    return calorie.split(" ")[0]


def parse_meal_time(meal_time):
    return meal_time


def parse_br(s: str):
    return s.split('<br/>')


def fetch_and_store_meals(year: int, month: int):
    allData = load_meals(year, month)
    logger.info(
        f'Successful Fetched {len(allData)} schools\' meals for {year} {month}.')
    db.save_meals(allData)


# 직접 실행할때만 실행되는 코드
if __name__ == '__main__':
    # 인자가 3개 이하면 사용 방법 출력
    if len(sys.argv) < 3:
        print('Usage: python3 fetch_meals.py [year] [month]')
        exit(0)
    year, month = map(int, sys.argv[1:])
    allData = load_meals(year, month)

    db.save_meals(allData)


