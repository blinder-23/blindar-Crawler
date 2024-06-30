
def check_args(year: int, month: int):
    if not (2018 <= year <= 2025):
        print(
            f'Error: year must be between 2018 to 2024 inclusive, but {year} given')
        exit(1)
    if not (1 <= month <= 12):
        print(
            f'Error: month must be between 1 to 12 inclusive, but {month} given')
        exit(1)


def check_args_range(start_year: int, start_month: int, end_year: int, end_month: int):
    if not (2018 <= start_year <= 2025):
        print(
            f'Error: start_year must be between 2018 to 2024 inclusive, but {start_year} given')
        exit(1)
    if not (1 <= start_month <= 12):
        print(
            f'Error: start_month must be between 1 to 12 inclusive, but {start_month} given')
        exit(1)
    if not (2018 <= end_year <= 2025):
        print(
            f'Error: end_year must be between 2018 to 2024 inclusive, but {end_year} given')
        exit(1)
    if not (1 <= end_month <= 12):
        print(
            f'Error: end_month must be between 1 to 12 inclusive, but {end_month} given')
        exit(1)
    if (start_year, start_month) > (end_year, end_month):
        print(
            f'Error: start_year-month must be less than or equal to end_year-month, but {start_year}-{start_month} > {end_year}-{end_month} given')
        exit(1)
