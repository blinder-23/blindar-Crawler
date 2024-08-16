from sqlite3 import Cursor
import pymysql
import os
from domain.meal import Meal
from Logger import myLogger

LOG_FILE = '../log/db.log'

logger = myLogger.set_logger(LOG_FILE)


def start_mysql():
    os.system('./scripts/start_mysql.sh')


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


def create_schedule_table_if_not_exists(cursor):

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedule (
                school_code INT NOT NULL,
                id VARCHAR(50) NOT NULL,
                date DATE NOT NULL,
                title VARCHAR(50) NOT NULL,
                contents VARCHAR(255),
                PRIMARY KEY (id, date)
            );
    ''')

    cursor.execute('''
        alter table schedule convert to charset utf8;
    ''')


def insert_schedules(schedules: list, year: int, month: int):
    # start_mysql()
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                create_and_use_database(cursor)
                create_schedule_table_if_not_exists(cursor)

                insert_sql = 'REPLACE INTO schedule (school_code,id,date,title, contents) VALUES (%s,%s, %s, %s, %s)'
                inserted = 0
                for schedule in schedules:
                    inserted += cursor.execute(insert_sql,
                                               (schedule.school_code, schedule.id, schedule.date, schedule.title, schedule.contents))
            connection.commit()
        logger.info(
            f'🗄️ {inserted} schedules of {year}-{month} inserted to db')
    except Exception as e:
        logger.warning(
            f'🚨Error occured while inserting schedules to {year}-{month} error: {e}')







