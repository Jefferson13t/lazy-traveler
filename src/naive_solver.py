from src.data_types import Solution, HolidayData

def solve_tsp_naive(holidays: list[HolidayData]) -> Solution:
    '''Returns a valid (but not optimal) solution to the TSP problem.'''

    holiday_with_index: list[tuple[int, HolidayData]] = []

    for index, holiday in enumerate(holidays):
        holiday_with_index.append((index, holiday))

    solution: Solution = []

    holiday_for_day = []
    for day in sorted({h[1].day_of_year for h in holiday_with_index}):
        cities = [h for h in holiday_with_index if h[1].day_of_year == day]
        if cities:
            holiday_for_day.append(cities[0])

    for i in range(len(holiday_for_day) - 1):
        solution.append(holiday_for_day[i][0])

    return solution
