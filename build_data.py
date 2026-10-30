"""Builds suppliers.csv, sites.csv, customers.csv from real NY coordinates.
Downstate suppliers: NYS DEC Solid Waste Management Facilities (data.ny.gov 2fni-raj8).
Upstate sawmills: NYS DEC Directory of Primary Wood-Using Industry (2017), geocoded via OSM Nominatim.
Customers: NYS DEC facility data / OpenStreetMap. Supply, moisture and prices are ASSUMPTIONS (see config.py)."""
import pandas as pd
import config as C

# name, region, lat, lon, supply wet t/yr, moisture, $/wet t (negative = tipping fee received), source
S = [
 ("DSNY Fresh Kills Composting Facility", "Downstate", 40.58586, -74.19319, 60000, 0.45, -35, "NYS DEC SWM Facilities"),
 ("Garden City Compost", "Downstate", 40.72178, -73.64408, 25000, 0.45, -35, "NYS DEC SWM Facilities"),
 ("Omni Recycling of Babylon", "Downstate", 40.73080, -73.39634, 35000, 0.40, -35, "NYS DEC SWM Facilities"),
 ("Carlsoncorp Kings Park", "Downstate", 40.87867, -73.28367, 30000, 0.40, -35, "NYS DEC SWM Facilities"),
 ("Long Island Compost Farm #36", "Downstate", 40.85226, -72.83329, 25000, 0.45, -35, "NYS DEC SWM Facilities"),
 ("Wagner Lumber Co. (Owego)", "Upstate", 42.12990, -76.18422, 18000, 0.50, 10, "DEC Wood Directory 2017"),
 ("Gutchess Lumber Co. (Cortland)", "Upstate", 42.58205, -76.21390, 18000, 0.50, 10, "DEC Wood Directory 2017"),
 ("Gutchess Freedom", "Upstate", 42.46678, -78.38494, 18000, 0.50, 10, "DEC Wood Directory 2017"),
 ("Ward Lumber Co. (Jay)", "Upstate", 44.36617, -73.72421, 13500, 0.50, 10, "DEC Wood Directory 2017"),
 ("Peter C. Herman Inc. (Marion)", "Upstate", 43.14956, -77.12458, 11700, 0.50, 10, "DEC Wood Directory 2017"),
]
sup = pd.DataFrame(S, columns=["name","region","lat","lon","supply_tpy","moisture","price_per_ton","source"])
sup.insert(0, "id", [f"S{i+1}" for i in range(len(sup))])
sup[["id","name","region","lat","lon","supply_tpy","moisture","price_per_ton","source"]].to_csv("data/suppliers.csv", index=False)

sites = sup[["id","name","lat","lon"]].copy()
sites["id"] = [f"K{i+1}" for i in range(len(sites))]
sites["colocated_supplier"] = sup["id"].values
sites["rent_factor"] = sup["region"].map({"Downstate": 1.5, "Upstate": 1.0})  # ASSUMPTION: downstate land costs more
sites.to_csv("data/sites.csv", index=False)

# name, type, lat, lon, demand t/yr, price
K = [
 ("Long Island Compost - Grucci Lane (Yaphank)", "Compost/Soil", 40.80158, -72.92632, 2500),
 ("C.J. Krantz Organic Recycling Center (Amherst)", "Compost/Soil", 43.05410, -78.72069, 2000),
 ("Vermi-Green LLC (Palmyra)", "Compost/Soil", 43.03793, -77.25640, 1500),
 ("Hurds Farm Compost (Clintondale)", "Compost/Soil", 41.70516, -74.06534, 1500),
 ("Montrose Water Treatment Plant (Westchester)", "Water Filtration", 41.29994, -73.88404, 1000),
 ("Syracuse Water Treatment Plant (Skaneateles Lake)", "Water Filtration", 42.94556, -76.43073, 1200),
 ("Michael C. O'Laughlin Water Plant (Niagara Falls)", "Water Filtration", 43.07615, -78.99844, 1000),
 ("Home Depot Distribution Center (Montgomery)", "Retail Garden Hub", 41.49622, -74.24280, 1800),
 ("Hicks Nurseries (Westbury)", "Retail Garden Hub", 40.76322, -73.59735, 800),
 ("Eastman Business Park / Li-Cycle (Rochester)", "Battery/Industrial", 43.20214, -77.62816, 1200),
 # Added so plants near New York City have buyers within a 50-mile haul. Locations: NYS DEC SWM Facilities (composters) and
 # OpenStreetMap Nominatim; demand is an ASSUMPTION (commercial composters 600-1,200 t, community farm / nursery sites 50-100 t).
 ("Gedney Composting and Recycling (White Plains)", "Compost/Soil", 41.01378, -73.75722, 1200),
 ("Organic Recycling Inc (Tappan)", "Compost/Soil", 41.03461, -73.94716, 800),
 ("Sustainable Materials Management (Cortlandt Manor)", "Compost/Soil", 41.29802, -73.94663, 800),
 ("Bistrian Materials / Calverton Materials (Calverton)", "Compost/Soil", 40.92778, -72.76002, 1200),
 ("Sky Materials Corp. (Calverton)", "Compost/Soil", 40.92683, -72.77408, 800),
 ("Rockland County Co-Composting Facility (Hillburn)", "Compost/Soil", 41.14754, -74.15334, 800),
 ("Clear Flo Technologies (Lindenhurst)", "Compost/Soil", 40.71658, -73.39818, 600),
 ("Queens Botanical Garden Farm & Compost Site (Flushing)", "Urban Agriculture", 40.75157, -73.82612, 100),
 ("Brooklyn Grange (Brooklyn Navy Yard)", "Urban Agriculture", 40.69854, -73.97228, 50),
 ("NYC Parks Greenbelt Native Plant Center (Staten Island)", "Municipal Nursery", 40.59646, -74.18139, 100),
]
cus = pd.DataFrame(K, columns=["name","type","lat","lon","demand_tpy"])
cus.insert(0, "id", [f"C{i+1}" for i in range(len(cus))])
cus["demand_tpy"] = (cus.demand_tpy * C.DEMAND_SCALE / 50).round() * 50   # ASSUMPTION: scaled demand
cus["price_per_ton"] = C.BIOCHAR_PRICE
cus.to_csv("data/customers.csv", index=False)
print(sup.iloc[:, :8].to_string()); print(sites.to_string()); print(cus.to_string())
