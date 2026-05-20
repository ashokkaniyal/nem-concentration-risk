# Cluster definitions — notebook 07 cluster resolution (APPROVED)

**Status: APPROVED 2026-05-20 with three revisions** (see "Approved revisions"
below). Final set: **5 multi-catchment clusters + 9 singletons.**

**Purpose.** Define a middle analytical resolution between the 23 individual REZ
catchments and the 4 states, derived **top-down from transmission topology** so
that the cluster boundaries are fixed *before* any test is run (guard against
post-hoc cluster engineering).

**Sources.** `sld_topology_adjudication.md` (2019 AEMO Main System Diagram,
connectivity-traced), `rez_substation_lookup_NEM.csv` (per-REZ backbone
substations + transmission lines), `sld_substations.csv`. **No analysis run yet.**

**Method.** Group catchments that (a) inject into a shared 330/500 kV backbone
node, (b) are geographically adjacent on that backbone, and (c) share
interconnector exposure. Catchments that don't share a backbone with a neighbour
are left as **singletons** (degenerate at the cluster resolution — their
cluster-level result equals their catchment-level result).

n estimates below are **first-entries under the high+medium confidence filter**
(post-censor, Proposed/Anticipated; the primary-analysis universe). Total 1,024.

---

## Approved clusters (5)

### 1. Central-Northern NSW — `{CWO, HCC, NEW}`  ·  n ≈ 238
**Topology:** all three inject into **Bayswater** (the 500/330 kV Hunter→Sydney
Ring gateway / Hunter Valley 330 kV ring chokepoint). HCC is Bayswater-native
(Bayswater PS switchyard, Liddell, the Hunter Valley 330 kV ring); the **NE REZ
Transmission Link terminates *into* Bayswater** (Central Hub 5 → Bayswater 500 kV)
so NEW exports through it; CWO feeds east via the **Wollar–Bayswater 330 kV line**
and into the Sydney Ring at Barigan Creek 500 kV. One convergence node, three
corridors.

### 2. Southern QLD — `{WD, SD, DD, TG, WG}`  ·  n ≈ 108
**Topology:** the **Southern QLD 275/330 kV corridor** — Western Downs SS /
Kogan / Chinchilla (WD), Bell (DD), Tarong (TG), Woolooga/Borumba (WG), and
**Bulli Creek/Karara/Warwick (SD), with Bulli Creek doubling as the QNI southern
node**. This is the **notebook-06 baseline cluster** (the validated QLD herding
signal), restated here so the NSW/VIC/SA clusters are tested against it.
*(QLD topology is lower-resolution — see Notes #4.)*

### 3. Eastern SA — `{MN, RIV}`  ·  n ≈ 85
**Topology:** the Adelaide 275 kV core + the **PEC eastern terminus at
Robertstown**. **MN** holds Robertstown/Bundey (the PEC gateway); **RIV** connects
via **Monash/Murraylink** and the Buronga–Red Cliffs PEC leg. **PEC is the
unifying mechanism** for these two. *(SE-SA removed — see Approved revisions.)*

### 4. Western Victoria — `{WV, SW-VIC}`  ·  n ≈ 99
**Topology:** the **Western Renewables Link + SW-VIC 500 kV** (Bulgana, Ararat,
Stockyard Hill → Moorabool/Mortlake/Sydenham). **Bulgana is the WV/SW-VIC
boundary node**; WRL stitches the two into one western-VIC export corridor toward
Melbourne and Heywood.

### 5. Northern Victoria — `{CN-VIC, MR}`  ·  n ≈ 88
**Topology:** the northern VIC **220 kV Murray network** (Bendigo, Shepparton,
Echuca, Kerang) with shared boundary nodes (Boort, Mologa, Yarrawonga). **VNI
West originates at Kerang (MR)** and runs to Dinawan; CN-VIC and MR sit on the
same northern 220 kV system feeding it.

---

## Singletons (9) — tested at catchment level only

Each shares no defining REZ backbone with a neighbour, so it has no cluster.
Degenerate at the cluster resolution (reported as "n/a — singleton" in the §3
cluster table, **not** as a duplicate of the catchment-level result).

| Catchment | n (h+m) | Why it doesn't cluster |
|---|---:|---|
| **SW-NSW** | 116 | Tumut–Wagga 500 kV spine / HumeLink. Bannaby is a connection node, not a defining shared corridor; very different generation/developer/policy profile from ILW. Tested independently *(revised — see below).* |
| **CQ** | 98 | Central QLD (Stanwell/Gladstone/Rockhampton 275 kV); separate from Southern QLD and from FNQ except via a long coastal radial. |
| **GIP** | 48 | Latrobe Valley 500 kV island (Loy Yang/Hazelwood) + Basslink; no shared REZ backbone with WV/SW-VIC or CN-VIC. |
| **TAS-NW** | 43 | Single TAS catchment; Basslink/Marinus island. Reported descriptively in §5; excluded from formal testing. |
| **FNQ** | 28 | Far North radial (Townsville/Cairns 275 kV single-circuit). |
| **ILW** | 22 | Illawarra (offshore + onshore). Bannaby is a connection node, not a defining corridor; profile diverges sharply from SW-NSW. Tested independently *(revised — see below).* |
| **SEQ** | 20 | SE QLD load centre (Brisbane/Ipswich); a sink, not a generation corridor. |
| **SE-SA** | 17 | South-East SA — Heywood-corridor-leaning (Tailem Bend/Tungkillo), **not on PEC**. A cross-border {SE-SA, SW-VIC} cluster would mix SA/VIC policy regimes. Cleaner as singleton *(revised — see below).* |
| **EYR** | 13 | Eyre Peninsula — **electrically separate** via Cultana/Davenport (the reason it was split from MN in Phase 2). |

All nine singletons clear n ≥ 10 individually except none below threshold — though
TAS-NW is excluded from formal testing on the single-catchment limitation.

---

## Approved revisions (from the Phase 1 proposal)

Three changes were made to the Phase 1 proposal before approval. The reasoning:

> **SE-SA → singleton; Eastern SA shrinks to {MN, RIV}.** SE-SA is not on PEC —
> it is Heywood-corridor-leaning (Tailem Bend/Tungkillo into the Adelaide ring and
> the SA–VIC interconnector). PEC (Robertstown terminus) is the *unifying
> mechanism* for MN and RIV specifically; SE-SA does not sit on it. A cross-border
> {SE-SA, SW-VIC} alternative would mix SA and VIC policy regimes and be harder to
> interpret. Cleaner to test SE-SA independently.
>
> **ILW → singleton; the {SW-NSW, ILW} "Southern NSW" cluster is dropped.**
> Bannaby is a connection node, not a defining corridor. ILW and SW-NSW have very
> different generation profiles, developer pools, and policy exposure (Illawarra
> offshore vs Riverina/Snowy inland), so they are better tested independently.
> Both stand as singletons.

Net effect: Phase 1's 6 clusters + 6 singletons → **5 clusters + 9 singletons**.
The CWO-into-Central-Northern-NSW call (Phase 1's biggest judgement call) was
accepted as-is.

---

## Coverage check

5 clusters span 14 catchments; 9 singletons span the remaining 9 → **all 23
catchments covered**, no overlaps. Two sub-threshold catchments (RIV n=7, TG n=5)
are **rescued by pooling** into Eastern SA and Southern QLD respectively, so they
contribute at the cluster resolution even though they're descriptive-only at the
catchment resolution.

| Cluster | Members | n (h+m) | ≥10? |
|---|---|---:|---|
| Central-Northern NSW | CWO, HCC, NEW | 238 | ✓ |
| Southern QLD | WD, SD, DD, TG, WG | 108 | ✓ |
| Western Victoria | WV, SW-VIC | 99 | ✓ |
| Northern Victoria | CN-VIC, MR | 88 | ✓ |
| Eastern SA | MN, RIV | 85 | ✓ |
| *singletons (9)* | SW-NSW, CQ, GIP, TAS-NW, FNQ, ILW, SEQ, SE-SA, EYR | — | tested at catchment level only |

**§6 multi-resolution comparison rests on:** 23 catchments (one per REZ) · 5
multi-catchment clusters · 4 states (NSW, VIC, SA, QLD; TAS descriptive). The
cluster-level Fisher's combined includes **only the 5 multi-catchment clusters**.

---

## Notes

1. **CWO placement (accepted).** CWO–Wollar–Bayswater 330 kV ties it to the
   Bayswater node, so it sits in Central-Northern NSW. CWO is a large, distinct
   Central-West corridor (Mudgee/Dubbo/Orange) that also feeds the Sydney Ring at
   Barigan Creek, but the Bayswater convergence is genuine and folding avoids a
   degenerate big-n singleton.

2. **MR cross-border.** MR connects to SW-NSW via VNI West (Kerang–Dinawan) and
   PEC (Red Cliffs–Buronga) as much as to CN-VIC. Kept with CN-VIC (same-state
   220 kV) — a Murray/Sunraysia cross-border {MR, SW-NSW} grouping would mix
   states.

3. **QLD-Coastal not formed.** CQ, SEQ, FNQ remain singletons; the coastal 275 kV
   radial Brisbane→Gladstone→Townsville→Cairns is too long/loose to be a genuine
   shared-backbone cluster.

4. **QLD topology is lower-resolution.** The 2019 SLD QLD pages are graphical
   (connectivity not extractable from the text layer), so QLD clusters rest on
   the `rez_substation_lookup_NEM` substation groupings + the established
   notebook-06 framework, not fresh SLD tracing. Southern QLD is well-grounded
   (Bulli Creek/QNI, Western Downs SS); the CQ/FNQ/SEQ separation is geographic.
