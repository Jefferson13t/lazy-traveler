from src.data_types import HolidayData
from datetime import datetime
from typing import List, Tuple
import math


def haversine2km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Distancia entre 2 coordenadas geográficas usando a fórmula de Haversine.
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    r = 6371
    return c * r

def build_tep_inputs(
    holidays: List[HolidayData],
    start_date: str,
    end_date: str,
) -> Tuple[list, list[int], dict[tuple[str, int], int], dict[tuple[str, str], float], dict]:

    start_date_formatted = datetime.fromisoformat(start_date).date()
    end_date_formatted = datetime.fromisoformat(end_date).date()

    filtered = [
        h for h in holidays
        if start_date_formatted <= h.date < end_date_formatted
    ]

    # 2. Conjunto de datas ordenadas
    dates_sorted = sorted({h.date for h in filtered})
    T = list(range(len(dates_sorted)))
    date_to_t = {d: t for t, d in enumerate(dates_sorted)}

    # 3. Conjunto de cidades
    N = sorted({h.city_name for h in filtered})

    # 4. Mapa de feriado por (cidade, tempo): 0/1
    holidays_map = {(city, t): 0 for city in N for t in T}
    for h in filtered:
        t = date_to_t[h.date]
        holidays_map[(h.city_name, t)] = 1

    # 5. Coordenadas das cidades
    city_coords = {}
    for h in filtered:
        # Se a cidade já foi registrada, ignore
        if h.city_name not in city_coords:
            city_coords[h.city_name] = {
                "name": h.city_name,
                "lat": h.lat, 
                "lon": h.lon
            }

    # 6. Distâncias haversine entre todas as cidades
    distances = {
        (i, j): (
            0.0 if i == j else haversine2km(
                city_coords[i]["lat"], city_coords[i]["lon"],
                city_coords[j]["lat"], city_coords[j]["lon"]
            )
        )
        for i in N
        for j in N
    }

    # # Metadados
    # meta = {"cities": N, "dates": dates_sorted}

    return N, T, holidays_map, distances, city_coords