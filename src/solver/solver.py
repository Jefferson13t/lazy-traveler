
import gurobipy as gp
from gurobipy import GRB, Model

# Contraints
def one_city_day_constraint(model: Model, x, T, N) -> None:
    for time in T:
        model.addConstr(gp.quicksum(x[city, time] for city in N) == 1, name=f"one_city_day[{time}]")

def holiday_block_constraint(model: Model, x, T, N, holidays) -> None:
    for city in N:
            for time in T:
                model.addConstr(x[city, time] <= holidays[city, time])

def time_movement_consistency_departure_constraint(model: Model, x, y, T, N) -> None:
    for city in N:
        for time in T[:-1]:
            model.addConstr(gp.quicksum(y[city, j, time] for j in N) == x[city, time],
                        name=f"depart[{city},{time}]")
            
def time_movement_consistency_arrival_constraint(model: Model, x, y, T, N) -> None:
    for city in N:
        for time in T[:-1]:
            model.addConstr(gp.quicksum(y[i, city, time] for i in N) == x[city, time + 1],
                        name=f"arrive[{city},{time + 1}]")
            
def block_arc_constraint(model: Model, y, T, N, holidays) -> None:
    for departure_city in N:
            for arrival_city in N:
                for time in T[:-1]:
                    if holidays[departure_city, time] == 0 or holidays[arrival_city, time + 1] == 0:
                        model.addConstr(y[departure_city, arrival_city, time] == 0, name=f"block_arc[{departure_city},{arrival_city},{time}]")
           
def solve_tep(N, T, holidays, distances) -> tuple[list[str], float]:
    with gp.Env() as env, gp.Model(env=env) as model:
        model.setParam("MemLimit", 6) 
        model.setParam('TimeLimit', 600)
        x = model.addVars(((i, t) for i in N for t in T), vtype = GRB.BINARY, name="x")
        y = model.addVars(((i, j, t) for i in N for j in N for t in T[:-1]),
                          vtype=GRB.BINARY, name="y")
        
        model.setObjective(gp.quicksum(distances[i, j] * y[i, j, t] for i in N for j in N for t in T[:-1]), GRB.MINIMIZE)

        # Adds problem constraints
        one_city_day_constraint(model, x, T, N)
        holiday_block_constraint(model, x, T, N, holidays) 
        time_movement_consistency_departure_constraint(model, x, y, T, N)
        time_movement_consistency_arrival_constraint(model, x, y, T, N)
        block_arc_constraint(model, y, T, N, holidays) 
                
        model.optimize()

        if model.Status not in (GRB.OPTIMAL, GRB.TIME_LIMIT):
            raise RuntimeError(f"MIP ended with status {model.Status}")

        chosen = []
        for t in T:
            chosen_city = max(N, key=lambda i: x[i, t].X)
            chosen.append(chosen_city)

        runtime = model.Runtime
        obj_val = model.ObjVal
        mip_gap_final = None
        try:
            mip_gap_final = model.MIPGap
        except gp.GurobiError:
            pass

        num_vars = model.NumVars
        num_bin_vars = sum(1 for v in model.getVars() if v.VType == GRB.BINARY)
        num_constrs = model.NumConstrs
        node_count = model.NodeCount

        # Número de movimentos (mudança de cidade)
        num_moves = 0
        for idx in range(1, len(T)):
            if chosen[idx] != chosen[idx - 1]:
                num_moves += 1

        stats  = {
            "n_cities": len(N),
            "n_days": len(T),
            "obj_val": obj_val,
            "runtime_s": runtime,
            "mip_gap": mip_gap_final,
            "num_vars": num_vars,
            "num_bin_vars": num_bin_vars,
            "num_constrs": num_constrs,
            "node_count": node_count,
            "num_moves": num_moves,
            "plan": chosen,
        }

        model.dispose()
        env.dispose()

        return chosen, stats

