"""Exports everything the interactive page needs to re-solve the model live in the browser -> output/model.json.
The page contains a JavaScript port of optimize.solve(); this file also embeds the Python base-case result so the
page can be checked against it."""
import json
import config as C
import optimize as O

REF = 0.55 * C.YIELD   # biochar t per wet t at a reference 45% moisture; converts CapEx $/annual t biochar <-> $/annual wet t


def compact(R):
    S = R["summary"]
    return dict(
        npv=S["total_npv"], capex=S["total_capex"], profit=S["annual_profit"], biochar=S["biochar_tons"], credits=S["credits"],
        demand=S["total_demand"],
        sites=[dict(k=r["idx"], size=r["machine_size"], wet=r["wet_tons_in"], dry=r["dry_tons"], bio=r["biochar_tons_out"],
                    cr=r["carbon_credits"], npv=r["npv"], profit=r["annual_profit"], capex=r["capex"],
                    rb=r["biochar_revenue"], rc=r["carbon_credit_revenue"], tip=r["tipping_fee_income"]) for r in R["sites"]],
        wood=[[f["i"], f["k"], f["wet_tons"], f["miles"]] for f in R["wood_flows"]],
        char=[[f["k"], f["j"], f["biochar_tons"], f["miles"]] for f in R["char_flows"]],
    )


def main():
    sup, sites, cus = O.sup, O.sites, O.cus
    down = sup.region == "Downstate"
    defaults = dict(
        biochar_price=C.BIOCHAR_PRICE, credit_price=C.CREDIT_PRICE, tco2_per_credit=C.TCO2_PER_CREDIT,
        co2_per_t=C.CO2_PER_T_BIOCHAR, yield_pct=C.YIELD * 100,
        tip=float(-sup[down].price_per_ton.mean()), residue_price=float(sup[~down].price_per_ton.mean()),
        capex_per_t=C.CAPEX_PER_TPY / REF, capex_fixed_m=C.CAPEX_FIXED / 1e6, opex=C.VAR_OPEX_PER_WET_T,
        rent_fixed_k=C.RENT_FIXED / 1e3, rent_per_t=C.RENT_PER_TPY, rent_factor=float(sites.rent_factor[down.values].mean()),
        truck=C.TRUCK_COST_PER_MILE, wood_payload=C.WOOD_PAYLOAD_T, char_payload=C.BIOCHAR_PAYLOAD_T,
        discount=C.DISCOUNT_RATE * 100, life=C.LIFETIME_YEARS, budget_m=C.BUDGET / 1e6, min_util=C.MIN_UTILIZATION * 100,
        demand_total=float(cus.demand_tpy.sum()), supply_scale=1.0,
    )
    base = compact(O.solve())
    data = dict(
        defaults=defaults, ref=REF, base=base,
        sizes=[dict(name=k, cap=v) for k, v in C.MACHINE_SIZES.items()],
        suppliers=[dict(name=r["name"], region=r.region, lat=r.lat, lon=r.lon, supply=int(r.supply_tpy), moisture=float(r.moisture))
                   for _, r in sup.iterrows()],
        sites=[dict(name=r["name"], lat=r.lat, lon=r.lon, region=sup.region[i]) for i, r in sites.iterrows()],
        customers=[dict(name=r["name"], type=r.type, lat=r.lat, lon=r.lon, demand=float(r.demand_tpy)) for _, r in cus.iterrows()],
        dSS=[[round(float(v), 2) for v in row] for row in O.D_SS], dSC=[[round(float(v), 2) for v in row] for row in O.D_SC],
        lifetime=C.LIFETIME_YEARS,
    )
    json.dump(data, open("output/model.json", "w"), separators=(",", ":"))
    print("wrote output/model.json | base NPV", base["npv"], "| sites", len(base["sites"]))
    print({k: round(v, 3) for k, v in defaults.items()})


if __name__ == "__main__":
    main()
