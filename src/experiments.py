
from solver.solver import solve_tep
from read_holiday import read_holidays
from solver.pre_processing import build_tep_inputs
import pandas as pd

FILE_NAME = 'data/feriados_com_pos.csv'

def experiment_intervals():
    """Roda os experimentos com diferentes intervalos de datas."""
    holidays = read_holidays(FILE_NAME)
    start_date = '2025-03-01'

    end_dates = ['2025-03-10', '2025-03-17', '2025-03-24', '2025-03-31']

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


def main() -> None:

    experiment_intervals()


if __name__ == "__main__":
    main()
