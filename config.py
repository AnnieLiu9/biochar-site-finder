"""All economic assumptions in one place. Values marked ASSUMPTION are not sourced data."""

# Revenue inputs (credit definition differs from the market standard of 1 t CO2e per credit; see research/PARAMETERS.md)
BIOCHAR_PRICE = 500.0          # $/tonne
CREDIT_PRICE = 177.0           # $/credit
TCO2_PER_CREDIT = 2.0          # 1 credit = 2 t CO2 (market standard: 1)

# ASSUMPTIONS
CO2_PER_T_BIOCHAR = 2.8        # t CO2e per t wood biochar: 2.57-3.26 (Nebraska Forest Service), 3.01 (Carbon Cycle, Puro audit)
YIELD = 0.275                  # biochar per dry ton (slow pyrolysis typically 25-30%)
VAR_OPEX_PER_WET_T = 12.0      # $/wet ton (~$80/t biochar); calibrated, see README
CAPEX_FIXED = 500_000.0          # $ per machine (site prep, permitting, interconnect)
CAPEX_PER_TPY = 180.0           # $ per annual wet ton ~ $1,200 per annual t biochar (benchmarks $770-1,700)
RENT_FIXED = 100_000.0         # $/yr site rent + utilities (unsourced)
RENT_PER_TPY = 2.0             # $/yr per annual wet ton (unsourced)
DISCOUNT_RATE = 0.10
LIFETIME_YEARS = 15            # WSU TEA uses 20 for a power plant; 15 is conservative for pyrolysis equipment
BUDGET = 60_000_000.0          # $ total CapEx cap (was 40M in v1)
MIN_UTILIZATION = 0.40         # an opened machine must run at >= 40% of capacity

# Trucking: ATRI 2025 operating cost $2.336/mile; DAT/Uber Freight dry van spot ~$2.25-2.44,
# flatbed ~$2.5-3.1. Use $2.50 per loaded mile.
TRUCK_COST_PER_MILE = 2.75    # ATRI 2025 op. cost $2.34/mi; DAT 2026 dry van ~$2.39, flatbed ~$3.0; walking floor in between
MAX_WOOD_MILES = 50.0          # ASSUMPTION: feedstock is not hauled farther than this (road miles); industry rule of thumb is 40-50
MAX_CHAR_MILES = 50.0          # ASSUMPTION: same limit for biochar deliveries to buyers
WOOD_PAYLOAD_T = 25.0          # wet wood chips, walking-floor trailer
BIOCHAR_PAYLOAD_T = 20.0       # biochar is low density

ANNUITY = (1 - (1 + DISCOUNT_RATE) ** -LIFETIME_YEARS) / DISCOUNT_RATE

# Machine options the optimizer may choose per site (wet tons/yr of feedstock)
MACHINE_SIZES = {"Small": 15_000, "Medium": 30_000, "Large": 50_000}

# Scales every customer demand in build_data.py (v1 used 1.0)
DEMAND_SCALE = 1.5
