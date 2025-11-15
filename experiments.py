
from src.solver.solver import solve_tep
from src.read_holiday import read_holidays
from src.solver.pre_processing import build_tep_inputs
import pandas as pd
import matplotlib.pyplot as plt
import random

FILE_NAME = 'data/feriados_com_pos.csv'


def experiment_intervals():
    """Roda os experimentos com diferentes intervalos de datas."""
    holidays = read_holidays(FILE_NAME)
    start_date = '2025-03-01'

    end_dates = ['2025-03-05', '2025-03-06', '2025-03-07', '2025-03-08', '2025-03-09']

    results = {'date_interval': [], 'plan': [], 'stats': [], 'time': [], 'cost': []}
    for date in end_dates:
        print(f"Experiment for interval {start_date} to {date}")

        N, T, H, dist, city_coordinates = build_tep_inputs(holidays, start_date, date)
        plan, stats = solve_tep(N, T, H, dist)

        results['date_interval'].append((start_date, date))
        results['plan'].append(plan)
        results['stats'].append(stats)
        results['time'].append(stats['runtime_s'])
        results['cost'].append(stats['obj_val'])

    df = pd.DataFrame(results)
    df.to_csv('experiment_intervals_results.csv', index=False)

def restrict_instance(N_selected, T, H_full, dist_full, city_coordinates_full):
    """Restringe H, dist e coordenadas a um subconjunto de cidades."""
    N_selected = list(N_selected)

    H = {(i, t): H_full[i, t] for i in N_selected for t in T}
    dist = {(i, j): dist_full[i, j] for i in N_selected for j in N_selected}
    city_coordinates = {i: city_coordinates_full[i] for i in N_selected}

    return N_selected, T, H, dist, city_coordinates

def rank_cities_by_holidays(N, T, H):
    """Ordena cidades por número de feriados no intervalo (maior primeiro)."""
    scores = {i: sum(H[i, t] for t in T) for i in N}
    return sorted(N, key=lambda i: scores[i], reverse=True)

def experiment_cities():
    """Roda experimentos variando o número de cidades."""
    holidays = read_holidays(FILE_NAME)

    start_date = "2025-03-01"
    end_date   = "2025-03-09"

    N_full, T, H_full, dist_full, city_coordinates_full = build_tep_inputs(
        holidays, start_date, end_date
    )

    plan_full, stats_full = solve_tep(N_full, T, H_full, dist_full)
    base_cities = sorted(set(plan_full))  # conjunto que cobre os dias
    print("Base cities:", base_cities)

    ordered_by_holidays = rank_cities_by_holidays(N_full, T, H_full)
    extra_cities = [c for c in ordered_by_holidays if c not in base_cities]

    sizes_to_test = [len(base_cities) + k for k in range(0, len(extra_cities) + 1, 5)]
    print(sizes_to_test)

    results = {
        "date_interval": [],
        "num_cities": [],
        "plan": [],
        "time": [],
        "cost": [],
        "stats": [],
    }

    for k in sizes_to_test:
        N_k = base_cities + extra_cities[: max(0, k - len(base_cities))]
        print(f"Experiment with {len(N_k)} cities")

        N_sub, T_sub, H_sub, dist_sub, coord_sub = restrict_instance(
            N_k, T, H_full, dist_full, city_coordinates_full
        )

        plan, stats = solve_tep(N_sub, T_sub, H_sub, dist_sub)

        results['date_interval'].append((start_date, end_date))
        results["num_cities"].append(len(N_k))
        results["plan"].append(plan)
        results["time"].append(stats["runtime_s"])
        results["cost"].append(stats["obj_val"])
        results["stats"].append(stats)

    df = pd.DataFrame(results)
    df.to_csv("experiment_cities_results.csv", index=False)
    return df

def main() -> None:

    # experiment_intervals()

    # df_time = pd.read_csv('experiment_intervals_results.csv')

    # def interval_to_midpoint(interval_str):
    #     start, end = interval_str.strip("()").replace("'", "").split(", ")
    #     return (pd.to_datetime(end) - pd.to_datetime(start)).days

    # plt.figure(figsize=(10, 6))
    # plt.plot(df_time['date_interval'].apply(interval_to_midpoint), df_time['time'], marker='o')
    # plt.title('Runtime vs Date Interval')
    # plt.xlabel('Date Interval')
    # plt.ylabel('Runtime (s)')
    # plt.grid(True)
    # plt.savefig('runtime_vs_date_interval.png')
    # plt.show()

    # experiment_cities()

    df_cities = pd.read_csv('experiment_cities_results.csv')
    plt.figure(figsize=(10, 6))
    plt.plot(df_cities['num_cities'], df_cities['time'], marker='o')
    plt.title('Runtime vs Number of Cities')
    plt.xlabel('Number of Cities')
    plt.ylabel('Runtime (s)')
    plt.grid(True)
    plt.savefig('runtime_vs_num_cities.png')
    plt.show()

if __name__ == "__main__":
    main()
