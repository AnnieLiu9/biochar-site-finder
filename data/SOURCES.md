# Data sources

The coordinates and names in `build_data.py` were collected from the sources below. The raw downloads (not committed) were only
used to pick and verify locations; the pipeline reads `data/*.csv`.

| Data | Source |
|---|---|
| Downstate wood / compost yards (5 suppliers) and compost buyers | NYS DEC Solid Waste Management Facilities, data.ny.gov dataset `2fni-raj8` (CSV export, `Georeference` column = lat/lon) |
| Upstate sawmills (5 suppliers) | NYS DEC Directory of Primary Wood-Using Industry (2017), https://dec.ny.gov/docs/lands_forests_pdf/directory17.pdf - largest mills with street addresses; geocoded with OpenStreetMap Nominatim |
| Water treatment plants | OpenStreetMap (Overpass query for `man_made=water_works` in NY) |
| Retail garden hubs, battery / industrial buyer | OpenStreetMap Nominatim (Home Depot distribution center, Hicks Nurseries, Eastman Business Park / Li-Cycle) |
| Road distances | Public OSRM server (`router.project-osrm.org`, table service), cached in `data/distances.json` |

Supplier volumes, moisture, buyer demand and tipping fees are modelling assumptions - see `research/PARAMETERS.md`.
