import csv
from datetime import datetime
from src.data_types import HolidayData

def parse_row(row: list[str]) -> HolidayData:
    return HolidayData(
        uf=row[0],
        holiday=row[1],
        name=row[2],
        note=row[3] or '',
        date=datetime.strptime(row[4], "%Y-%m-%d").date(),
        city_name=row[5],
        lat=float(row[6]),
        lon=float(row[7]),
    )

def read_holidays(filename: str) -> list[HolidayData]:
    holidays = []

    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)
        for row in reader:
            if len(row) < 8 or row[0].lower() == "uf":
                continue
            holidays.append(parse_row(row))

    return holidays
