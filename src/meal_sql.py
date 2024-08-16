from sqlite3 import Cursor
import pymysql
import os
from domain.meal import Meal
from Logger import myLogger
import json

LOG_FILE = '../log/db.log'

logger = myLogger.set_logger(LOG_FILE)


def start_mysql():
    os.system('../scripts/start_mysql.sh')


def get_connection():
    db_config = {}
    with open('../etc/database', 'r', encoding='utf-8') as f:
        for line in f:
            key, value = line.strip().split('=', 1)
            db_config[key] = value
    
    # 데이터베이스 연결 설정
    return pymysql.connect(
        host=db_config.get('host', 'localhost'),  # 기본값 설정
        port=int(db_config.get('port', 3306)),    # 기본값 설정
        user=db_config.get('user', 'root'),
        password=db_config.get('password', ''),
        charset=db_config.get('charset', 'utf8mb4')
    )


def create_and_use_database(cursor: Cursor):
    cursor.execute('CREATE DATABASE IF NOT EXISTS hanbit')
    cursor.execute('USE hanbit')


# 주어진 문자열 데이터를 JSON 형식으로 변환




def create_table_if_not_exists(cursor, table_name, create_sql):
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        cursor.execute(create_sql)
        print(f"{table_name} table created.")

def check_table_exists(cursor):
    create_table_if_not_exists(cursor, 'meal', '''
        CREATE TABLE meal (
            meal_id INT AUTO_INCREMENT,
            school_code INT NOT NULL,
            date DATE NOT NULL,
            meal_time VARCHAR(255) NOT NULL DEFAULT '중식',
            calorie Double NULL,
            PRIMARY KEY (meal_id),
            UNIQUE KEY (school_code, date, meal_time),
            FOREIGN KEY (school_code) REFERENCES school(school_code) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    create_table_if_not_exists(cursor, 'dish', '''
        CREATE TABLE dish (
            dish_id INT AUTO_INCREMENT,
            meal_id INT NOT NULL,
            name VARCHAR(50) NOT NULL,
            primary key (dish_id),
            FOREIGN KEY (meal_id) REFERENCES meal(meal_id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    create_table_if_not_exists(cursor, 'ingredient', '''
        CREATE TABLE ingredient (
            ingredient_id INT AUTO_INCREMENT,
            name VARCHAR(50) NOT NULL,
            origin VARCHAR(50) NOT NULL DEFAULT '정보 없음',
            PRIMARY KEY (ingredient_id)
        )
    ''')

    create_table_if_not_exists(cursor, 'meal_ingredients', '''
        CREATE TABLE meal_ingredients (
            meal_id INT NOT NULL,
            ingredient_id INT NOT NULL,
            PRIMARY KEY (meal_id, ingredient_id),
            FOREIGN KEY (meal_id) REFERENCES meal (meal_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (ingredient_id) REFERENCES ingredient (ingredient_id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    create_table_if_not_exists(cursor, 'dish_allergies', '''
        CREATE TABLE dish_allergies (
            allergy_id INT AUTO_INCREMENT,
            dish_id INT NOT NULL,
            allergy INT NOT NULL,
            PRIMARY KEY (allergy_id,dish_id),
            FOREIGN KEY (dish_id) REFERENCES dish (dish_id) ON DELETE CASCADE ON UPDATE CASCADE
        )
    ''')

    create_table_if_not_exists(cursor, 'nutrient', '''
        CREATE TABLE nutrient(
            nutrient_id INT PRIMARY KEY AUTO_INCREMENT,
            meal_id INT NOT NULL,
            name VARCHAR(50),
            unit VARCHAR(10),
            amount DOUBLE(10,2),
            FOREIGN KEY (meal_id) REFERENCES meal(meal_id) ON DELETE CASCADE ON UPDATE CASCADE
    )
    ''')

    return True


def save_meals(allData):


    with get_connection() as connection:
        with connection.cursor() as cursor:
            create_and_use_database(cursor)
            check_table_exists(cursor)
            for mealsWithSchool in allData:
                school_code=mealsWithSchool['school_info']['school_code']
                meals = mealsWithSchool['data']
                for meal in meals:
                    cursor.execute('''
                    REPLACE INTO meal (date, meal_time, calorie, school_code)
                    VALUES (%s, %s, %s, %s)
                    ''', (meal.ymd, meal.meal_time, meal.calorie, school_code))  # school_code는 1로 예시

                    meal_id = cursor.lastrowid

                    for dish in meal.dishes:
                        cursor.execute('''
                        INSERT INTO dish (meal_id, name)
                        VALUES (%s, %s)
                        ''', (meal_id, dish[0]))

                        dish_id = cursor.lastrowid

                        for allergy in dish[1]:
                            cursor.execute('''
                            INSERT INTO dish_allergies (dish_id, allergy)
                            VALUES (%s, %s)
                            ''', (dish_id, allergy))

                    for ingredient_name, origin in meal.origins.items():
                        cursor.execute('''
                        REPLACE INTO ingredient (name, origin)
                        VALUES (%s, %s)
                        ''', (ingredient_name, origin))

                        ingredient_id = cursor.lastrowid

                        cursor.execute('''
                        INSERT INTO meal_ingredients (meal_id, ingredient_id)
                        VALUES (%s, %s)
                        ''', (meal_id, ingredient_id))

                    for nutrient in meal.nutrients:
                        cursor.execute('''
                        INSERT INTO nutrient (meal_id, name, unit, amount)
                        VALUES (%s, %s, %s, %s)
                        ''', (meal_id, nutrient[0], nutrient[1], float(nutrient[2])))

            connection.commit()



if __name__ == '__main__':
    print("Test By fetch_melas.py")