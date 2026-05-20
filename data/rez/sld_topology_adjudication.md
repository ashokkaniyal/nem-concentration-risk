# SLD topology adjudication — boundary-case REZ assignment

**Source:** AEMO High Voltage Network Main System Diagram, **dated 04-04-2019**
(`data/rez/sources/aemo_sld_2022.pdf` — note the filename says 2022 but the
diagram content is dated April 2019; treat as 2019 network topology).

**Method:** pages rendered to PNG at 3× zoom via pymupdf
(`scripts/render_sld_pages.py` equivalent inline), read visually to trace
electrical connectivity (which lines/corridor a substation belongs to), not
geographic proximity.

**Caveat — 2019 vintage:** anything commissioned after April 2019 is absent
(MacIntyre WF, Karara, the CWO/NE REZ build substations, most recent BESS).
This is why the `proposed_not_yet_built` category exists in the lookup.

**Status:** findings only. Per instruction, no REZ reassignments applied to
`rez_substation_lookup_NEM.csv` — these feed the joint decision when Layer 2+
resumes and when the 5 user-prior adjudications are finalised.

---

## 1. Bayswater (NSW-j) — currently assigned NEW

**SLD finding:** Bayswater appears on **NSW-j** (the Sydney/Central page), drawn
as the 500/330 kV gateway from the Hunter generation cluster into the Sydney
ring. It is **not** drawn on NSW-b, where the Hunter Valley 330 kV ring
(Liddell, Muswellbrook, Tomago, Singleton) lives — but Liddell sits immediately
adjacent to Bayswater geographically.

**Call:** Bayswater is **natively a Hunter Valley (HCC) 500/330 kV node** — it
is the Bayswater coal power station's switchyard and the Hunter→Sydney
injection point. The **NEW REZ Transmission Link terminates *into* Bayswater**
(per Transgrid TAPR 2024), i.e. NEW REZ generation is delivered *to* Bayswater,
but Bayswater itself is Hunter infrastructure.

**Implication for classification:**
- Projects *at* Bayswater (e.g. "Bayswater" 685 MW = the coal PS, "Bayswater BESS") → **HCC** (native).
- New generation connecting *via the NE REZ Link* → **NEW** (the corridor, not the node).
- This nuances the Phase 1 prior: the user's "NEW per Transgrid TAPR" is correct for *REZ-corridor* purposes, but the substation node is HCC-native. For Method 2 spatial join, anything snapping to Bayswater should be flagged `bayswater_dual_role_HCC_native_NEW_injection` for manual confirmation.

## 2. Wollar (NSW-h) — currently CWO ✓ CONFIRMED

**SLD finding:** Wollar is on **NSW-h**, clustered on the 330 kV network with
**Wellington, Beryl, Bodangora** — all CWO REZ substations — and feeds
eastward toward Bayswater via the Wollar–Bayswater 330 kV line.

**Call:** **CWO confirmed by topology.** Wollar belongs to the Central-West
Orana corridor (Wellington/Beryl/Bodangora cluster), not merely near a CWO
centroid. The Wollar–Bayswater line is the CWO export path. No change.

## 3. Bulli Creek (QLD-k) — currently SD

**SLD finding:** Bulli Creek (R3) is on **QLD-k**, a 330 kV node (orange, not
yet 500 kV in 2019) tied to Millmerran (R4/R5) and the Braemar / Darling Downs
cluster. MacIntyre WF and Karara are **absent** (post-2019). Bulli Creek is the
QNI (Queensland–NSW Interconnector) southern node.

**Call:** **SD reasonable.** Bulli Creek is the border/interconnection node that
MacIntyre WF (Southern Downs) and Karara connect into (built after 2019). It
doubles as the QNI interconnection point — flag `bulli_creek_also_QNI_node`.
For SD-generation classification it is the correct anchor.

## 4. Mortlake / MOPS (VIC-a) — currently SW-VIC ✓ CONFIRMED

**SLD finding:** Mortlake (MOPS) is on **VIC-a**, in the South-West Victoria
coastal cluster with Portland (PTWF) and Alcoa Portland (APD), connected via the
500 kV network toward Heywood/Moorabool.

**Call:** **SW-VIC confirmed.** No change.

## 5. Robertstown (SA-d) — currently MN ✓ CONFIRMED

**SLD finding:** Robertstown is on **SA-d**, the 275 kV PEC (Project
EnergyConnect) eastern terminus, clustered with Hallett, North Brown Hill,
Hornsdale, Mokota, Belalie — the SA Mid-North wind/solar hubs.

**Call:** **MN confirmed.** Robertstown is the Mid-North 275 kV node and PEC
gateway. No change. (Bonus: MOR PUMP and MORGAN-WHYALLA PUMP 4 appear on the
same page as real load nodes — validates the exclusion filter treating the
pipeline pumping stations as non-generation.)

## 6. Heywood / HYTS (VIC-a) — flag as interconnector_terminal

**SLD finding:** Heywood (HYTS) is on **VIC-a** as the SA–VIC 500 kV
interconnector terminal (the magenta 500 kV line running off-page west to South
Australia).

**Call:** **`interconnector_terminal` — NOT a REZ node.** Heywood should not
carry a REZ assignment. Projects near Heywood belong to SW-VIC (VIC side) or
SE-SA (SA side) by their own location, not by snapping to the interconnector
terminal. Recommend tagging the Heywood lookup row `interconnector_terminal`
and excluding it as a spatial-join anchor.

## 7. Glenbawn (NSW-h area) — no substation in SLD

**SLD finding:** **There is no Glenbawn substation in the 2019 SLD.** Glenbawn
is the dam/lake; the Glenbawn Pumped Hydro project (proposed, post-2019) would
tie into the Upper Hunter network near Bayswater/Liddell.

**Call:** "Glenbawn" in our lookup is a **locality_keyword**, not a real
substation. The Glenbawn PHES project connects to the Hunter (HCC) network →
**HCC**, confidence high. Consistent with the Phase 1 adjudication
(Glenbawn PHES → HCC high).

## 8. Pottinger Energy Park (NSW) — project, not in SLD

**SLD finding:** Not in the 2019 SLD (post-2019 project). Per Transgrid TAPR
2024 and the NSW Electricity Infrastructure Roadmap, Pottinger Energy Park
connects via the **NE REZ Transmission Link** in the Liverpool Plains.

**Call:** **NEW**, confidence medium. Consistent with the Phase 1 adjudication
(Pottinger → NEW, overriding the SW-NSW prior slip). It is a project that should
live in `project_coordinates.csv`, not as a substation in the lookup.

## 9. Loy Yang / LYPS (VIC-f) — GIP ✓ CONFIRMED

**SLD finding:** Loy Yang (LYPS, Loy Yang Sub) is on **VIC-f**, the Latrobe
Valley 500 kV generation cluster with Hazelwood (HWTS/HAPS), Yallourn (YPS),
Jeeralang (JLTS), Morwell (MWTS).

**Call:** **GIP confirmed.** LYA BESS (= Loy Yang A BESS) → GIP. Consistent with
the Phase 1 adjudication. No change.

## 10. Kerang / Koorangie area (VIC-b) — MR ✓ CONFIRMED

**SLD finding:** Kerang (KGTS) is on **VIC-b**, in the Murray cluster with Swan
Hill and Gannawarra Solar/ESS. The Koorangie ESS connects at/near Kerang.

**Call:** **MR confirmed.** Koorangie ESS + Koorangie BESS Stage 2 → MR.
Consistent with the Phase 1 adjudication. No change.

---

## Summary of adjudication outcomes

| Case | Prior | SLD-based call | Change? |
|---|---|---|---|
| Bayswater | NEW | HCC-native / NEW-injection (dual role) | **nuance** — flag dual role |
| Wollar | CWO | CWO | confirmed |
| Bulli Creek | SD | SD (+ QNI node) | confirmed |
| Mortlake | SW-VIC | SW-VIC | confirmed |
| Robertstown | MN | MN | confirmed |
| Heywood | (various) | interconnector_terminal | **flag** — not a REZ anchor |
| Glenbawn | HCC (adj.) | HCC (locality, no substation) | confirmed |
| Pottinger | NEW (adj.) | NEW | confirmed |
| Loy Yang | GIP | GIP | confirmed |
| Kerang/Koorangie | MR | MR | confirmed |

**Two action items for the joint decision:**
1. **Bayswater** — decide whether the lookup row stays NEW (corridor role) or
   splits into HCC-native + NEW-injection. Recommend HCC-native with a NEW flag.
2. **Heywood** — retag `interconnector_terminal` and drop as a spatial-join
   anchor so SA/VIC border projects classify by their own location.

All other boundary cases are **confirmed** by SLD topology — strengthening the
Phase 1 spatial-join results with a connectivity-based (not proximity-based)
second line of evidence.
