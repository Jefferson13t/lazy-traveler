from src.solution_vizualizer import SolutionVizualizer
from src.solver.other_strategies import solve_tsp_naive, solve_tsp_greedy
from src.solver.solver import solve_tep
from src.read_holiday import read_holidays
from src.solver.pre_processing import build_tep_inputs


def main() -> None:

    # reads holidays
    FILE_NAME = 'data/feriados_com_pos.csv'
    holidays = read_holidays(FILE_NAME)

    # Defines time interval
    start_date = '2025-03-01'
    end_date = '2025-03-24'

    # Prepare problem inputs
    N, T, H, dist, city_coordinates = build_tep_inputs(holidays, start_date, end_date)

    # Solve the problem
    plan, cost = solve_tep(N, T, H, dist)
    plan_naive, cost_naive = solve_tsp_naive(holidays, start_date, end_date, city_coordinates)
    plan_greedy, cost_greedy = solve_tsp_greedy(holidays, start_date, end_date, city_coordinates)

    # Vizualize the solution
    solution_vizualizer = SolutionVizualizer()
    plan_coordinates = [city_coordinates[c].copy() for c in plan]
    plan_coordinates_naive = [city_coordinates[c].copy() for c in plan_naive]
    plan_coordinates_greedy = [city_coordinates[c].copy() for c in plan_greedy]
    solution_vizualizer.draw_travel_schedule(holidays, [
        plan_coordinates, 
        plan_coordinates_naive,
        plan_coordinates_greedy,
    ])

    print("\nChosen city per day:", plan)
    print(f"Total travel cost: {cost:.2f}\n")
    print(f"Total travel cost_naive: {cost_naive:.2f}\n")
    print(f"Total travel cost_greedy: {cost_greedy:.2f}\n")

if __name__ == "__main__":
    main()
