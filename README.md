# Biochar Site Finder

Site-selection model and interactive 3D investor demo for placing biomass-to-biochar (pyrolysis) plants in New York State.
Given wood suppliers, candidate plant sites and biochar buyers, a mixed-integer optimizer picks the sites, machine sizes and
road flows that maximise portfolio NPV.

**Demo:** open `investor_demo_3d.html` in a browser (internet needed: map tiles, deck.gl, MapLibre and the HiGHS solver load from CDNs).
Every assumption in the left panel can be edited; the optimizer re-runs in the browser and the map updates. Each input is tagged
*Researched* (backed by published data) or *Assumption* (no reliable data found).

## Quick start

```bash
pip install -r requirements.txt     # Python 3.12
python build_data.py                # data/suppliers.csv, sites.csv, customers.csv
python optimize.py                  # base-case MILP (Pyomo + HiGHS) -> output/results.json and CSVs
python export_model.py              # output/model.json (data, defaults, Python base result) for the page
python make_map.py                  # -> investor_demo_3d.html (interactive)
python make_map_static.py           # -> investor_demo_3d_pydeck_static.html (plain pydeck, base case only)
```

`data/distances.json` caches OSRM road distances (delete it to re-query the public OSRM server).

## Changing things

| I want to... | Do this |
|---|---|
| Try different numbers during a demo | Use the sliders in the page; nothing to rebuild |
| Change a **default** value, or the default case | Edit `config.py` (and supplier/customer values in `build_data.py`), then rerun the five commands above |
| Change an input's label, range, note or Researched/Assumption tag | Edit `GROUPS` in `templates/map_template.html`, then `python make_map.py` |
| Add or replace suppliers, sites or buyers | Edit the lists in `build_data.py` (real coordinates), then rerun the pipeline |

## How it works

- `optimize.py` - Pyomo model solved with HiGHS: binary choice of machine size per site, wood flows supplier -> site, biochar flows site -> buyer,
  supply / capacity / demand / budget / minimum-utilisation constraints, mass balance (moisture, yield). Objective: NPV of annual cash flow minus CapEx.
  Haul-distance limits (`MAX_WOOD_MILES`, `MAX_CHAR_MILES` in `config.py`, 50 road miles by default; sliders in the page) forbid any wood or
  biochar flow on a longer link - a rule of thumb that trucked biomass and biochar rarely pay beyond 40-50 miles. Set them to 500 to remove the limit.
- `templates/map_template.html` - the demo page. It contains a JavaScript port of the same model. The WebAssembly HiGHS build (`highs@1.8.0`)
  solves linear programs; its integer solver crashes on this model, so branch-and-bound over the 0/1 site variables is implemented in the page
  (`branchAndBound`). It shows a near-optimal answer in about 0.1 s and refines to a proven optimum (typically 1-5 s, 6 s limit).
  Checked against `optimize.py` on 7 assumption sets: identical NPV, sites and CapEx. `investor_demo_3d.html?nosolver` disables the in-page optimizer.
- `export_model.py` / `make_map.py` bake the data and defaults into the page.

## Data

Locations are real New York facilities. See `data/SOURCES.md` for where each one comes from and `research/PARAMETERS.md` for every
parameter, its source and confidence level.

## Caveats

- Biochar and wood hauls are limited to 50 road miles by default, so the result depends on which buyers lie within reach of each plant; the 10 buyers added near New York City have guessed volumes.
- Supplier volumes, buyer demand, site rent and several cost items are assumptions; buyer demand is the largest unknown and drives how many plants make sense.
- Carbon-credit defaults (credit price, tonnes of CO2 per credit) differ from published market figures; the page shows the market range next to each.
- Prototype for discussion, not investment advice.
