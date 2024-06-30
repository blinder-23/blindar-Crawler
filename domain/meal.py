from dataclasses import dataclass
from sqlite3 import Date


@dataclass
class Meal:
    ymd: str  # YYYYMMD
    dishes: list  # list of (식단, 알레르기)
    origins: dict  # dict of (원재료: 원산지)
    nutrients: list  # list of (영양소 이름, 단위, 양)
    calorie: float
    meal_time: str

   