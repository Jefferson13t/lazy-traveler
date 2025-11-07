from src.read_holiday import read_holidays
from src.solution_vizualizer import SolutionVizualizer
from src.naive_solver import solve_tsp_naive

def main() -> None:

    # Reads holidays from a csv file
    holidays = read_holidays('data/feriados_com_pos.csv')

    # Solution Exemple
    solution = solve_tsp_naive(holidays)

    # Displays the solution over time
    solution_vizualizer = SolutionVizualizer()
    solution_vizualizer.draw_travel_schedule(holidays, solution)

if __name__ == "__main__":
    main()
