from typing import TypeAlias
from dataclasses import dataclass
from datetime import date

# Defines a class that represents each row on the csv file
@dataclass
class HolidayData:
    uf: str
    holiday: str
    name: str
    note: str
    date: date
    city_name: str
    lat: float
    lon: float

    @property
    def day_of_year(self) -> int:
        """Returns the index of the day on the year (1–365/366)."""
        return self.date.timetuple().tm_yday

# # Defines a solution as a list of indexes of the visited cities 
# # Solution: TypeAlias = list[int]
# Solution: TypeAlias = list[dict[str, float]]


