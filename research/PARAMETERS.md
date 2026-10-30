# Parameter research log (2026-10-27)

Confidence: **H** = published figure used directly, **M** = published range, our pick inside it, **L** = no usable source found (assumption).

| Parameter | v2 | Now | Basis | Conf. |
|---|---|---|---|---|
| Biochar price | $500/t | $500/t | Bulk market quotes range ~$300-1,500/t (aggregator, low reliability); Wakefield 2 yd3 supersack $375 | M |
| Carbon credit price | $177 | $177 | Market is lower: Puro/Nasdaq CORCCHAR index $125-145 in 2025; Platts US biochar $150/tCO2e (Oct 2025); $170 presale offer | H (market) |
| tCO2 per credit | 2 t | 2 t | **Conflicts with market standard**: 1 CORC = 1 t CO2e (Puro). Default is still 2 t - decide whether to align with the market standard | H (market) |
| tCO2e per t biochar | 2.5 | **2.8** | Wood biochar 2.57-3.26 credits/t (Nebraska Forest Service sheet); Carbon Cycle 3.01 (Puro audit) | M |
| Biochar yield | 27.5% | 27.5% (unchanged) | Slow pyrolysis typically 25-30% of dry wood; vendor data ~21% of wet feed | M |
| CapEx | $1M + $375/annual wet t (~$2,900 per annual t biochar) | **$0.5M + $180/annual wet t (~$1,200 per annual t biochar)** | Edmonton wood-waste plant: 3,500 t biochar/yr for ~CA$3.7M (~$770/t); Alberta centralised study US$2.75M; Pyreg PX1500-H EUR 1.54M for ~1,000 t/yr (~$1,700/t, equipment only, student estimate). Old value was 2-4x the benchmarks | M |
| Variable opex | $22/wet t | **$12/wet t** (~$80/t biochar) | Calibrated so total levelized production cost is ~$300/t biochar: literature $150-260/t (large-scale TEA), $233/t (peer-reviewed), up to ~$390/t (UK range); our plants are small | L-M |
| Rent/utilities | $150k + $8/t | **$100k + $2/t** (x1.5 downstate) | No source | L |
| Tipping fee income (downstate) | $35-55/wet t | **$35/wet t, all five** | Shelter Island wood chips $35/t; Manchester CT $40/t; Lexington SC $28/t; DSNY landscaper yard waste $12.34/cu yd (per-ton conversion not sourced) | M |
| Sawmill residue price | $10/t paid | $10/t (unchanged) | No current NY/Northeast price found; Northeast fuelwood prices fell ~23% since 2015, outlets shrinking, so low | L |
| Sawmill residue volume | ~0.9 t per MBF capacity | unchanged | ResourceWise rule of thumb: 1 t chips + 1 t bark/sawdust per MBF | M |
| Moisture | 40-50% | unchanged | Green wood 30-60%; pyrolysis needs 10-15% after drying. **Drying cost is not modelled separately**; assumed covered by pyrolysis waste heat and the opex above | M / L |
| Discount rate | 10% | 10% | WSU biochar TEA: real 10% (nominal 12.2%) | M |
| Lifetime | 10 yr | **15 yr** | WSU TEA uses 20 yr for a power plant; 15 conservative for pyrolysis equipment | M |
| Trucking | $2.50/mi | **$2.75/mi** | ATRI 2025 cost $2.336/mi; DAT 2026 dry van ~$2.39, flatbed ~$3.0 | H |
| Customer demand | x1.5 of 14,500 t | x1.5 of 20,967 t (20 buyers, 10 added near NYC) | **No data at all.** Biggest unknown; drives the number of sites. Added buyers' volumes are guesses | L |
| Supplier supply volumes | assumed | unchanged | DEC lists mill capacity, not residue output; urban yard volumes not public | L |

## Sources
- Credit prices: Puro.earth / Nasdaq CORCCHAR index; S&P Global Platts (Nov 2025) "biochar carbon credit prices steady but sentiment weakens"
- tCO2e per t biochar: Nebraska Forest Service biochar carbon sheet; Puro audit for Carbon Cycle
- CapEx: Petrox/M&L Edmonton press release (Sept 2023); Oregon State PX1500-H design presentation; Alberta centralised pyrolysis study
- Production cost: USFS mobile pyrolysis financial study; WSU "Biochar Production in Biomass Power Plants" TEA (discount rate, lifetime); peer-reviewed agronomic/economic study ($232.87/t)
- Tipping fees: NYC DSNY compost fee notice (eff. Nov 1 2025); Shelter Island, Manchester CT, Lexington SC fee schedules
- Residues: ResourceWise "Residues becoming a problem for Northeastern mills"
- Trucking: ATRI 2026 operational costs report (via Bulk Transporter / CCJ); Uber Freight and JOC/DAT rate reports
