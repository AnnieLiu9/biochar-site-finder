# Data sources

The coordinates and names in `build_data.py` were collected from the sources below. The raw downloads (not committed) were only
used to pick and verify locations; the pipeline reads `data/*.csv`.

| Data | Source |
|---|---|
| Downstate wood / compost yards (5 suppliers) and compost buyers | NYS DEC Solid Waste Management Facilities, data.ny.gov dataset `2fni-raj8` (CSV export, `Georeference` column = lat/lon) |
| Upstate sawmills (5 suppliers) | NYS DEC Directory of Primary Wood-Using Industry (2017), https://dec.ny.gov/docs/lands_forests_pdf/directory17.pdf - largest mills with street addresses; geocoded with OpenStreetMap Nominatim |
| Added New York City-area buyers (7 composters: Gedney, Organic Recycling, Sustainable Materials Management, Bistrian / Calverton Materials, Sky Materials, Rockland County co-composting, Clear Flo; Queens Botanical Garden compost site) | NYS DEC Solid Waste Management Facilities, `2fni-raj8` (active composting registrations / permits; coordinates from the `georeference` column). Municipal yard-waste sites were left out because they give compost away |
| Brooklyn Grange, NYC Parks Greenbelt Native Plant Center | OpenStreetMap Nominatim. Demand for all added buyers is an assumption (see below) |
| Water treatment plants | OpenStreetMap (Overpass query for `man_made=water_works` in NY) |
| Retail garden hubs, battery / industrial buyer | OpenStreetMap Nominatim (Home Depot distribution center, Hicks Nurseries, Eastman Business Park / Li-Cycle) |
| Road distances | Public OSRM server (`router.project-osrm.org`, table service), cached in `data/distances.json` |

Supplier volumes, moisture, buyer demand and tipping fees are modelling assumptions - see `research/PARAMETERS.md`.

Buyer demand for the 10 added buyers is **not sourced**: commercial composters were set to 600-1,200 t/yr before the x1.5 scaling (smaller than the
existing Long Island Compost buyer), community farm and nursery sites to 50-100 t/yr. No public data says whether any of these buyers uses biochar.
Road distances for the added buyers come from the public OSRM server like the rest.
