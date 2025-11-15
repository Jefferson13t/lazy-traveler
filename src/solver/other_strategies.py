from datetime import datetime
from src.data_types import HolidayData
from src.solver.pre_processing import haversine2km


def solve_tsp_naive(
    holidays: list[HolidayData],
    start_date: str,
    end_date: str,
    city_coords: dict[str, dict[str, float]]
) -> tuple[list[str], float]:
    """Retorna uma solução simples (não ótima) para o TSP."""

    start_date_formatted = datetime.fromisoformat(start_date).date()
    end_date_formatted = datetime.fromisoformat(end_date).date()

    # Filtra feriados dentro do intervalo
    filtered = [
        h for h in holidays
        if start_date_formatted <= h.date < end_date_formatted
    ]

    # Seleciona exatamente 1 feriado por dia (o primeiro)
    days_sorted = sorted({h.day_of_year for h in filtered})
    holiday_for_day = [
        next(h for h in filtered if h.day_of_year == day)
        for day in days_sorted
    ]

    # Extrai o nome das cidades em ordem
    solution = [h.city_name for h in holiday_for_day]

    # Calcula custo total
    cost = 0.0
    for a, b in zip(solution, solution[1:]):
        cost += haversine2km(
            city_coords[a]["lat"], city_coords[a]["lon"],
            city_coords[b]["lat"], city_coords[b]["lon"]
        )

    return solution, cost

def solve_tsp_greedy(
    holidays: list[HolidayData],
    start_date: str,
    end_date: str,
    city_coords: dict[str, dict[str, float]]
) -> tuple[list[str], float]:
    """Solução gulosa: para cada dia escolhe a cidade com feriado mais próxima da cidade anterior."""

    start_date_formatted = datetime.fromisoformat(start_date).date()
    end_date_formatted = datetime.fromisoformat(end_date).date()

    filtered = [
        h for h in holidays
        if start_date_formatted <= h.date < end_date_formatted
    ]

    days_sorted = sorted({h.day_of_year for h in filtered})

    cities_by_day: dict[int, list[HolidayData]] = {
        day: [h for h in filtered if h.day_of_year == day]
        for day in days_sorted
    }

    solution: list[str] = []
    cost = 0.0


    first_day = days_sorted[0]
    current_city = cities_by_day[first_day][0].city_name
    solution.append(current_city)

    for day in days_sorted[1:]:
        candidate_cities = cities_by_day[day]

        best_city = min(
            candidate_cities,
            key=lambda h: haversine2km(
                city_coords[current_city]["lat"],
                city_coords[current_city]["lon"],
                city_coords[h.city_name]["lat"],
                city_coords[h.city_name]["lon"],
            )
        )

        dist = haversine2km(
            city_coords[current_city]["lat"],
            city_coords[current_city]["lon"],
            city_coords[best_city.city_name]["lat"],
            city_coords[best_city.city_name]["lon"],
        )
        cost += dist

        current_city = best_city.city_name
        solution.append(current_city)

    return solution, cost
