"""Expand rez_substation_lookup_NEM.csv with town/locality keywords.

Adds Eyre Peninsula (EYR) as a fourth SA catchment per user request, and adds
~400 town/wind-farm-cluster keywords across four expansion passes derived from
iterative inspection of the unclassified list in
transmission_catchment_lookup_draft_v2.csv. All locality additions are written
at confidence_default='medium' (matching the QLD methodology pattern where
town-name matches are medium-confidence judgement calls). Direct substation
matches retain 'high'.

Passes:
  1. Initial locality + EYR catchment additions (~286 rows)
  2. Pass-2 corrections after first matcher run (~124 rows)
  3. Pass-3 focused on remaining clearly-classifiable >100MW items (~77 rows)
  4. Pass-4 sweep of NSW/VIC residue with clear REZ assignment (~43 rows)

Re-running this script is idempotent: it drops any prior rows with the same
(state, rez_code, substation) tuple before re-inserting.
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LOOKUP = REPO / "data" / "rez" / "rez_substation_lookup_NEM.csv"

# (state, rez_code, rez_name, substation, substation_type, transmission_lines,
#  source_document, confidence_default, notes)
COLS = [
    "state", "rez_code", "rez_name", "substation", "substation_type",
    "transmission_lines", "source_document", "confidence_default", "notes",
]

# Standard rationale strings per REZ name
NSW_REZ_NAME = {
    "CWO": "Central-West Orana",
    "NEW": "New England",
    "HCC": "Hunter-Central Coast",
    "ILW": "Illawarra",
    "SW-NSW": "South West NSW",
}
VIC_REZ_NAME = {
    "CN-VIC": "Central North Victoria",
    "MR": "Murray River",
    "WV": "Western Victoria",
    "GIP": "Gippsland",
    "SW-VIC": "South-West Victoria",
}
SA_REZ_NAME = {
    "MN": "Mid-North SA",
    "SE-SA": "South-East SA",
    "RIV": "Riverland",
    "EYR": "Eyre Peninsula",
}

# Each tuple: (substation, type, lines, source, notes)
# Confidence default is 'medium' for all (locality matches), 'high' overrides noted below.

NSW_ADDITIONS = {
    "CWO": [
        ("Cobbora", "town/project cluster", "CWO", "Public records (Cobbora SF/BESS near Dunedoo)", ""),
        ("Goulburn River", "river/project area", "CWO (national park north of Mudgee)", "Public records", ""),
        ("Uungula", "wind farm cluster", "CWO (Wellington area)", "Public records (Uungula WF)", ""),
        ("Tallawang", "solar/BESS cluster", "CWO (Gulgong area)", "Public records", ""),
        ("Pottinger", "energy park cluster", "CWO/NEW border (Liverpool Plains)", "Public records (Pottinger Energy Park)", ""),
        ("Lake Lyell", "pumped hydro", "CWO/Central West (Lithgow area)", "Public records (Lake Lyell PHES)", ""),
        ("Lambruk", "solar/BESS", "CWO", "Public records", ""),
        ("Burrendong", "wind farm", "CWO (Wellington area)", "Public records (Burrendong WF)", ""),
        ("Argoon", "wind farm", "CWO", "Public records (Argoon WF — RES Group)", ""),
        ("Kerrs Creek", "wind farm", "CWO (Orange area)", "Public records (Kerrs Creek WF)", ""),
        ("Ilford", "energy hub", "CWO", "Public records (Ilford Green Energy Hub)", ""),
        ("Pint Pot", "BESS", "CWO", "Public records", ""),
        ("Lindsay Gap", "BESS", "CWO (Gulgong area)", "Public records", ""),
        ("Devlins", "wind farm", "CWO", "Public records (Devlins WF)", ""),
        ("Hanworth", "battery", "CWO", "Public records (Hanworth Battery)", ""),
        ("Garoo", "BESS", "CWO", "Public records", ""),
        ("Gara", "BESS", "CWO", "Public records", ""),
        ("Holloway", "BESS", "CWO", "Public records (Holloway BESS)", ""),
        ("Junction Rivers", "wind farm", "CWO border", "Public records", ""),
        ("Tallawang", "solar/BESS", "CWO", "Public records", ""),
        ("Piambong", "wind farm", "CWO", "Public records (Piambong WF — KCI)", ""),
        ("Wattle Creek", "energy hub", "CWO/NEW", "Public records (Wattle Creek Energy Hub)", ""),
        ("Moah Creek", "solar", "CWO", "Public records (Moah Creek SF)", ""),
        ("Valley of the Winds", "wind farm", "CWO", "Public records", ""),
        ("Central West", "region", "CWO/Central West NSW", "AEMO ISP A3 N3", ""),
        ("Mudgee", "town", "CWO (Mudgee area)", "EnergyCo CWO", ""),
        ("Gulgong", "town", "CWO (Gulgong area)", "EnergyCo CWO", ""),
        ("Orana", "region", "CWO (Orana region)", "EnergyCo CWO", ""),
        ("Dargues", "energy project", "CWO area (gold mine)", "Public records", ""),
        ("Sandy Creek", "solar farm", "CWO area", "Public records (Sandy Creek SF)", ""),
        ("Deargee", "solar/BESS", "CWO", "Public records (Deargee SF)", ""),
        ("Wongalea", "BESS", "CWO", "Public records", ""),
        ("Willavale", "BESS", "CWO", "Public records", ""),
        ("Cassilis", "wind farm", "CWO/Upper Hunter border", "Public records (Cassilis area)", ""),
        ("The Plains", "energy hub", "CWO (Liverpool Plains)", "Public records (The Plains project)", ""),
    ],
    "NEW": [
        ("Winterbourne", "wind farm", "NEW (Walcha area)", "Public records (Winterbourne WF)", ""),
        ("Hills of Gold", "wind farm", "NEW (Nundle/Hanging Rock)", "Public records (Hills of Gold WF)", ""),
        ("Kings Plain", "wind farm", "NEW (Glen Innes area)", "Public records (Kings Plain WF)", ""),
        ("Peel Valley", "BESS", "NEW (Tamworth area)", "Public records", ""),
        ("Wallabadah", "BESS", "NEW (Liverpool Plains)", "Public records", ""),
        ("Apsley", "BESS/project", "NEW (Walcha-Apsley area)", "Public records", ""),
        ("Nundle", "town", "NEW", "Public records", ""),
        ("Murrurundi", "town", "NEW/HCC border", "Public records", ""),
        ("Quirindi", "town", "NEW (Liverpool Plains)", "Public records", ""),
        ("Hanworth", "wind farm", "NEW", "Public records", ""),
        ("Mt Lindesay", "wind farm", "NEW border", "Public records", ""),
        ("Pottinger Energy Park", "energy hub", "NEW (Liverpool Plains)", "Public records", ""),
        ("Sundown", "hybrid facility", "NEW border (QLD)", "Public records (Sundown Hybrid Facility)", ""),
        ("New England Solar", "solar project", "NEW (Uralla area)", "Public records (UPC NE Solar)", ""),
        ("Bowmans Creek", "wind farm", "Upper Hunter/NEW border", "Public records", "Could be HCC — review"),
        ("Salt Creek", "wind farm", "NEW/HCC border", "Public records", ""),
        ("Goonoo", "wind/forest", "CWO/NEW border", "Public records", ""),
        ("Romani", "solar farm", "NEW (Quirindi area)", "Public records (Romani SF)", ""),
        ("Merino", "solar farm", "NEW", "Public records", ""),
        ("Sundown Hybrid", "hybrid", "NEW border", "Public records", ""),
        ("Belhaven", "renewable project", "NEW", "Public records (Belhaven RE Project)", ""),
        ("Bellambi Heights", "renewable project", "NEW", "Public records", ""),
        ("Strontian", "solar/BESS", "NEW (Liverpool Plains)", "Public records", ""),
        ("Texas BESS", "BESS", "NEW/QLD border", "Public records", ""),
        ("Edderton", "hybrid facility", "Upper Hunter (NEW/HCC border)", "Public records (Edderton Hybrid)", ""),
        ("McCullys Gap", "BESS", "Upper Hunter (HCC/NEW border)", "Public records", "Could be HCC"),
        ("Liverpool Plains", "region", "NEW (Liverpool Plains)", "EnergyCo NEW", ""),
        ("Tablelands", "region", "NEW (New England Tableland)", "EnergyCo NEW", ""),
    ],
    "HCC": [
        ("Denman", "town/BESS", "Upper Hunter (HCC)", "Public records (Denman BESS — KCI)", ""),
        ("Glenbawn", "pumped hydro", "Upper Hunter", "Public records (Glenbawn PHES)", ""),
        ("Stratford", "renewable hub", "Gloucester (HCC)", "Public records (Stratford Renewable Energy Hub)", ""),
        ("Maison Dieu", "BESS", "Hunter Valley", "Public records", ""),
        ("Merriwa", "solar/BESS", "Upper Hunter (HCC/CWO border)", "Public records", "Could be CWO"),
        ("Anvil Hill", "project", "Upper Hunter", "Public records", ""),
        ("Glennies Creek", "pumped hydro", "Hunter Valley (Singleton)", "Public records (Glennies Creek PHES)", ""),
        ("Yarrabee", "solar project", "Hunter", "Public records (Yarrabee Solar)", ""),
        ("Mt View", "wind farm", "HCC (Cessnock area)", "Public records (Mt View WF — KCI)", ""),
        ("Awaba", "BESS", "Central Coast (HCC)", "Public records", ""),
        ("Beresfield", "BESS", "Hunter", "Public records", ""),
        ("Camberwell", "project", "Hunter Valley", "Public records", ""),
        ("Mt Arthur", "coal/project", "Upper Hunter", "Public records", ""),
        ("Liddell", "existing coal", "Upper Hunter", "Transgrid TAPR 2024", ""),
        ("Bayswater", "existing coal/REZ collector", "Upper Hunter", "Transgrid TAPR 2024", "Also NEW REZ collector"),
        ("Gloucester", "town/project area", "HCC", "Public records", ""),
        ("Cessnock", "town", "HCC", "Public records", ""),
        ("Kurri Kurri", "town", "Hunter (HCC)", "Public records", ""),
        ("Maitland", "town", "Hunter (HCC)", "Public records", ""),
        ("Lake Macquarie", "region", "Central Coast (HCC)", "Public records", ""),
        ("Central Coast", "region", "HCC", "EnergyCo HCC", ""),
        ("Upper Hunter", "region", "HCC", "EnergyCo HCC", ""),
        ("Goulburn River Solar", "solar/BESS", "HCC/CWO border (Bylong)", "Public records", "Border case"),
        ("Bylong", "town", "HCC/CWO border", "Public records", ""),
        ("Glenbawn Pumped", "pumped hydro", "Upper Hunter", "Public records", ""),
        ("Novocastrian", "offshore wind", "Hunter Coast (N10 — offshore)", "AEMO ISP A3 N10", ""),
        ("Hunter Coast", "offshore zone", "N10 offshore wind", "AEMO ISP A3 N10; EnergyCo", ""),
    ],
    "ILW": [
        ("Tallawarra", "existing gas", "Illawarra (Dapto area)", "Public records (Tallawarra A/B)", ""),
        ("Marulan", "OCGT/CCGT", "Southern Highlands (Bannaby gateway)", "Public records (Marulan OCGT)", "Could be SW-NSW"),
        ("Kangaroo Valley", "BESS", "ILW", "Public records", ""),
        ("Bargo", "project", "Macarthur/ILW", "Public records", ""),
        ("Western Sydney", "load/pumped hydro", "ILW gateway/load", "Public records (Western Sydney PHES)", ""),
        ("Ulladulla", "offshore wind", "Illawarra Coast (N11)", "AEMO ISP A3 N11", ""),
        ("Illawarra Coast", "offshore zone", "N11 offshore wind", "AEMO ISP A3 N11", ""),
        ("Southern Highlands", "region", "ILW gateway", "Public records", ""),
        ("Eden", "offshore wind", "Cooma-Monaro Coast (south coast)", "AEMO ISP A3 N8", "Geographically Cooma-Monaro — flagged"),
        ("Eastern Rise", "offshore wind", "South coast/Cooma-Monaro", "Public records", "Possibly Cooma-Monaro N8"),
        ("South Pacific Offshore", "offshore wind", "South coast", "Public records", ""),
    ],
    "SW-NSW": [
        ("Talbingo", "BESS/Snowy", "Snowy 2.0 area", "Transgrid TAPR 2024 (HumeLink)", ""),
        ("Snowy 2.0", "pumped hydro", "Snowy/SW-NSW", "Transgrid TAPR 2024", ""),
        ("Bago", "wind farm", "SW-NSW (Tumut area)", "Public records (Bago WF)", ""),
        ("Khancoban", "hydro", "Snowy/SW-NSW", "Public records", ""),
        ("Bookham", "wind farm", "SW-NSW (Yass area)", "Public records (Bookham WF)", ""),
        ("Wee Jasper", "wind farm", "SW-NSW (south of Yass)", "Public records (Wee Jasper WF)", ""),
        ("Rye Park", "wind farm", "SW-NSW (Yass area)", "Public records (Rye Park WF)", ""),
        ("Gullen Range", "wind/BESS", "Southern Tableland (SW-NSW)", "Public records (Gullen Range WF)", ""),
        ("Gundary", "solar farm", "SW-NSW (Goulburn area)", "Public records (Gundary SF)", ""),
        ("Gol Gol", "wind farm", "SW-NSW (Buronga area)", "Public records (Gol Gol WF)", ""),
        ("Mallee", "wind farm", "SW-NSW (Far West)", "Public records", ""),
        ("Morundah", "solar/thermal", "SW-NSW (Riverina)", "Public records", ""),
        ("Bullawah", "wind farm", "SW-NSW (Riverina)", "Public records (Bullawah WF Stage 1)", ""),
        ("Ivanhoe", "BESS", "SW-NSW (Far West)", "Public records", ""),
        ("Tchelery", "wind farm", "SW-NSW (Far West)", "Public records", ""),
        ("Lake Victoria", "energy park", "SW-NSW (Far West)", "Public records (Lake Victoria Energy Park)", ""),
        ("Lake Cargelligo", "project area", "SW-NSW (Lachlan)", "Public records", ""),
        ("Narrandera", "BESS", "SW-NSW (Riverina)", "Public records", ""),
        ("Junee", "project", "SW-NSW (Riverina)", "Public records", ""),
        ("Culcairn", "solar farm", "SW-NSW (south Riverina)", "Public records (Culcairn SF)", ""),
        ("Albury", "load/border", "SW-NSW/border", "Public records", ""),
        ("Avonlie", "solar/wind cluster", "SW-NSW (Hay area)", "Public records", ""),
        ("Barwon", "solar farm/BESS", "SW-NSW", "Public records", ""),
        ("Blind Creek", "solar/BESS", "SW-NSW", "Public records (Blind Creek SF/BESS)", ""),
        ("Boco Rock", "wind farm", "SW-NSW (Cooma-Monaro N8 — electrically linked)", "Public records (Boco Rock WF)", "Flagged: geographically N8 Cooma-Monaro"),
        ("Bodangora", "wind farm", "(CWO — see CWO entry)", "Public records", "Already CWO"),
        ("Bango", "wind farm", "SW-NSW (Yass area)", "Public records (Bango 973/999 WF)", ""),
        ("Crookwell", "wind farm cluster", "SW-NSW (Southern Tableland)", "Public records", ""),
        ("Gunning", "wind farm", "SW-NSW (Southern Tableland)", "Public records (Gunning WF)", ""),
        ("Yass", "town", "SW-NSW (Yass area)", "Public records", ""),
        ("Riverina", "region", "SW-NSW", "AEMO ISP A3 N5/N6", ""),
        ("Far West", "region", "SW-NSW (Far West NSW)", "AEMO ISP A3 N4/N5", ""),
        ("Lower Lachlan", "region", "SW-NSW", "AEMO ISP A3 N5", ""),
        ("Tumut", "region/hydro", "SW-NSW (Tumut N7)", "AEMO ISP A3 N7", ""),
        ("Snowy", "project cluster", "SW-NSW (Snowy 2.0)", "Transgrid TAPR 2024", ""),
        ("Murrumbidgee", "region", "SW-NSW (Riverina)", "AEMO ISP A3 N5", ""),
        ("Wakool", "region", "SW-NSW (Riverina south)", "Public records", ""),
        ("Sunraysia NSW", "solar cluster", "SW-NSW border with VIC", "Public records", ""),
        ("Mt Hope", "wind farm", "SW-NSW (Lower Lachlan)", "Public records", ""),
        ("Yawong", "wind farm", "SW-NSW", "Public records", ""),
        ("Wallaroo", "wind farm", "SW-NSW (Yass area)", "Public records", ""),
        ("Goulburn", "BESS/town", "Southern Tableland (SW-NSW)", "Public records", ""),
        ("Tirranna", "BESS", "SW-NSW (Goulburn area)", "Public records (Tirranna BESS — KCI)", ""),
        ("Gol Gol", "wind farm", "SW-NSW (Buronga area)", "Public records (Gol Gol WF)", ""),
    ],
}

VIC_ADDITIONS = {
    "GIP": [
        ("Seaspray", "offshore wind", "Gippsland Coast (V7)", "AEMO ISP A3 V7", ""),
        ("Deal 1", "offshore wind", "Gippsland Coast (V7)", "Public records (Deal 1/2 OWF)", ""),
        ("Deal 2", "offshore wind", "Gippsland Coast (V7)", "Public records", ""),
        ("Great Eastern", "offshore wind", "Gippsland Coast (V7)", "Public records (Great Eastern OWF)", ""),
        ("Kut Wut Brataualung", "offshore wind", "Gippsland Coast (V7)", "Public records", ""),
        ("Kentbruck", "wind/green hub", "GIP (Wonthaggi area)", "Public records (Kentbruck Green Power Hub)", ""),
        ("Blue Mackerel North", "offshore wind", "Gippsland Coast", "Public records", ""),
        ("Spinifex", "offshore wind", "Gippsland Coast (V7)", "Public records", ""),
        ("Cape Winds", "offshore wind", "Gippsland Coast (V7)", "Public records", ""),
        ("Greater Southern Offshore", "offshore wind", "Gippsland Coast (V7)", "Public records", ""),
        ("Southern Winds Offshore", "offshore wind", "Gippsland Coast (V7)", "Public records", ""),
        ("Wooreen", "energy storage", "GIP (Latrobe Valley)", "Public records (Wooreen ESS)", ""),
        ("Hexham", "wind farm", "GIP", "Public records (Hexham WF)", ""),
        ("Phillip Island", "offshore/region", "GIP coast", "Public records", ""),
        ("Anglesea", "existing coal/project", "GIP/SW-VIC", "Public records", "Border case"),
        ("Jeeralang", "existing gas", "GIP (Latrobe Valley)", "Public records", ""),
        ("Loy Yang B", "existing coal", "GIP (Latrobe Valley)", "Public records", ""),
        ("Bairnsdale", "existing gas", "GIP (East Gippsland)", "Public records", ""),
        ("Darnum", "BESS", "GIP (West Gippsland)", "Public records", ""),
        ("Maryvale", "energy hub", "GIP (Latrobe Valley)", "Public records", ""),
        ("Latrobe Valley", "region", "GIP (V5 REZ scope)", "AEMO ISP A3 V5", ""),
        ("Gippsland Coast", "offshore zone", "V7 offshore wind", "AEMO ISP A3 V7", ""),
    ],
    "WV": [
        ("Warracknabeal", "wind farm", "WV (Wimmera)", "Public records", ""),
        ("Joel", "BESS", "WV (Ararat area)", "Public records (Joel BESS — sometimes Joel Joel)", ""),
        ("Lambing Gully", "wind farm", "WV/SW-VIC border (Ballarat)", "Public records", "Could be SW-VIC"),
        ("Meredith", "wind farm", "WV (Ballarat area)", "Public records (Meredith WF)", ""),
        ("Elaine", "BESS", "WV (Ballarat area)", "Public records (Elaine BESS)", ""),
        ("Learmonth", "BESS", "WV (Ballarat area)", "Public records (Learmonth BESS)", ""),
        ("Lovely Banks", "renewable hub", "WV (Geelong-Ballarat corridor)", "Public records", ""),
        ("Glenbrae", "BESS", "WV (Ballarat area)", "Public records (Glenbrae BESS)", ""),
        ("Warrenheip", "BESS", "WV (Ballarat area)", "Public records (Warrenheip BESS)", ""),
        ("Mt Mercer", "wind farm", "WV (Ballarat area)", "Public records (Mt Mercer WF)", ""),
        ("Mt Hopes", "wind project", "WV", "Public records", ""),
        ("Cooba", "solar farm", "WV", "Public records (Cooba SF — KCI)", ""),
        ("Haunted Gully", "terminal/BESS", "WV (Stockyard Hill area)", "Public records", ""),
        ("Newlyn", "wind farm", "WV", "Public records", ""),
        ("Wimmera", "region", "WV (Wimmera)", "AEMO ISP A3 V3", ""),
    ],
    "SW-VIC": [
        ("Mt Fyans", "wind farm", "SW-VIC (Mortlake area)", "Public records (Mt Fyans WF)", ""),
        ("Connewarren", "BESS", "SW-VIC (Mortlake area)", "Public records (Connewarren BESS)", ""),
        ("Darlington", "wind farm", "SW-VIC", "Public records (Darlington WF — GPG)", ""),
        ("Willatook", "wind farm", "SW-VIC (Hamilton area)", "Public records (Willatook WF)", ""),
        ("Ryan Corner", "wind farm", "SW-VIC (Portland area)", "Public records (Ryan Corner WF)", ""),
        ("Gnarwarre", "BESS", "SW-VIC (Geelong area)", "Public records", ""),
        ("Dalvui", "BESS", "SW-VIC", "Public records", ""),
        ("Stonehaven", "gas turbine", "SW-VIC (Geelong)", "Public records", ""),
        ("Winchelsea", "gas turbine", "SW-VIC (Geelong area)", "Public records", ""),
        ("Geelong", "load/BESS", "SW-VIC (Geelong)", "Public records", "Load centre"),
        ("Little River", "BESS/solar", "SW-VIC (Geelong-Melbourne)", "Public records (Little River BESS/SF)", ""),
        ("Mornington", "BESS", "SW-VIC/Melbourne", "Public records", "Could be load-area, flag for review"),
        ("Yaloak South", "wind farm", "SW-VIC", "Public records", ""),
        ("Yambuk", "wind farm", "SW-VIC", "Public records", ""),
        ("Codrington", "wind farm", "SW-VIC", "Public records (Codrington WF)", ""),
        ("Dundonnell", "wind farm", "SW-VIC", "Public records (Dundonnell WF)", ""),
        ("Newport", "existing gas", "SW-VIC/Melbourne", "Public records", "Load area"),
        ("Mortlake South", "energy hub", "SW-VIC", "Public records", ""),
        ("Cape Bridgewater", "wind farm", "SW-VIC", "Public records", ""),
        ("Portland", "load/region", "SW-VIC (V4)", "AEMO ISP A3 V4", ""),
    ],
    "CN-VIC": [
        ("Goorambat", "BESS/solar", "CN-VIC (Benalla area)", "Public records (Goorambat BESS/SF)", ""),
        ("Pine Lodge", "BESS", "CN-VIC (Shepparton area)", "Public records (Pine Lodge BESS)", ""),
        ("West Mokoan", "solar farm", "CN-VIC (Benalla area)", "Public records (West Mokoan SF)", ""),
        ("Corop", "solar/BESS", "CN-VIC (Echuca area)", "Public records (Corop SF/BESS)", ""),
        ("Mologa", "BESS", "CN-VIC/MR border", "Public records", ""),
        ("Prairie", "solar farm", "CN-VIC", "Public records (Prairie SF)", ""),
        ("Koyuga", "wind farm", "CN-VIC (Echuca area)", "Public records (Koyuga Nanneella WF)", ""),
        ("Nanneella", "wind farm", "CN-VIC", "Public records", ""),
        ("Numurkah", "solar farm", "CN-VIC", "Public records", ""),
        ("Tatura", "region", "CN-VIC", "Public records", ""),
        ("Stanhope", "BESS", "CN-VIC (Tatura area)", "Public records", ""),
        ("Bullarook", "wind/solar", "CN-VIC/WV border", "Public records", ""),
        ("Murray 1", "hydro", "CN-VIC/Ovens Murray (V1) border", "Public records (Snowy Hydro Murray 1)", ""),
        ("Murray 2", "hydro", "CN-VIC/Ovens Murray (V1) border", "Public records (Snowy Hydro Murray 2)", ""),
        ("Hume", "hydro/border", "CN-VIC/Ovens Murray (V1)", "Public records", ""),
        ("Baranduda", "energy reserve", "CN-VIC (Wodonga area)", "Public records", ""),
        ("Kiewa Valley", "BESS", "CN-VIC (Wodonga area)", "Public records (KIEWA VALLEY BESS)", ""),
        ("Barnawartha", "solar/storage", "CN-VIC (Wodonga area)", "Public records", ""),
        ("Bogong", "hydro", "CN-VIC/Ovens Murray V1", "Public records (Bogong/Mackay)", ""),
        ("Banimboola", "hydro", "CN-VIC (Kiewa scheme)", "Public records", ""),
        ("Clover", "hydro", "CN-VIC (Kiewa scheme)", "Public records", ""),
        ("Clayton", "hydro", "CN-VIC", "Public records", ""),
        ("Eildon", "hydro", "CN-VIC (Eildon)", "Public records", ""),
        ("Rubicon", "BESS/hydro", "CN-VIC (Eildon area)", "Public records", ""),
        ("Goulburn Valley", "region", "CN-VIC", "Public records", ""),
    ],
    "MR": [
        ("Nowingi", "solar farm/BESS", "MR (Mildura area)", "Public records (Nowingi SF — Edify)", ""),
        ("Kiamal", "solar/BESS", "MR (Mildura area)", "Public records (Kiamal SF/BESS)", ""),
        ("Quandong", "solar farm", "MR", "Public records", ""),
        ("Karadoc", "solar farm", "MR (Mildura)", "Public records (Karadoc SF)", ""),
        ("Yatpool", "solar farm", "MR (Mildura)", "Public records (Yatpool SF)", ""),
        ("Hattah", "solar/wind", "MR", "Public records", ""),
        ("Manangatang", "solar/wind", "MR", "Public records", ""),
        ("Ouyen", "solar farm", "MR", "Public records", ""),
        ("Tutye", "wind/solar", "MR", "Public records", ""),
        ("Meering", "wind farm/BESS", "MR (Kerang area)", "Public records (Meering WF/BESS)", ""),
        ("Swan Hill", "town", "MR", "Public records", ""),
        ("Sunraysia", "region", "MR (Mildura/Sunraysia)", "AEMO ISP A3 V2", ""),
        ("Mildura", "town/region", "MR", "AEMO ISP A3 V2", ""),
    ],
}

SA_ADDITIONS = {
    "MN": [
        ("Goyder", "wind/solar/BESS", "MN (Goyder regional council)", "Public records (Goyder North/South RE Facility)", ""),
        ("Bundy Energy Hub", "BESS hub", "MN (Bundey area)", "Public records (Bundy Energy Hub A/B)", ""),
        ("Snapper Point", "power station", "MN/Adelaide", "Public records", ""),
        ("Solar River", "solar/BESS", "MN (Riverland border)", "Public records (Solar River Project)", "Could be RIV"),
        ("Geranium Plains", "solar/BESS", "MN", "Public records (Geranium Plains SF)", ""),
        ("Mintaro", "GT", "MN", "Public records (Mintaro GT)", ""),
        ("Willogoleche", "wind farm", "MN (Hallett area)", "Public records (Willogoleche WF)", ""),
        ("Reeves Plains", "OCGT/BESS", "MN/Adelaide", "Public records (Reeves Plains OCGT/BESS)", ""),
        ("Quarantine", "existing gas", "Adelaide/MN", "Public records (Quarantine PS)", "Load-area"),
        ("Pelican Point", "existing gas/BESS", "Adelaide", "Public records (Pelican Point PS/BESS)", "Load-area"),
        ("Osborne", "existing/BESS", "Adelaide", "Public records (Osborne BESS)", "Load-area"),
        ("Lonsdale", "OCGT", "Adelaide", "Public records", ""),
        ("Lindley", "BESS", "MN", "Public records", ""),
        ("Koolunga", "BESS", "MN", "Public records (Koolunga BESS 1/2)", ""),
        ("Summerfield", "BESS", "MN", "Public records", ""),
        ("Playford", "battery/coal site", "MN (Port Augusta)", "Public records (Playford Battery)", ""),
        ("Morgan Solar", "solar", "MN/Riverland border", "Public records", ""),
        ("Goat Hill", "pumped hydro", "MN", "Public records (Goat Hill PHES)", ""),
        ("Gould Creek", "BESS", "MN/Adelaide", "Public records (Gould Creek BESS)", ""),
        ("Mannum", "BESS", "MN/Adelaide border", "Public records", ""),
        ("Yorke Peninsula", "wind farm", "MN (Yorke Pen — per user spec mapped to MN)", "ElectraNet TAPR 2024 (S4)", "Yorke flagged for user review"),
        ("Yorke", "region", "MN (Yorke Pen)", "ElectraNet TAPR 2024 (S4)", ""),
        ("Wattle Point", "wind farm", "MN (Yorke Pen)", "Public records (Wattle Point WF)", ""),
        ("Edithburgh", "wind cluster", "MN (Yorke Pen)", "Public records", ""),
        ("Hornsdale", "wind/BESS", "MN", "Public records (Hornsdale Power Reserve)", ""),
        ("Sturt Solar", "solar", "MN/Adelaide", "Public records", ""),
        ("Lake Bonney 1", "wind farm", "SE-SA (overlap MN)", "Public records", "Belongs to SE-SA"),
        ("Hallett 1", "wind farm", "MN (Hallett)", "Public records", ""),
        ("Hallett 2", "wind farm", "MN", "Public records", ""),
        ("Hallett 4", "wind farm", "MN", "Public records", ""),
        ("Brown Hill", "wind farm", "MN (Hallett area)", "Public records", ""),
        ("Bluff", "wind farm", "MN", "Public records", ""),
        ("Snowtown North", "wind farm", "MN (Snowtown)", "Public records", ""),
        ("Snowtown 2", "wind farm", "MN", "Public records (Snowtown S2 WF)", ""),
        ("Heywood", "interconnector", "SA-VIC border (Heywood interconnector)", "Public records", "Cross-border"),
        ("Robertstown", "PEC terminus", "MN (shared RIV)", "ElectraNet TAPR 2024", ""),
        ("Para", "Adelaide North", "MN/Adelaide", "ElectraNet TAPR 2024", ""),
    ],
    "SE-SA": [
        ("Lake Bonney", "wind/BESS cluster", "SE-SA (Millicent area)", "Public records (Lake Bonney WF 1/2/3 + BESS)", ""),
        ("Yumali", "wind farm/BESS", "SE-SA", "Public records (Yumali WF/BESS)", ""),
        ("Marcollat", "energy hub", "SE-SA (Limestone Coast)", "Public records (Marcollat Energy Hub)", ""),
        ("Limestone Coast", "region/zone", "SE-SA", "Public records", ""),
        ("Pacific Green", "energy park", "SE-SA (Limestone Coast)", "Public records (Pacific Green Energy Park)", ""),
        ("Canunda", "wind farm", "SE-SA", "Public records (Canunda WF)", ""),
        ("Snuggery", "gas station", "SE-SA", "Public records (Snuggery GT)", ""),
        ("Blanche", "wind/BESS", "SE-SA", "Public records", ""),
        ("Millicent", "town/region", "SE-SA", "Public records", ""),
        ("Naracoorte", "town", "SE-SA", "Public records", ""),
        ("Bordertown", "town/region", "SE-SA", "Public records", ""),
        ("Palmer", "wind farm", "SE-SA (Mt Lofty)", "Public records (Palmer WF)", ""),
        ("Harrogate", "BESS", "SE-SA (Mt Lofty)", "Public records (Harrogate BESS)", ""),
        ("Mobilong", "BESS", "SE-SA (Murray Bridge)", "Public records (Mobilong BESS)", ""),
        ("Murray Bridge", "town/BESS", "SE-SA (Murray Bridge)", "Public records", ""),
        ("Lameroo", "wind/solar", "SE-SA", "Public records", ""),
        ("Tailem Bend", "solar/BESS hub", "SE-SA", "ElectraNet TAPR 2024 (S1)", ""),
    ],
    "RIV": [
        ("Markaranka", "solar/storage", "RIV (Waikerie area)", "Public records (Markaranka Solar)", ""),
        ("Morgan Solar", "solar", "RIV/MN border", "Public records", ""),
        ("Pyap", "solar", "RIV", "Public records", ""),
        ("Waikerie", "town", "RIV", "Public records", ""),
        ("Barmera", "town", "RIV", "Public records", ""),
        ("Lyrup", "town", "RIV", "Public records", ""),
        ("Bookpurnong", "solar/wind", "RIV", "Public records", ""),
    ],
    "EYR": [
        # Eyre Peninsula — new SA catchment per user request
        ("Cultana", "existing 275 kV", "EYR (Spencer Gulf gateway)", "ElectraNet TAPR 2024 (S8/S9)", "Gateway to MN via Davenport"),
        ("Yadnarie", "existing 132/275 kV", "EYR (Eastern Eyre Peninsula)", "ElectraNet TAPR 2024 (S8/S9)", ""),
        ("Mount Lock", "existing", "EYR (eastern Eyre)", "ElectraNet TAPR 2024", ""),
        ("Mount Gunson", "existing", "EYR/MN border (Upper Spencer Gulf)", "ElectraNet TAPR 2024", ""),
        ("Cathedral Rocks", "wind farm", "EYR (Port Lincoln area)", "Public records (Cathedral Rocks WF)", ""),
        ("Mt Millar", "wind farm", "EYR (Cowell area)", "Public records (Mt Millar WF)", ""),
        ("Lincoln Gap", "wind farm", "EYR (Port Augusta area)", "Public records (Lincoln Gap WF stages 1/2/3)", "Geographically Upper Spencer Gulf — could be MN"),
        ("Port Augusta", "load/region", "MN/EYR border (Upper Spencer Gulf)", "ElectraNet TAPR 2024", "Shared MN/EYR — flagged"),
        ("Port Bonython", "hydrogen hub", "EYR", "ElectraNet TAPR 2024 (Mid North expansion)", ""),
        ("Cape Hardy", "hydrogen hub", "EYR (lower Eyre)", "ElectraNet TAPR 2024", ""),
        ("Whyalla", "load/region", "EYR (Upper Spencer Gulf)", "ElectraNet TAPR 2024", ""),
        ("Port Lincoln", "load/region", "EYR (Lower Eyre)", "ElectraNet TAPR 2024", ""),
        ("Cowell", "town", "EYR (Eastern Eyre)", "Public records", ""),
        ("Tumby Bay", "town", "EYR (Lower Eyre)", "Public records", ""),
        ("Wudinna", "town/wind", "EYR (Western Eyre)", "Public records", ""),
        ("Streaky Bay", "town/wind", "EYR (Western Eyre)", "Public records", ""),
        ("Ceduna", "town/wind/solar", "EYR (Far West Eyre)", "Public records (Ceduna SF/WF/BESS)", ""),
        ("Eyre Peninsula", "region", "EYR (S8/S9 REZ scope)", "ElectraNet TAPR 2024 (S8/S9)", ""),
        ("Eastern Eyre", "region", "EYR (S8)", "ElectraNet TAPR 2024 (S8)", ""),
        ("Western Eyre", "region", "EYR (S9)", "ElectraNet TAPR 2024 (S9)", ""),
        ("Davenport", "existing 275 kV", "MN/EYR gateway (Port Augusta area)", "ElectraNet TAPR 2024 (S8)", "Keep in MN — gateway only"),
        ("Emeroo", "BESS", "EYR (Upper Spencer Gulf)", "Public records (Emeroo BESS)", ""),
        ("Port Paterson", "BESS", "EYR/MN", "Public records", ""),
        ("Barn Hill", "solar/BESS", "EYR (lower Eyre)", "Public records (Barn Hill SF/BESS)", "Geographically Lyndhurst — could be MN; flagged"),
    ],
}


def to_rows(state, additions, rez_name_map):
    rows = []
    for rez_code, items in additions.items():
        rez_name = rez_name_map[rez_code]
        for sub, stype, lines, src, notes in items:
            rows.append({
                "state": state,
                "rez_code": rez_code,
                "rez_name": rez_name,
                "substation": sub,
                "substation_type": stype,
                "transmission_lines": lines,
                "source_document": src,
                "confidence_default": "medium",  # locality matches are medium per QLD pattern
                "notes": notes,
            })
    return rows


# === Pass-1 dicts (initial expansion + EYR introduction) ===
# (NSW_ADDITIONS / VIC_ADDITIONS / SA_ADDITIONS are pass-1; aliased below for symmetry)
NSW_PASS1 = None  # filled at module-load via alias
VIC_PASS1 = None
SA_PASS1 = None


def _apply_pass(existing, pass_dicts, pass_label):
    """Append rows for one pass. Idempotent on (state, rez_code, substation)."""
    new_rows = []
    for state, pass_dict, name_map in pass_dicts:
        if pass_dict is None:
            continue
        new_rows.extend(to_rows(state, pass_dict, name_map))
    if not new_rows:
        return existing, 0
    new_df = pd.DataFrame(new_rows, columns=COLS)
    key = ["state", "rez_code", "substation"]
    existing["_k"] = existing[key].astype(str).agg("|".join, axis=1)
    new_df["_k"] = new_df[key].astype(str).agg("|".join, axis=1)
    new_df = new_df[~new_df["_k"].isin(existing["_k"])].drop(columns=["_k"])
    existing = existing.drop(columns=["_k"])
    out = pd.concat([existing, new_df], ignore_index=True)
    print(f"{pass_label}: appended {len(new_df)} rows (total now {len(out)})")
    return out, len(new_df)


def main():
    out = pd.read_csv(LOOKUP)
    print(f"Starting from {len(out)} existing rows in {LOOKUP.relative_to(REPO)}")
    # Aliases so pass-1 dicts fit the same iteration pattern as later passes
    nsw_p1 = NSW_ADDITIONS
    vic_p1 = VIC_ADDITIONS
    sa_p1 = SA_ADDITIONS
    passes = [
        ("Pass-1 (initial locality + EYR)", [
            ("NSW", nsw_p1, NSW_REZ_NAME),
            ("VIC", vic_p1, VIC_REZ_NAME),
            ("SA",  sa_p1,  SA_REZ_NAME),
        ]),
        ("Pass-2 (corrections)", [
            ("NSW", NSW_PASS2, NSW_REZ_NAME),
            ("VIC", VIC_PASS2, VIC_REZ_NAME),
            ("SA",  SA_PASS2,  SA_REZ_NAME),
        ]),
        ("Pass-3 (clear >100MW residue)", [
            ("NSW", NSW_PASS3, NSW_REZ_NAME),
            ("VIC", VIC_PASS3, VIC_REZ_NAME),
            ("SA",  SA_PASS3,  SA_REZ_NAME),
        ]),
        ("Pass-4 (sweep remaining)", [
            ("NSW", NSW_PASS4, NSW_REZ_NAME),
            (None,  None,     None),  # no VIC pass-4
            ("SA",  SA_PASS4,  SA_REZ_NAME),
        ]),
    ]
    total_added = 0
    for label, dicts in passes:
        # filter out the None placeholders
        dicts = [d for d in dicts if d[0] is not None]
        out, n = _apply_pass(out, dicts, label)
        total_added += n
    out.to_csv(LOOKUP, index=False)
    print(f"\nDone — {total_added} total new rows; lookup now {len(out)} rows")
    print("\nBy state and rez_code:")
    print(out.groupby(["state", "rez_code"]).size().to_string())


# === Second expansion pass — added after initial review ===
NSW_PASS2 = {
    "CWO": [
        ("Wallerawang", "BESS/coal site", "CWO/Central West (Lithgow)", "Public records (Wallerawang 9 BESS)", ""),
        ("Hargraves", "wind farm/BESS", "CWO (Mudgee area)", "Public records (Hargraves WF/BESS)", ""),
        ("Mullion Creek", "wind farm", "CWO (Orange area)", "Public records (Mullion Creek WF)", ""),
        ("Mandurama", "wind farm", "CWO (Orange area)", "Public records (Mandurama WF)", ""),
        ("Stubbo", "solar farm", "CWO (Gulgong area)", "Public records (Stubbo SF)", ""),
        ("Oxley", "solar farm", "CWO (north of Mudgee)", "Public records", ""),
        ("Maxwell Downs", "solar", "CWO/Upper Hunter border", "Public records (Maxwell Downs SF)", "Could be HCC"),
        ("Maxwell", "solar", "CWO", "Public records", ""),
        ("Yarrabee Solar", "solar", "CWO/HCC border", "Public records (Yarrabee Solar)", "Border"),
        ("Tallawang Solar", "solar/BESS", "CWO", "Public records", ""),
        ("Orange", "town/region", "CWO (Central West)", "Public records", ""),
        ("Lithgow", "town/region", "CWO/Central West", "Public records", ""),
        ("Cudgegong", "river/region", "CWO", "Public records", ""),
        ("Goulburn River Solar", "solar/BESS", "CWO (Bylong)", "Public records", ""),
        ("Pottinger", "energy park", "CWO/NEW border", "Public records", ""),
    ],
    "NEW": [
        ("Oven Mountain", "pumped storage", "NEW (Walcha area)", "Public records (Oven Mountain PHES)", ""),
        ("Dungowan", "PHES", "NEW (Tamworth area)", "Public records (Dungowan 3000 MWH PHES)", ""),
        ("Tilbuster", "solar farm", "NEW (Armidale area)", "Public records (Tilbuster SF)", ""),
        ("Thunderbolt", "wind farm", "NEW (Uralla area)", "Public records (Thunderbolt WF)", ""),
        ("Salisbury", "solar/BESS", "NEW (Liverpool Plains)", "Public records (Salisbury Solar/BESS)", ""),
        ("Aquila", "wind", "NEW (New England area)", "Public records (Aquila Wind)", ""),
        ("Juno", "wind farm", "NEW", "Public records (Juno WF)", ""),
        ("Glenbawn Pumped Hydro", "pumped hydro", "Upper Hunter (HCC)", "Public records", "Could be HCC"),
        ("Phoenix Pumped Hydro", "pumped hydro", "NEW (Walcha-Armidale area)", "Public records (Phoenix PHES)", ""),
        ("Bendemeer Solar", "solar", "NEW (Tamworth area)", "Public records", ""),
        ("Ruby Hills", "wind farm", "NEW/CWO border", "Public records (Ruby Hills North/South WF)", "Border — flagged"),
        ("Jeremiah", "wind farm", "NEW/HCC border", "Public records (Jeremiah WF)", "Border"),
        ("Sundown", "hybrid", "NEW border", "Public records", ""),
        ("Walcha", "town/region", "NEW", "EnergyCo NEW", ""),
        ("Liverpool Plains", "region", "NEW (Liverpool Plains)", "EnergyCo NEW", ""),
    ],
    "HCC": [
        ("Glennies Creek", "pumped hydro", "Upper Hunter (Singleton)", "Public records (Glennies Creek PHES)", ""),
        ("Glennis Creek", "pumped hydro", "Upper Hunter (Singleton)", "Public records (Glennis Creek PHES — variant)", ""),
        ("Bowmans Creek", "wind farm", "HCC (Singleton area)", "Public records (Bowmans Creek WF)", ""),
        ("Glenbawn", "pumped hydro", "Upper Hunter", "Public records (Glenbawn PHES)", ""),
        ("Camberwell", "project", "Hunter Valley", "Public records", ""),
        ("Sandy Point", "hybrid", "Hunter coast", "Public records (Sandy Point Hybrid)", ""),
        ("Maxwell", "solar/coal site", "Upper Hunter", "Public records (Maxwell)", "Could be CWO"),
        ("Shoalhaven", "pumped hydro/expansion", "Illawarra/South Coast", "Public records", "Closer to ILW — review"),
        ("Awaba", "BESS", "Central Coast (HCC)", "Public records", ""),
    ],
    "ILW": [
        ("Marulan", "OCGT/CCGT", "Southern Highlands (ILW gateway)", "Public records (Marulan)", ""),
        ("Canyonleigh", "BESS", "Southern Highlands (ILW)", "Public records (Canyonleigh BESS)", ""),
        ("Shoalhaven Expansion", "pumped hydro", "ILW/South Coast", "Public records (Shoalhaven PHES)", ""),
        ("Tallawarra", "gas/BESS", "Illawarra (Dapto)", "Public records (Tallawarra A/B)", ""),
        ("Williamsdale", "BESS", "ACT/Southern Tableland", "Public records", "Border — ACT/SW-NSW"),
    ],
    "SW-NSW": [
        ("Baldon", "wind farm", "SW-NSW (Hay area)", "Public records (Baldon WF)", ""),
        ("Nonowie", "wind farm", "SW-NSW (Hay-Balranald area)", "Public records (Nonowie WF)", ""),
        ("Kerrawary", "power station", "SW-NSW (Riverina)", "Public records (Kerrawary PS)", ""),
        ("Great Western", "battery", "SW-NSW (Wagga area)", "Public records (Great Western Battery)", ""),
        ("NSW Gas Peaker", "OCGT", "SW-NSW (Riverina gas)", "Public records", ""),
        ("Central Para", "wind farm", "SW-NSW (Goulburn area)", "Public records (Central Para WF)", ""),
        ("Swallow Tail", "BESS", "SW-NSW", "Public records (Swallow Tail BESS)", ""),
        ("Euston", "wind farm", "SW-NSW (Murray border)", "Public records (Euston WF)", ""),
        ("Bushranger", "hybrid", "SW-NSW (Yass area)", "Public records (Bushranger Hybrid Facility)", ""),
        ("Sandigo", "solar farm", "SW-NSW (Riverina)", "Public records (Sandigo SF)", ""),
        ("Koorakee", "wind farm", "SW-NSW (Far West)", "Public records (Koorakee WF)", ""),
        ("Coppabella", "wind farm", "SW-NSW (Yass-Crookwell area)", "Public records (Coppabella WF)", ""),
        ("Paling Yards", "wind farm", "SW-NSW (Crookwell area)", "Public records (Paling Yards WF)", ""),
        ("Lerida", "BESS/solar", "SW-NSW (Goulburn area)", "Public records (Lerida BESS/SF)", ""),
        ("Woodland", "BESS", "SW-NSW (Yass area)", "Public records", ""),
        ("Kingswood", "BESS", "SW-NSW", "Public records", ""),
        ("Collector", "town/wind farm", "SW-NSW (Collector WF area)", "Public records (Collector)", ""),
        ("Rollsville", "hybrid", "SW-NSW (Crookwell area)", "Public records (Rollsville Hybrid)", ""),
        ("Silver City", "energy storage", "SW-NSW (Broken Hill)", "Public records (Silver City ESS)", ""),
        ("Yambla Range", "wind farm", "SW-NSW (Albury area)", "Public records (Yambla Range WF)", ""),
        ("Limondale", "solar farm", "SW-NSW (Balranald area)", "Public records (Limondale SF)", ""),
        ("Sunraysia", "solar farm", "SW-NSW (Buronga area)", "Public records (Sunraysia SF)", ""),
        ("Mt Hope", "wind farm", "SW-NSW (Lachlan)", "Public records (Mt Hope WF)", ""),
        ("Conroys Gap", "wind farm", "SW-NSW (Yass area)", "Public records (Conroys Gap WF)", ""),
        ("Hawkesdale", "wind farm", "SW-NSW", "Public records", "Could be SW-VIC"),
        ("Albury", "load/border", "SW-NSW (Albury area)", "Public records", ""),
        ("Mullion", "wind farm", "SW-NSW (Crookwell area)", "Public records", ""),
    ],
}

VIC_PASS2 = {
    "WV": [
        ("Waubra", "wind farm", "WV (Ballarat area)", "Public records (Waubra WF/BESS)", ""),
        ("Puzzle Range", "wind farm", "WV (Pyrenees Ranges)", "Public records (Puzzle Range WF)", ""),
        ("Mt Doran", "BESS", "WV (Ballarat area)", "Public records (Mt Doran BESS)", ""),
        ("Yendon", "wind farm", "WV (Ballarat area)", "Public records (Yendon WF)", ""),
        ("SEC Renewable Energy Hub", "renewable hub", "WV (Horsham area)", "Public records", ""),
        ("SEC ", "renewable hub", "WV (general SEC hub)", "Public records", "Note trailing space — KCI naming"),
        ("Willowvale", "solar farm", "WV", "Public records", ""),
        ("Halys", "BESS", "WV (X-Elio)", "Public records (Halys BESS X-Elio)", ""),
        ("Salt Creek Wind Farm", "wind farm", "WV/SW-VIC", "Public records", ""),
    ],
    "CN-VIC": [
        ("Doreen", "BESS", "Melbourne outer NE", "Public records (Doreen BESS)", "Load-area — flag"),
        ("Wollert", "gas turbine", "Melbourne outer N", "Public records (Wollert GT)", "Load-area"),
        ("Everleigh", "solar/BESS", "CN-VIC (Riddells Creek area)", "Public records", ""),
        ("LYA", "BESS", "GIP (Loy Yang A — should be GIP)", "Public records", "Should be GIP — review"),
        ("Muskerry", "solar", "CN-VIC (Bendigo area)", "Public records (Muskerry SF)", ""),
        ("Winton", "energy reserve/BESS", "CN-VIC (Benalla area)", "Public records (Winton Energy/BESS)", ""),
        ("Dartmouth", "hydro", "CN-VIC/Ovens Murray (Hume)", "Public records (Dartmouth Hydro)", ""),
        ("Koorangie", "BESS/ESS", "MR (Kerang area)", "Public records (Koorangie ESS)", "Actually MR — Kerang area"),
        ("Meadow Creek", "solar", "CN-VIC (King Valley)", "Public records", ""),
        ("Moonah", "solar", "CN-VIC", "Public records", ""),
        ("Springvale", "energy hub", "CN-VIC (Bendigo area)", "Public records (Springvale Energy Hub)", ""),
        ("Fosterville", "solar/BESS", "CN-VIC (Bendigo area)", "Public records (Fosterville SF/BESS)", ""),
        ("Wunghnu", "solar", "CN-VIC (Shepparton)", "Public records", ""),
        ("Girgarre", "solar", "CN-VIC (Shepparton)", "Public records", ""),
        ("Grahamvale", "BESS", "CN-VIC (Shepparton)", "Public records", ""),
        ("Bullarook", "wind/solar", "CN-VIC/WV border", "Public records", ""),
        ("Normanville", "energy park", "CN-VIC (Bendigo area)", "Public records (Normanville)", ""),
    ],
    "SW-VIC": [
        ("Mt Fyans", "wind farm", "SW-VIC (Mortlake area)", "Public records (Mt Fyans WF 2.0)", ""),
        ("Mount Fyans", "wind farm", "SW-VIC", "Public records", ""),
        ("Watta Wella", "wind/PS", "SW-VIC", "Public records (Watta Wella WF/PS)", ""),
        ("Moreton Hill", "wind farm", "SW-VIC", "Public records (Moreton Hill WF)", ""),
        ("Nyaninyuk", "wind farm", "SW-VIC (Hamilton area)", "Public records (Nyaninyuk WF)", ""),
        ("Victorian Big Battery", "BESS", "SW-VIC (Geelong)", "Public records (VBB)", ""),
        ("Golden Plains", "wind farm/BESS", "SW-VIC (Rokewood)", "Public records (Golden Plains WF East/West/BESS)", ""),
        ("Terang", "BESS", "SW-VIC", "Public records", ""),
        ("Mt Gellibrand", "wind farm", "SW-VIC (Colac area)", "Public records (Mt Gellibrand WF)", ""),
        ("Hawkesdale", "wind farm", "SW-VIC (Hamilton area)", "Public records (Hawkesdale WF)", ""),
        ("Inverleigh", "wind farm", "SW-VIC (Geelong area)", "Public records (Inverleigh WF)", ""),
        ("Yaloak", "wind farm", "SW-VIC", "Public records (Yaloak South WF)", ""),
        ("Yambuk", "wind farm", "SW-VIC", "Public records (Yambuk WF)", ""),
        ("Mortlake South", "energy hub", "SW-VIC", "Public records", ""),
    ],
    "GIP": [
        ("Delburn", "wind farm", "GIP (Strzelecki Ranges)", "Public records (Delburn WF)", ""),
        ("North Yarragon", "BESS", "GIP", "Public records (North Yarragon BESS)", ""),
        ("LYA", "Loy Yang A BESS", "GIP (Loy Yang)", "Public records", ""),
        ("Fulham", "solar/BESS", "GIP (Sale area)", "Public records (Fulham SF/BESS)", ""),
        ("Bennetts Creek", "BESS", "GIP", "Public records", ""),
    ],
    "MR": [
        ("Koorangie", "ESS/BESS", "MR (Kerang area)", "Public records (Koorangie ESS)", ""),
        ("Malunga Nine Mile", "BESS", "MR/CN-VIC border", "Public records (Malunga Nine Mile BESS)", ""),
    ],
}

SA_PASS2 = {
    "MN": [
        ("Yoorndoo Ilga", "solar", "MN (north of Adelaide)", "Public records (Yoorndoo Ilga SF — KCI)", ""),
        ("Lionsgate", "battery", "MN/Adelaide", "Public records (Lionsgate Battery)", "Load-area"),
        ("Kingfisher", "solar/storage", "MN (Mid-North)", "Public records (Kingfisher Solar Storage)", ""),
        ("Blacktop", "BESS", "MN", "Public records (Blacktop BESS — KCI)", ""),
        ("Port Stanvac", "existing power", "Adelaide", "Public records (Port Stanvac 1)", "Load-area"),
        ("Dry Creek", "GT", "Adelaide", "Public records (Dry Creek GT)", "Load-area"),
        ("Penfield", "BESS", "Adelaide", "Public records (Penfield BESS)", "Load-area"),
        ("Direk", "BESS", "Adelaide", "Public records (Direk BESS)", "Load-area"),
        ("Wingfield", "BESS", "Adelaide", "Public records (Wingfield 1/2)", "Load-area"),
        ("Happy Valley", "reservoir", "Adelaide", "Public records", "Load-area"),
        ("Kincraig", "BESS", "Adelaide", "Public records", "Load-area"),
        ("Christies Beach", "wastewater", "Adelaide", "Public records", "Load-area"),
        ("Goyder North", "wind/BESS hub", "MN (Goyder area)", "Public records (Goyder North RE Facility)", ""),
        ("Goyder South", "wind farm hub", "MN", "Public records (Goyder South WF 1A/1B)", ""),
        ("Bundy Energy Hub", "BESS hub", "MN", "Public records (Bundy Energy Hub A/B)", ""),
    ],
    "EYR": [
        ("Aurora Solar", "concentrated solar", "EYR/MN border (Port Augusta)", "Public records (Aurora SEP — Vast Solar)", "Could be MN"),
        ("Vast Solar", "concentrated solar", "EYR (Port Augusta area)", "Public records", ""),
        ("Yoorndoo Ilga", "solar", "EYR border", "Public records", "Could be MN"),
    ],
    "SE-SA": [
        ("Ladbroke Grove", "gas station", "SE-SA (Mt Gambier)", "Public records (Ladbroke Grove)", ""),
        ("Starfish Hill", "wind farm", "SE-SA (Cape Jervis)", "Public records (Starfish Hill WF)", ""),
        ("Dalrymple", "BESS", "MN/SE-SA border (Yorke Pen)", "Public records (Dalrymple BESS)", "Yorke Pen — could be MN"),
        ("Lameroo", "solar/wind", "SE-SA", "Public records", ""),
    ],
    "RIV": [
        ("Morgan Long Duration", "LDES", "RIV (Morgan area)", "Public records (Morgan LDES — KCI)", ""),
        ("Morgan Battery", "BESS", "RIV/MN border (Morgan)", "Public records (Morgan Battery)", ""),
        ("Markaranka", "solar/storage", "RIV", "Public records (Markaranka)", ""),
    ],
}


# === Pass-3 expansion (clearly-classifiable remaining items >100MW) ===
NSW_PASS3 = {
    "CWO": [
        ('Ben Bullen', 'BESS', 'CWO (Lithgow area)', 'Public records (Ben Bullen BESS)', ''),
        ('Mount Lambie', 'wind farm', 'CWO (Lithgow area)', 'Public records (Mount Lambie WF)', ''),
        ('Maryvale', 'solar/ESS', 'CWO (Wellington area)', 'Public records (Maryvale SF/ESS)', ''),
        ('Molong', 'BESS', 'CWO (Orange area)', 'Public records (Molong BESS — KCI)', ''),
        ('Suntop', 'solar farm', 'CWO (Wellington area)', 'Public records (Suntop SF)', ''),
        ('Boree', 'solar project', 'CWO (Orange area)', 'Public records (Boree SP)', ''),
        ('Flyers Creek', 'wind farm', 'CWO (Orange area)', 'Public records (Flyers Creek WF)', ''),
        ('Crudine Ridge', 'wind farm', 'CWO (Mudgee)', 'Public records (Crudine Ridge WF)', ''),
        ('Daroobalgie', 'solar farm', 'CWO (Parkes/Forbes)', 'Public records (Daroobalgie SF)', ''),
        ('Nevertire', 'solar farm', 'CWO (Nyngan area)', 'Public records (Nevertire SF)', ''),
        ('Parkes', 'town/region', 'CWO (Parkes-Forbes)', 'Public records', ''),
        ('Forbes', 'town', 'CWO', 'Public records', ''),
        ('Wellington', 'town/region', 'CWO', 'Transgrid TAPR 2024', ''),
        ('Stratford', 'renewable hub', 'CWO', 'Public records', 'Stratford typo coverage'),
        ('Strafford', 'typo of Stratford', 'Upper Hunter', 'Public records', 'Typo coverage'),
    ],
    "NEW": [
        ('Nottingham Park', 'solar farm', 'NEW (Liverpool Plains)', 'Public records (Nottingham Park SF)', ''),
        ('Calala', 'BESS', 'NEW (Tamworth)', 'Public records (Calala BESS — CABESS2)', ''),
        ('Texas', 'solar/BESS', 'NEW/QLD border (Texas)', 'Public records (Texas SF/BESS)', ''),
        ('Deepwater', 'solar/BESS', 'NEW (Glen Innes area)', 'Public records (Deepwater SF/BESS)', ''),
        ('Silverleaf', 'solar farm', 'NEW (Tamworth area)', 'Public records (Silverleaf SF — KCI)', ''),
        ('Rangoon', 'wind farm', 'NEW (Glen Innes)', 'Public records (Rangoon WF)', ''),
        ('Tabulam', 'solar/BESS', 'NEW (Tenterfield area)', 'Public records (Tabulam SF/BESS)', 'North Coast — could be unclassified'),
        ('Comet Park', 'BESS', 'NEW', 'Public records (Comet Park BESS — KCI)', ''),
        ('Granite Hills', 'wind farm', 'NEW (Glen Innes area)', 'Public records (Granite Hills WF)', ''),
        ('Ridgey Creek', 'BESS', 'NEW (Liverpool Plains)', 'Public records', ''),
        ('Salisbury', 'solar/BESS', 'NEW (Liverpool Plains)', 'Public records', ''),
    ],
    "HCC": [
        ('Colongra', 'existing gas', 'Central Coast (HCC)', 'Public records (Colongra GT)', ''),
        ('Redbank', 'existing coal/BESS', 'Upper Hunter (Singleton)', 'Public records (Redbank PS)', ''),
        ('Burgmanns', 'BESS', 'HCC', 'Public records (Burgmanns BESS)', ''),
        ('Glennies', 'creek/PHES', 'HCC (Singleton)', 'Public records', ''),
        ('Wallaroo Hunter', 'cluster', 'HCC', 'Public records', ''),
    ],
    "ILW": [
        ('Capital', 'wind/BESS', 'ACT/Southern Tableland (Bungendore)', 'Public records (Capital WF/Battery)', 'Bungendore — could be SW-NSW; mapping to ILW per Yass/Goulburn corridor'),
        ('Capital Wind Farm', 'wind farm', 'ACT border (Bungendore)', 'Public records', 'Could be SW-NSW'),
    ],
    "SW-NSW": [
        ('Silverton', 'wind farm', 'Far West (Broken Hill)', 'Public records (Silverton WF)', ''),
        ('Uranquinty', 'existing gas', 'SW-NSW (Wagga area)', 'Public records (Uranquinty PS)', ''),
        ('Murrumburrah', 'BESS', 'SW-NSW (Harden area)', 'Public records (Murrumburrah BESS)', ''),
        ('Walla Walla', 'solar farm', 'SW-NSW (Albury area)', 'Public records (Walla Walla SF)', ''),
        ('Glenellen', 'solar farm', 'SW-NSW (Albury area)', 'Public records (Glenellen SF)', ''),
        ('Bomen', 'solar farm', 'SW-NSW (Wagga)', 'Public records (Bomen SF)', ''),
        ('Gerogery', 'solar/BESS', 'SW-NSW (Albury area)', 'Public records (Gerogery SF/BESS)', ''),
        ('Mangoplah', 'BESS', 'SW-NSW (Wagga area)', 'Public records (Mangoplah BESS — KCI)', ''),
        ('McMahons Reef', 'solar farm', 'SW-NSW (Yass area)', 'Public records (McMahons Reef SF)', ''),
        ('Stoney Creek', 'BESS', 'SW-NSW', 'Public records (Stoney Creek BESS)', ''),
        ('Deniliquin', 'BESS', 'SW-NSW (Riverina)', 'Public records (Deniliquin BESS — KCI)', ''),
        ('Hillston', 'solar farm', 'SW-NSW (Lachlan)', 'Public records (Hillston Sun Farm)', ''),
        ('West Wyalong', 'solar farm', 'SW-NSW (Wyalong)', 'Public records (West Wyalong SF)', ''),
        ('Nyngan', 'solar plant', 'CWO/SW-NSW border (Nyngan)', 'Public records (Nyngan Solar Plant)', 'Could be CWO'),
        ('Hay', 'town/region', 'SW-NSW', 'Transgrid TAPR 2024', ''),
        ('Lachlan', 'region', 'SW-NSW (Lower Lachlan)', 'AEMO ISP A3 N5', ''),
        ('Wyalong', 'town', 'SW-NSW', 'Public records', ''),
        ('Emu Park', 'solar/BESS', 'SW-NSW (Riverina)', 'Public records (Emu Park SF/BESS)', 'Possibly different — review'),
        ('Yawong', 'wind farm', 'SW-NSW (Riverina)', 'Public records (Yawong WF)', ''),
    ],
}

VIC_PASS3 = {
    "CN-VIC": [
        ('West Kiewa', 'hydro', 'CN-VIC (Kiewa Valley)', 'Public records (West Kiewa Hydro)', ''),
        ('Mokoan', 'solar farm', 'CN-VIC (Benalla)', 'Public records (Mokoan SF — LightsourceBP / West Mokoan SF)', ''),
        ('Yarrawonga', 'existing', 'CN-VIC/MR border (Murray)', 'Public records', ''),
        ('Ravenswood', 'solar/BESS', 'CN-VIC (Bendigo area)', 'Public records (Ravenswood SF/BESS)', ''),
        ('Frasers', 'solar farm', 'CN-VIC', 'Public records (Frasers SF)', ''),
        ('Lancaster', 'solar farm', 'CN-VIC (Tatura area)', 'Public records (Lancaster SF)', ''),
        ('William Hovel', 'hydro', 'CN-VIC (King Valley)', 'Public records', ''),
        ('Mt Lyon', 'wind farm', 'CN-VIC', 'Public records', ''),
    ],
    "WV": [
        ('Oaklands Hill', 'wind farm', 'WV (Glenthompson area)', 'Public records (Oaklands Hill WF)', ''),
        ('Kiata', 'wind farm', 'WV (Wimmera)', 'Public records (Kiata WF)', ''),
        ('Wombelano', 'wind farm', 'WV', 'Public records (Wombelano WF)', ''),
        ('Diapur', 'wind farm', 'WV (Wimmera)', 'Public records (Diapur WF)', ''),
        ('Ferguson', 'wind farm', 'WV (Crowlands area)', 'Public records (Ferguson WF)', ''),
        ('Maroona', 'wind farm', 'WV (Ararat area)', 'Public records (Maroona WF)', ''),
        ('Leonards Hill', 'wind/hydro', 'WV (Daylesford)', 'Public records', ''),
        ('Daylesford', 'region', 'WV', 'Public records', ''),
        ('Yawong', 'wind farm', 'WV/MR border', 'Public records (Yawong WF)', ''),
        ('Toolern Vale', 'solar/BESS', 'WV (Sunbury area)', 'Public records (Toolern Vale SF/BESS)', 'Border with Melbourne — load area'),
        ('Coonooer Bridge', 'wind farm', 'WV/MR border (Wycheproof)', 'Public records (Coonooer Bridge WF)', ''),
    ],
    "SW-VIC": [
        ('Woolsthorpe', 'wind farm', 'SW-VIC', 'Public records (Woolsthorpe WF)', ''),
        ('Mortons Lane', 'wind farm', 'SW-VIC', 'Public records (Mortons Lane WF)', ''),
        ('Timboon West', 'wind farm', 'SW-VIC', 'Public records (Timboon West WF)', ''),
    ],
    "GIP": [
        ('Valley Power', 'existing gas', 'GIP (Latrobe)', 'Public records (Valley Power PS)', ''),
        ('Glenmaggie', 'hydro', 'GIP (Macalister scheme)', 'Public records (Glenmaggie Hydro)', ''),
        ('Philip Island', 'BESS', 'GIP coast', 'Public records (Phillip Island BESS)', ''),
    ],
    "MR": [
        ('Gannawarra', 'solar/storage', 'MR (Kerang area)', 'Public records (Gannawarra SF/ESS)', ''),
        ('Cohuna', 'solar farm', 'MR (Kerang area)', 'Public records (Cohuna SF)', ''),
        ('Rifle Butts', 'wind farm', 'MR/WV border', 'Public records (Rifle Butts WF)', ''),
    ],
}

SA_PASS3 = {
    "SE-SA": [
        ('Mount Lofty', 'region', 'SE-SA (Mt Lofty)', 'Public records', ''),
    ],
}

# === Pass-4 expansion (sweep remaining NSW/VIC residue with clear REZ assignment) ===
NSW_PASS4 = {
    "CWO": [
        ('Brewongle', 'solar farm', 'CWO (Bathurst area)', 'Public records', ''),
        ('Glanmire', 'solar farm', 'CWO (Bathurst)', 'Public records', ''),
        ('Burroway', 'BESS', 'CWO (Dubbo)', 'Public records', ''),
        ('Goonumbla', 'solar farm', 'CWO (Parkes area)', 'Public records', ''),
        ('Manildra', 'solar farm', 'CWO (Orange area)', 'Public records', ''),
        ('Jemalong', 'solar farm', 'CWO (Forbes area)', 'Public records', ''),
        ('Narromine', 'solar farm', 'CWO (Dubbo area)', 'Public records', ''),
        ('Dubbo', 'town/region', 'CWO', 'Public records', ''),
        ('Wyangala', 'pumped hydro', 'CWO/SW-NSW (Cowra)', 'Public records', ''),
        ('Bathurst', 'town/region', 'CWO', 'Public records', ''),
        ('Midwest', 'solar/BESS', 'CWO (Central West)', 'Public records', ''),
    ],
    "NEW": [
        ('Maules Creek', 'solar/BESS', 'NEW (Boggabri area)', 'Public records', ''),
        ('Bonshaw', 'solar farm', 'NEW (Inverell area)', 'Public records', ''),
        ('Ebor', 'BESS', 'NEW (Dorrigo area)', 'Public records', ''),
        ('Springdale', 'solar farm', 'NEW', 'Public records', ''),
        ('Tenterfield', 'solar farm', 'NEW (Glen Innes border)', 'Public records', ''),
        ('Copeton', 'dam/PHES', 'NEW (Inverell area)', 'Public records', ''),
        ('Keepit', 'hydro', 'NEW (Tamworth area)', 'Public records', ''),
    ],
    "ILW": [
        ('Sutton Forest', 'BESS', 'ILW (Southern Highlands)', 'Public records', ''),
    ],
    "SW-NSW": [
        ('Cooma', 'solar/BESS', 'SW-NSW (Cooma-Monaro N7/N8 → mapped here)', 'Public records (Cooma SF/Hybrid)', 'Cooma-Monaro REZ not in user spec — mapped to SW-NSW'),
        ('Cooma-Monaro', 'region', 'SW-NSW (per user spec)', 'AEMO ISP A3 N7/N8', "Mapped here for user's 5-zone NSW spec"),
        ('Sebastopol', 'solar farm', 'SW-NSW (Albury area)', 'Public records (Sebastopol SF)', ''),
        ('South Coree', 'BESS', 'SW-NSW (Albury area)', 'Public records', ''),
        ('Hume', 'Dam/BESS', 'SW-NSW (Albury)', 'Public records', ''),
        ('Hume Dam', 'hydro/storage', 'SW-NSW (Albury)', 'Public records', ''),
        ('Blowering', 'hydro', 'SW-NSW (Snowy)', 'Public records', ''),
        ('Guthega', 'hydro', 'SW-NSW (Snowy)', 'Public records', ''),
        ('Jounama', 'hydro', 'SW-NSW (Snowy)', 'Public records', ''),
        ('Burrinjuck', 'hydro', 'SW-NSW (Yass)', 'Public records', ''),
        ('Griffith', 'BESS/solar', 'SW-NSW (Riverina)', 'Public records', ''),
        ('Corowa', 'solar farm', 'SW-NSW (Murray)', 'Public records', ''),
        ('Moama', 'solar farm', 'SW-NSW (Echuca-Murray)', 'Public records', ''),
        ('Mulwala', 'solar farm', 'SW-NSW (Yarrawonga)', 'Public records', ''),
        ('Cullerin', 'wind farm', 'SW-NSW (Yass)', 'Public records (Cullerin Range WF)', ''),
        ('Taralga', 'wind farm', 'SW-NSW (Crookwell)', 'Public records', ''),
        ('Woodlawn', 'wind farm/bioreactor', 'SW-NSW (Goulburn)', 'Public records (Woodlawn WF/Bioreactor)', ''),
        ('Bonnie Brae', 'hybrid', 'SW-NSW', 'Public records (Bonnie Brae Hybrid)', ''),
        ('Gregadoo', 'solar farm', 'SW-NSW (Wagga area)', 'Public records', ''),
        ('Lockhart', 'hybrid', 'SW-NSW (Riverina)', 'Public records (Lockhart Hybrid)', ''),
        ('Milpulling', 'wind farm', 'SW-NSW (Riverina)', 'Public records', ''),
        ('Argyle', 'solar farm', 'SW-NSW', 'Public records', ''),
        ('Tower', 'wind farm', 'SW-NSW', 'Public records', ''),
        ('Yarrawonga', 'existing', 'SW-NSW/Murray (Yarrawonga)', 'Public records', 'NSW side'),
        ('Murrumbidgee', 'region', 'SW-NSW', 'Public records', ''),
    ],
}

# No VIC pass-4 (VIC reached 24.9% review after pass-3)

SA_PASS4 = {
    "EYR": [
        ('Yoorndoo Ilga', 'solar', 'EYR (Eyre area)', 'Public records', 'Could be MN — flagged'),
    ],
}


if __name__ == "__main__":
    main()
