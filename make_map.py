"""Builds the interactive investor demo: templates/map_template.html + output/model.json -> investor_demo_3d.html.
Uses deck.gl (the library pydeck wraps) and MapLibre directly, plus HiGHS (WebAssembly) so every assumption can be edited live.
The plain pydeck export is still produced by make_map_static.py."""
import json

data = open("output/model.json", encoding="utf-8").read()
html = open("templates/map_template.html", encoding="utf-8").read()
assert "/*__DATA__*/null" in html
html = html.replace("/*__DATA__*/null", data)
open("investor_demo_3d.html", "w", encoding="utf-8").write(html)
print("wrote investor_demo_3d.html", len(html) // 1024, "KB, defaults:", len(json.loads(data)["defaults"]), "editable inputs")
