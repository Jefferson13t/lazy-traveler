
import math
import pandas as pd

import gurobipy as gp
from gurobipy import GRB

def haversine2km(lat1, lon1, lat2, lon2):
    """
    Distancia entre 2 coordenadas geográficas usando a fórmula de Haversine.
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    r = 6371
    return c * r


def build_tep_inputs(df: pd.DataFrame):
    df = df.copy()
    df['data'] = pd.to_datetime(df['data']).dt.date

    # Sets
    dates_sorted = sorted(df['data'].unique())
    T = list(range(len(dates_sorted)))
    date_to_t = {d: t for t, d in enumerate(dates_sorted)}

    N = sorted(df['cidade_uf'].unique())

    holidays = {(i, t): 0 for i in N for t in T}
    for _, row in df[['cidade_uf', 'data']].drop_duplicates().iterrows():
        i = row['cidade_uf']
        t = date_to_t[row['data']]
        holidays[(i, t)] = 1

    city_coords = (
        df[["cidade_uf", "lat", "lon"]]
        .drop_duplicates("cidade_uf")
        .set_index("cidade_uf")[["lat", "lon"]]
        .to_dict(orient="index")
    )
    distances = {}
    for i in N:
        lat_i, lon_i = city_coords[i]["lat"], city_coords[i]["lon"]
        for j in N:
            lat_j, lon_j = city_coords[j]["lat"], city_coords[j]["lon"]
            distances[(i, j)] = 0.0 if i == j else haversine2km(lat_i, lon_i, lat_j, lon_j)

    meta = {'cities': N, 'dates': dates_sorted}
    return N, T, holidays, distances, meta



def solve_tep(N, T, holidays, distances):
    with gp.Env() as env, gp.Model(env=env) as m:
        x = m.addVars(((i, t) for i in N for t in T), vtype=GRB.BINARY, name="x")
        y = m.addVars(((i, j, t) for i in N for j in N for t in T[:-1]),
                          vtype=GRB.BINARY, name="y")
        
        m.setObjective(gp.quicksum(distances[i, j] * y[i, j, t] for i in N for j in N for t in T[:-1]), GRB.MINIMIZE)

        for t in T:
            m.addConstr(gp.quicksum(x[i, t] for i in N) == 1, name=f"one_city_day[{t}]")

        for i in N:
            for t in T:
                # If H=0, force x=0; if H=1, just allow it
                if holidays[i, t] == 0:
                    m.addConstr(x[i, t] == 0, name=f"holiday_block[{i},{t}]")
        
        # Movement consistency (depart at t)
        for i in N:
            for t in T[:-1]:
                m.addConstr(gp.quicksum(y[i, j, t] for j in N) == x[i, t],
                            name=f"depart[{i},{t}]")

        # Movement consistency (arrive at t+1)
        for j in N:
            for t in T[:-1]:
                m.addConstr(gp.quicksum(y[i, j, t] for i in N) == x[j, t+1],
                            name=f"arrive[{j},{t+1}]")
                
        for i in N:
            for j in N:
                for t in T[:-1]:
                    if holidays[i, t] == 0 or holidays[j, t+1] == 0:
                        m.addConstr(y[i, j, t] == 0, name=f"block_arc[{i},{j},{t}]")
                
        m.optimize()

        if m.Status not in (GRB.OPTIMAL, GRB.TIME_LIMIT):
            raise RuntimeError(f"MIP ended with status {m.Status}")

        chosen = []
        for t in T:
            chosen_city = max(N, key=lambda i: x[i, t].X)
            chosen.append(chosen_city)

        return chosen, m.ObjVal


if __name__ == "__main__":
    # Example: 5 cities x 5 days, like the slide example
    # C, D, H, dist = generate_demo(n_cities=5, n_days=5, seed=7, ensure_daily_feasibility=True)
    df = pd.read_csv('data/feriados_com_pos.csv')
    df['data'] = pd.to_datetime(df['data'])
    start_date = '2025-03-01'
    end_date = '2025-03-25'

    filtered_df = df[(df['data'] >= start_date) & (df['data'] < end_date)]


    C, D, H, dist, meta = build_tep_inputs(filtered_df)

    plan, cost = solve_tep(C, D, H, dist)

    print("\nChosen city per day:", plan)
    print(f"Total travel cost: {cost:.2f}\n")
