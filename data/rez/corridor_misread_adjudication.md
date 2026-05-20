# Corridor-misread adjudication (8 cases)

Each case: Method 1 keyword anchor vs Method 2 spatial finding, with a location
check and SLD-topology read. Call at the end of each.

## 1. Belhaven Renewable Project (NSW) — M1 NEW vs M2 SW-NSW
M1 keyword `Belhaven` → NEW (there is a Belhaven locality near Scone, Upper
Hunter). M2 coord (-35.200, 147.372) snaps to **Wagga @ 2.0 km, high**.
Verified: Vena Energy Belhaven BESS is **7 km south of Wagga Wagga**, Riverina,
connecting to the Transgrid 330 kV substation 1.4 km away. SLD places Wagga in
the SW-NSW/Riverina corridor. The keyword matched the wrong Belhaven.
**→ Method 2 correct (SW-NSW).**

## 2. Strontian Solar BESS (NSW) — M1 NEW vs M2 SW-NSW
M1 keyword `Strontian` → NEW (spurious). M2 coord (-34.921, 146.644) from the
AEMO KCI address (Sandigo, near Narrandera) snaps to **Lockhart @ 13.9 km,
high**. Sandigo/Narrandera is firmly Riverina. SLD: Riverina = SW-NSW.
**→ Method 2 correct (SW-NSW).**

## 3. Jeremiah WF (NSW) — M1 NEW vs M2 SW-NSW
M1 keyword `Jeremiah` → NEW (spurious). M2 coord (-35.068, 148.112), AEMO KCI
"Gundagai", snaps to **Blowering @ 38.7 km, medium**. Gundagai is in the
Tumut/SW-NSW corridor (near Snowy/Blowering). The 38.7 km distance reflects
sparse substation coverage there, not a wrong call. SLD: Tumut/Gundagai feeds
the SW-NSW/Snowy corridor. **→ Method 2 correct (SW-NSW)**, low spatial
precision noted.

## 4. Kingswood BESS (NSW) — M1 SW-NSW vs M2 NEW
M1 keyword `Kingswood` → SW-NSW (there is a Kingswood near Penrith/elsewhere).
M2 coord (-31.141, 150.901), AEMO KCI "744 Burgmanns Lane, Kingswood (Tamworth)
NSW 2340", snaps to **Tamworth @ 4.9 km, high**. The project is the
Tamworth-area Kingswood, squarely NEW. SLD: Tamworth = NEW (New England).
**→ Method 2 correct (NEW).**

## 5-6. Wattle Creek Energy Hub — Battery + Solar/BESS (NSW) — M1 CWO vs M2 ILW
M1 keyword `Wattle Creek` → CWO (spurious). M2 coords (-34.60, 150.06 /
-34.65, 149.97) snap to **Marulan @ 1.5 km / 8.8 km, high**. The project is at
Arthursleigh, ~15 km NW of Marulan (Southern Tablelands). CWO is clearly wrong.
The Marulan/Bannaby area feeds the ILW corridor via the Bannaby gateway (per the
SLD topology adjudication — Bannaby is the southern collector). **→ Method 2
correct that it is NOT CWO**; ILW is defensible via the Bannaby corridor, though
Marulan itself sits on the ILW/SW-NSW boundary — flag both Wattle Creek rows for
a one-line ILW-vs-SW-NSW eyeball.

## 7. Malunga Nine Mile BESS - KCI (VIC) — M1 MR vs M2 SW-VIC
M1 keyword `Malunga Nine Mile` → MR (the "Mallee/Murray" association is
spurious). M2 coord (-38.030, 143.634), proponent (Pacific Green Nine Mile
Energy Park, Cressy), snaps to **Berrybank @ 22.6 km, medium**. Cressy is in the
SW Victoria corridor (Cressy/Berrybank terminal stations). SLD: Cressy/Berrybank
= SW-VIC. **→ Method 2 correct (SW-VIC).**

## 8. Quandong Solar Farm (VIC) — M1 MR vs M2 SW-VIC — AMBIGUOUS
M1 keyword `Quandong` → MR (there is a Quandong locality in the Murray/Sunraysia
region). M2 used a **locality_proxy (low)** to "Quandong VIC 3030" in
Wyndham/Werribee (-37.836, 144.508) → Yaloak South @ 26.4 km, medium. A 350 MW
solar farm in peri-urban Werribee is implausible, and no proponent/planning
source confirms either location. Both anchors are weak: M1's keyword and M2's
locality proxy could each be the wrong Quandong. **→ ambiguous — coord
uncertainty.** Recommend treating as unresolved (drop the locality_proxy coord)
pending a proponent/planning-portal location, rather than trusting either.

## Outcome
- **Method 2 correct: 7 of 8** (Belhaven, Strontian, Jeremiah, Kingswood,
  Wattle Creek ×2, Malunga). All were Method 1 keyword misreads.
- **Ambiguous: 1** (Quandong) — neither method reliable; hold as unresolved.
- **Method 1 correct: 0.**

## Merge-rule impact
`corridor_misread → Method 2` **holds**, with one refinement:
- Where Method 2's coord is a low-confidence locality_proxy AND no proponent
  source confirms it (Quandong), do NOT auto-adopt Method 2 — mark unresolved.
- Flag the two Wattle Creek rows for an ILW-vs-SW-NSW eyeball (boundary, not
  CWO).
