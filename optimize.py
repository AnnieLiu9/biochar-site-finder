"""Site Economic & Spatial Optimization Engine: reads the 3 CSVs, solves a MILP (Pyomo + HiGHS).
`solve()` can override the main commercial assumptions so the same model serves the scenario explorer.
Running this file solves the base case and writes output/results.json and output/*.csv."""
import json, math, os
import numpy as np, pandas as pd, requests
import pyomo.environ as pyo
import config as C

KM_TO_MI = 0.621371
sup = pd.read_csv("data/suppliers.csv")
sites = pd.read_csv("data/sites.csv")
cus = pd.read_csv("data/customers.csv")


def haversine_km(a, b):
    R = 6371.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dphi, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))


def osrm_matrix(src, dst):
    """Road distance (km) src x dst via the public OSRM server; falls back to haversine*1.3."""
    pts = list(src) + list(dst)
    coords = ";".join(f"{lon:.5f},{lat:.5f}" for lat, lon in pts)
    url = (f"https://router.project-osrm.org/table/v1/driving/{coords}?annotations=distance"
           f"&sources={';'.join(map(str, range(len(src))))}"
           f"&destinations={';'.join(str(len(src) + j) for j in range(len(dst)))}")
    try:
        r = requests.get(url, timeout=60, headers={"User-Agent": "biochar-site-finder-prototype/0.1"}).json()
        m = np.array(r["distances"], dtype=float) / 1000.0
        if np.isnan(m).any():
            raise ValueError("null distances")
        return m, "OSRM road distance"
    except Exception as e:
        print("OSRM unavailable, using haversine*1.3:", e)
        return np.array([[haversine_km(a, b) * 1.3 for b in dst] for a in src]), "haversine x1.3 (fallback)"


def get_distances():
    cache = "data/distances.json"
    if os.path.exists(cache):
        d = json.load(open(cache))
        return np.array(d["sup_site"]), np.array(d["site_cus"]), d["method"]
    s = list(zip(sup.lat, sup.lon))
    k = list(zip(sites.lat, sites.lon))
    c = list(zip(cus.lat, cus.lon))
    d1, m1 = osrm_matrix(s, k)
    d2, m2 = osrm_matrix(k, c)
    method = m1 if m1 == m2 else "mixed"
    json.dump({"sup_site": d1.tolist(), "site_cus": d2.tolist(), "method": method}, open(cache, "w"))
    return d1, d2, method


_D_SS, _D_SC, _METHOD = get_distances()
D_SS, D_SC = _D_SS * KM_TO_MI, _D_SC * KM_TO_MI  # miles
RAW_DEMAND = cus.demand_tpy.values / C.DEMAND_SCALE   # demand before the DEMAND_SCALE assumption


def solve(credit_price=None, tco2_per_credit=None, biochar_price=None, demand_scale=None, budget=None, verbose=False):
    """Solve the siting MILP. Overrides default to config.py / customers.csv values."""
    credit_price = C.CREDIT_PRICE if credit_price is None else credit_price
    tco2_per_credit = C.TCO2_PER_CREDIT if tco2_per_credit is None else tco2_per_credit
    budget = C.BUDGET if budget is None else budget
    price = np.full(len(cus), biochar_price, dtype=float) if biochar_price is not None else cus.price_per_ton.values.astype(float)
    demand = cus.demand_tpy.values.astype(float) if demand_scale is None else np.round(RAW_DEMAND * demand_scale / 50) * 50

    t_wood = D_SS * C.TRUCK_COST_PER_MILE / C.WOOD_PAYLOAD_T      # $ per wet ton delivered
    t_char = D_SC * C.TRUCK_COST_PER_MILE / C.BIOCHAR_PAYLOAD_T   # $ per biochar ton delivered
    credits_per_t = C.CO2_PER_T_BIOCHAR / tco2_per_credit
    credit_per_t = credits_per_t * credit_price                    # $ per t biochar
    conv = (1 - sup.moisture.values) * C.YIELD                     # biochar t per wet t, by supplier

    I, K, J = range(len(sup)), range(len(sites)), range(len(cus))
    m = pyo.ConcreteModel()
    m.x = pyo.Var(I, K, domain=pyo.NonNegativeReals)   # wet tons supplier -> site
    m.z = pyo.Var(K, J, domain=pyo.NonNegativeReals)   # biochar tons site -> customer
    SZ = list(C.MACHINE_SIZES)
    m.y = pyo.Var(K, SZ, domain=pyo.Binary)            # open site k with machine size s
    m.one = pyo.Constraint(K, rule=lambda m, k: sum(m.y[k, s] for s in SZ) <= 1)
    capex_s = {s: C.CAPEX_FIXED + C.CAPEX_PER_TPY * C.MACHINE_SIZES[s] for s in SZ}
    rent = lambda k, s: (C.RENT_FIXED + C.RENT_PER_TPY * C.MACHINE_SIZES[s]) * sites.rent_factor[k]
    cap_k = lambda k: sum(C.MACHINE_SIZES[s] * m.y[k, s] for s in SZ)
    wet_in = lambda k: sum(m.x[i, k] for i in I)

    m.supply = pyo.Constraint(I, rule=lambda m, i: sum(m.x[i, k] for k in K) <= sup.supply_tpy[i])
    m.capc = pyo.Constraint(K, rule=lambda m, k: wet_in(k) <= cap_k(k))
    m.minu = pyo.Constraint(K, rule=lambda m, k: wet_in(k) >= C.MIN_UTILIZATION * cap_k(k))
    m.bal = pyo.Constraint(K, rule=lambda m, k: sum(m.z[k, j] for j in J) == sum(m.x[i, k] * conv[i] for i in I))
    m.dem = pyo.Constraint(J, rule=lambda m, j: sum(m.z[k, j] for k in K) <= demand[j])
    m.budget = pyo.Constraint(expr=sum(capex_s[s] * m.y[k, s] for k in K for s in SZ) <= budget)

    rev = sum(m.z[k, j] * (price[j] + credit_per_t) for k in K for j in J)
    wood = sum(m.x[i, k] * (sup.price_per_ton[i] + t_wood[i, k] + C.VAR_OPEX_PER_WET_T) for i in I for k in K)
    char = sum(m.z[k, j] * t_char[k, j] for k in K for j in J)
    rent_cost = sum(rent(k, s) * m.y[k, s] for k in K for s in SZ)
    m.obj = pyo.Objective(expr=C.ANNUITY * (rev - wood - char - rent_cost)
                          - sum(capex_s[s] * m.y[k, s] for k in K for s in SZ), sense=pyo.maximize)

    res = pyo.SolverFactory("appsi_highs").solve(m)
    if verbose:
        print("Solver:", res.solver.termination_condition, "| distances:", _METHOD)

    X = np.array([[pyo.value(m.x[i, k]) for k in K] for i in I])
    Z = np.array([[pyo.value(m.z[k, j]) for j in J] for k in K])
    size_of = {k: s for k in K for s in SZ if pyo.value(m.y[k, s]) > 0.5}

    site_rows, wood_flows, char_flows = [], [], []
    for k in size_of:
        sz = size_of[k]
        cap = C.MACHINE_SIZES[sz]
        wet, bio = X[:, k].sum(), Z[k].sum()
        tip = sum(-X[i, k] * min(sup.price_per_ton[i], 0) for i in I)       # tipping fees received
        buy = sum(X[i, k] * max(sup.price_per_ton[i], 0) for i in I)        # wood purchase
        trk = sum(X[i, k] * t_wood[i, k] for i in I) + sum(Z[k, j] * t_char[k, j] for j in J)
        opex = wet * C.VAR_OPEX_PER_WET_T + rent(k, sz)
        sales = sum(Z[k, j] * price[j] for j in J)
        credits = bio * credits_per_t
        cred_rev = credits * credit_price
        profit = sales + cred_rev + tip - buy - trk - opex
        npv = C.ANNUITY * profit - capex_s[sz]
        site_rows.append(dict(
            idx=int(k), site_id=sites.id[k], site=sites.name[k], lat=sites.lat[k], lon=sites.lon[k],
            machine_size=sz, capacity_tpy=cap, wet_tons_in=round(wet),
            dry_tons=round(sum(X[i, k] * (1 - sup.moisture[i]) for i in I)),
            biochar_tons_out=round(bio), carbon_credits=round(credits),
            biochar_revenue=round(sales), carbon_credit_revenue=round(cred_rev), tipping_fee_income=round(tip),
            wood_purchase_cost=round(buy), trucking_cost=round(trk), opex_rent=round(opex),
            annual_profit=round(profit), capex=round(capex_s[sz]), npv=round(npv)))
        for i in I:
            if X[i, k] > 1:
                wood_flows.append(dict(i=int(i), k=int(k), supplier=sup.name[i], site=sites.name[k], wet_tons=round(X[i, k]),
                                       miles=round(D_SS[i, k]), s_lat=sup.lat[i], s_lon=sup.lon[i], k_lat=sites.lat[k], k_lon=sites.lon[k]))
        for j in J:
            if Z[k, j] > 1:
                char_flows.append(dict(k=int(k), j=int(j), site=sites.name[k], customer=cus.name[j], biochar_tons=round(Z[k, j]),
                                       miles=round(D_SC[k, j]), k_lat=sites.lat[k], k_lon=sites.lon[k], c_lat=cus.lat[j], c_lon=cus.lon[j]))
    summary = dict(total_npv=round(pyo.value(m.obj)), total_capex=sum(r["capex"] for r in site_rows),
                   annual_profit=sum(r["annual_profit"] for r in site_rows),
                   biochar_tons=sum(r["biochar_tons_out"] for r in site_rows), credits=sum(r["carbon_credits"] for r in site_rows),
                   total_demand=int(demand.sum()), distance_method=_METHOD,
                   sites_opened=[r["site"] for r in site_rows])
    return dict(summary=summary, sites=site_rows, wood_flows=wood_flows, char_flows=char_flows)


def main():
    R = solve(verbose=True)
    pd.DataFrame(R["sites"]).to_csv("output/selected_sites.csv", index=False)
    pd.DataFrame(R["wood_flows"]).to_csv("output/wood_flows.csv", index=False)
    pd.DataFrame(R["char_flows"]).to_csv("output/biochar_flows.csv", index=False)
    json.dump(R, open("output/results.json", "w"), indent=1)

    S = R["summary"]
    pd.set_option("display.width", 220)
    print("\nSITES TO OPEN:", len(R["sites"]))
    print(pd.DataFrame(R["sites"])[["site", "machine_size", "wet_tons_in", "biochar_tons_out", "carbon_credits",
                                    "annual_profit", "capex", "npv"]].to_string(index=False))
    print("\nTOTAL NPV $%s | CAPEX $%s | annual profit $%s" % (
        f"{S['total_npv']:,}", f"{S['total_capex']:,}", f"{S['annual_profit']:,}"))
    print("\nWOOD IN:")
    print(pd.DataFrame(R["wood_flows"])[["supplier", "site", "wet_tons", "miles"]].to_string(index=False))
    print("\nBIOCHAR OUT:")
    print(pd.DataFrame(R["char_flows"])[["site", "customer", "biochar_tons", "miles"]].to_string(index=False))


if __name__ == "__main__":
    main()
