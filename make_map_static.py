"""Reads output/results.json and the input CSVs, writes a standalone investor_demo_3d_pydeck_static.html (PyDeck)."""
import json
import pandas as pd
import pydeck as pdk

R = json.load(open("output/results.json"))
sup = pd.read_csv("data/suppliers.csv")
cus = pd.read_csv("data/customers.csv")
sites = pd.DataFrame(R["sites"])
S = R["summary"]

TALLEST_M = 150_000        # tallest tower (highest-NPV site) is 150 km; others scale proportionally
ELEV_PER_DOLLAR = TALLEST_M / max(x["npv"] for x in R["sites"])
usd = lambda v: f"${v / 1e6:,.1f}M"

# ---------- data frames for layers ----------
sites["elev"] = sites.npv * ELEV_PER_DOLLAR
sites["npv_fmt"] = sites.npv.map(lambda v: f"${v:,.0f}")
sites["label"] = sites.npv.map(usd)
sites["tooltip"] = sites.apply(lambda r: (
    f"<div class='tt'><b>{r.site}</b><hr>"
    f"Machine size: <b>{r.machine_size}</b> ({r.capacity_tpy:,} t/yr)<br>"
    f"Tons processed / yr: <b>{r.wet_tons_in:,} wet t</b> ({r.dry_tons:,} dry t)<br>"
    f"Biochar produced: <b>{r.biochar_tons_out:,} t/yr</b><br>"
    f"Carbon credits generated: <b>{r.carbon_credits:,} /yr</b><br>"
    f"Annual profit: <b>${r.annual_profit:,.0f}</b><br>"
    f"Net present value: <b style='color:#ffd24d'>{r.npv_fmt}</b></div>"), axis=1)
sites["pos"] = sites.apply(lambda r: [r.lon, r.lat, r.elev + 2500], axis=1)

opened_names = set(sites.site)
sup["selected"] = sup.name.isin(opened_names)
sup["tooltip"] = sup.apply(lambda r: f"<div class='tt'><b>{r['name']}</b><hr>Wood supplier ({r.region})<br>"
                           f"Supply: {r.supply_tpy:,} wet t/yr<br>Moisture: {r.moisture:.0%}</div>", axis=1)
cus["tooltip"] = cus.apply(lambda r: f"<div class='tt'><b>{r['name']}</b><hr>Biochar buyer: {r.type}<br>"
                           f"Demand: {r.demand_tpy:,} t/yr @ ${r.price_per_ton:,.0f}/t</div>", axis=1)

wood = pd.DataFrame(R["wood_flows"])
wood = wood[wood.miles > 0].copy()
wood["w"] = 2 + wood.wet_tons / 3000
wood["tooltip"] = wood.apply(lambda r: f"<div class='tt'><b>Wood feedstock</b><hr>{r.supplier} &rarr; {r.site}<br>"
                             f"{r.wet_tons:,} wet t/yr &middot; {r.miles:,} mi</div>", axis=1)
char = pd.DataFrame(R["char_flows"])
char["w"] = 2 + char.biochar_tons / 600
char["tooltip"] = char.apply(lambda r: f"<div class='tt'><b>Biochar delivery</b><hr>{r.site} &rarr; {r.customer}<br>"
                             f"{r.biochar_tons:,} t/yr &middot; {r.miles:,} mi</div>", axis=1)

# ---------- layers ----------
layers = [
    # all candidate yards / sawmills: dim amber dots; chosen ones glow
    pdk.Layer("ScatterplotLayer", sup, get_position=["lon", "lat"], get_radius=5500,
              get_fill_color="selected ? [255,190,60,255] : [255,170,40,150]", pickable=True,
              radius_min_pixels=4, radius_max_pixels=14, stroked=True, get_line_color=[255, 200, 90, 220], line_width_min_pixels=1),
    pdk.Layer("ScatterplotLayer", cus, get_position=["lon", "lat"], get_radius=5500,
              get_fill_color=[60, 190, 255, 230], pickable=True, radius_min_pixels=4, radius_max_pixels=12,
              stroked=True, get_line_color=[160, 230, 255, 255], line_width_min_pixels=1),
    pdk.Layer("ArcLayer", wood, get_source_position=["s_lon", "s_lat"], get_target_position=["k_lon", "k_lat"],
              get_source_color=[60, 255, 120, 230], get_target_color=[255, 190, 40, 230],
              get_width="w", get_height=0.6, great_circle=False, pickable=True),
    pdk.Layer("ArcLayer", char, get_source_position=["k_lon", "k_lat"], get_target_position=["c_lon", "c_lat"],
              get_source_color=[0, 255, 255, 240], get_target_color=[40, 110, 255, 240],
              get_width="w", get_height=0.5, great_circle=False, pickable=True),
    # glowing towers: wide translucent halo + bright core
    pdk.Layer("ColumnLayer", sites, get_position=["lon", "lat"], get_elevation="elev", elevation_scale=1,
              radius=17000, get_fill_color=[255, 190, 40, 45], extruded=True, pickable=False, material=False, disk_resolution=24),
    pdk.Layer("ColumnLayer", sites, get_position=["lon", "lat"], get_elevation="elev", elevation_scale=1,
              radius=8500, get_fill_color=[255, 215, 90, 235], extruded=True, pickable=True, auto_highlight=True,
              highlight_color=[255, 255, 255, 255], material=False, disk_resolution=24),
    pdk.Layer("TextLayer", sites, get_position="pos", get_text="label", get_size=18, get_color=[255, 235, 160, 255], font_family="'Segoe UI', Arial, sans-serif",
              get_alignment_baseline="'bottom'", billboard=True, font_weight=700),
]

view = pdk.ViewState(latitude=42.3, longitude=-75.6, zoom=6.2, pitch=45, bearing=-12)
deck = pdk.Deck(layers=layers, initial_view_state=view, map_provider="carto", map_style="dark",
                tooltip={"html": "{tooltip}", "style": {"backgroundColor": "transparent", "color": "white"}})
deck.to_html("investor_demo_3d_pydeck_static.html", open_browser=False, notebook_display=False)

# ---------- overlay (title, KPIs, legend) injected into the standalone page ----------
import config as C
C_LIFE, C_DISC = C.LIFETIME_YEARS, f"{C.DISCOUNT_RATE:.0%}"
tot_t = int(sites.biochar_tons_out.sum()); tot_c = int(sites.carbon_credits.sum())
overlay = f"""
<style>
 .tt{{font:13px/1.55 -apple-system,Segoe UI,Roboto,sans-serif;background:rgba(10,14,24,.94);color:#e8eef8;padding:12px 14px;
     border:1px solid rgba(255,210,77,.55);border-radius:10px;box-shadow:0 0 22px rgba(255,190,40,.35);min-width:250px}}
 .tt hr{{border:0;border-top:1px solid rgba(255,255,255,.15);margin:6px 0}}
 .panel{{position:fixed;z-index:9;font:13px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;color:#dfe8f5;background:rgba(10,14,24,.78);
     backdrop-filter:blur(6px);border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:14px 16px}}
 #hdr{{top:16px;left:16px;max-width:360px}} #hdr h1{{margin:0 0 2px;font-size:20px;color:#fff;letter-spacing:.3px}}
 #hdr .sub{{color:#9fb0c8;font-size:12px;margin-bottom:10px}}
 .kpis{{display:flex;gap:16px}} .kpi b{{display:block;font-size:19px;color:#ffd24d}} .kpi span{{font-size:11px;color:#9fb0c8;text-transform:uppercase;letter-spacing:.6px}}
 #leg{{bottom:16px;left:16px}} #leg div{{margin:3px 0;display:flex;align-items:center;gap:9px}}
 .sw{{width:26px;height:4px;border-radius:2px;display:inline-block}} .dot{{width:11px;height:11px;border-radius:50%;display:inline-block}}
 #note{{bottom:16px;right:16px;max-width:300px;font-size:11px;color:#9fb0c8}}
</style>
<div class="panel" id="hdr"><h1>Biochar Site Finder</h1><div class="sub">New York State &middot; {len(sup) * 2 + len(cus)}-node optimization prototype &middot; {C_LIFE}-yr NPV @ {C_DISC}</div>
 <div class="kpis"><div class="kpi"><b>{usd(S['total_npv'])}</b><span>Portfolio NPV</span></div>
 <div class="kpi"><b>{len(sites)}</b><span>Sites opened</span></div>
 <div class="kpi"><b>{tot_t:,}</b><span>t biochar / yr</span></div>
 <div class="kpi"><b>{tot_c:,}</b><span>credits / yr</span></div></div></div>
<div class="panel" id="leg">
 <div><span class="sw" style="background:#ffd75a;height:14px;width:10px"></span>Selected site &mdash; tower height = NPV</div>
 <div><span class="sw" style="background:linear-gradient(90deg,#3cff78,#ffbe28)"></span>Wood feedstock &rarr; site</div>
 <div><span class="sw" style="background:linear-gradient(90deg,#00ffff,#286eff)"></span>Biochar &rarr; buyer</div>
 <div><span class="dot" style="background:#ffaa28"></span>Wood supplier / candidate site</div>
 <div><span class="dot" style="background:#3cbeff"></span>Biochar buyer</div></div>
<div class="panel" id="note">Locations: real NYS DEC facility data. Biochar $500/t and carbon credit $177 per credit. CapEx, opex, supply and tipping fees are assumptions for the prototype. Hover a tower for details; drag to rotate.</div>
"""
html = open("investor_demo_3d_pydeck_static.html", encoding="utf-8").read()
html = html.replace("</body>", overlay + "</body>").replace("<title>pydeck</title>", "<title>Biochar Site Finder - NY Investor Demo</title>")
open("investor_demo_3d_pydeck_static.html", "w", encoding="utf-8").write(html)
print("wrote investor_demo_3d_pydeck_static.html", len(html) // 1024, "KB")
