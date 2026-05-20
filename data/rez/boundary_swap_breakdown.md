# Boundary-swap breakdown by Method 1 confidence (56 cases)

Boundary swaps = M1 and M2 assign *adjacent* REZ corridors. The right tie-break
depends on how strong M1's keyword anchor was. Split:

| M1 confidence | n | Suspected winner | Rationale |
|---|---:|---|---|
| **high** | 1 | **Method 1** | keyword anchored to a specific REZ; M2 was a far stretch |
| **medium** | 37 | mixed (see sub-split) | depends on M2 distance |
| **review** | 18 | **Method 2** | keyword was weak/ambiguous — exactly what spatial fixes |

## M1 high (1) — keep Method 1
- **Riverland Solar Storage - Solar**: M1 RIV (keyword `Riverland`, high) → M2 MN
  @ **42.7 km** (medium). The project is ~6 km NE of Morgan (Riverland/MN
  border); M1's high-confidence `Riverland` anchor is defensible, and M2's MN is
  a 42 km reach to the nearest geocoded MN substation (no Riverland substation
  with coords nearby). **Keep M1 (RIV).** This is the one case where a confident
  keyword beats a distant spatial match.

## M1 medium (37) — sub-split by M2 distance
**M2 high-confidence: 21 → prefer Method 2.** When the coord lands
within 20 km of a substation in the adjacent REZ, topology wins. Clear examples:
- Lovely Banks REH ×2: WV → **SW-VIC** (Moorabool TS @ 0.2 km) — M2 right.
- McCullys Gap BESS: NEW → **HCC** (Muswellbrook @ 1.1 km) — Upper Hunter, M2 right.
- Mannum Solar Farm: MN → **SE-SA** (Mobilong @ 2.4 km) — Murray Bridge, M2 right.
- Wongalea BESS: CWO → **NEW** (3.3 km); Bellambi Heights: NEW → **CWO** (3.4 km);
  Oxley SF: CWO → **NEW** (6.1 km); Blind Creek SF: SW-NSW → **ILW** (5.3 km);
  Swallow Tail BESS: SW-NSW → **ILW** (5.1 km); Murray 1/2: CN-VIC → **MR** (2-5 km);
  Barn Hill BESS: EYR → **MN** (9 km); Goat Hill PHES: MN → **EYR** (9 km).

**M2 medium/far: 16 → flag for review.** The adjacent-REZ call is
genuinely uncertain because the nearest substation is far:
- Aquila Wind/Wind Farm: NEW → CWO @ 31-35 km
- Phoenix PHES: NEW → CWO @ 33 km; Strafford REH: CWO → HCC @ 24 km
- Western Sydney PHES: ILW → SW-NSW @ 31 km; Prairie SF: CN-VIC → MR @ 37 km
- Mologa BESS: CN-VIC → MR @ 31 km; Puzzle Range WF: WV → CN-VIC @ 33 km
- Kentbruck Green Power Hub: GIP → SW-VIC @ 37 km; Cooba SF: WV → CN-VIC @ 22 km
- Ferguson WF: WV → SW-VIC @ 32 km; Starfish Hill: SE-SA → MN @ 60 km (review)
- Deargee Solar: CWO → NEW @ 22 km
These need a one-line eyeball each (M2 is plausible but the distance weakens it).

## M1 review (18) — accept Method 2
These are the weak-keyword cases — and they are exactly the projects already
adjudicated M2-correct in earlier waves / the SLD work:
- Bayswater (NEW→**HCC** 0.6 km) — SLD-confirmed HCC-native.
- Bowmans Creek (NEW→**HCC** 12 km), Glenbawn PHES (NEW→**HCC** 10 km),
  Goulburn River BESS/SF (CWO→**HCC** 7 km), Maxwell/Maxwell Downs ×3
  (CWO→**HCC** 9 km) — Upper Hunter cluster, M2 right.
- Cathedral Rocks (MN→**EYR** 27 km), Emeroo BESS (MN→**EYR** 8 km),
  Port Augusta SF (MN→**EYR** 0 km) — Eyre Peninsula, M2 right.
- Koorangie ×2 (CN-VIC→**MR** 9 km), LYA BESS (CN-VIC→**GIP** 1.6 km),
  Salt Creek WF (WV→**SW-VIC** 1.7 km) — all M2 right (matches Phase-1 spike).
- Hanworth BESS/Battery (CWO→**NEW** 30 km) — medium distance; M2 NEW
  (Liverpool Plains) is the better read but flag.
- Yarrabee Solar (CWO→**SW-NSW** 32 km) — already user-adjudicated SW-NSW.

## Refined boundary_swap merge rule
Replace the blanket "boundary_swap → Method 2" with:

1. **M1 high → keep Method 1** (1 case: Riverland Solar Storage). A confident
   keyword anchored to a specific REZ beats a distant spatial match.
2. **M1 medium + M2 high-confidence → Method 2** (21 cases). Topology
   wins when the coord is substation-close.
3. **M1 medium + M2 medium/far → flag for one-line review** (16 cases).
   Default to Method 2 but mark uncertain.
4. **M1 review → Method 2** (18 cases). Weak keyword; spatial corrects it.
   (All consistent with prior wave/SLD adjudications.)

Net: of 56 boundary swaps, **1 stays Method 1**, ~39 go to Method 2 cleanly,
~16 go to Method 2 with a review flag. No interconnector-anchored cases appeared
(the exclusion already handled those).
