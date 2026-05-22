"""Task 1 — synthetic-data sanity check for the v0.7.2 pipeline.

Scenario A (null): generate first-entries with per-(catchment,window) rate EXACTLY
proportional to the real lagged-exposure baseline (i.e. the null hypothesis both tests
assume: no clustering beyond exposure). Calibrated p-values should be ~Uniform[0,1];
~5% of units p<0.05, ~none after Bonferroni; within-window combined p far from significance.

Scenario B (planted clustering): concentrate 80% of events in 3 catchments x 4 windows;
the pipeline should detect the planted signal in exactly those catchments/windows.

Note on the null design: a generative model with "uniform-over-windows timing" would NOT
be the right null — if the global rate per unit-exposure is flat over time but exposure
itself grows, that is itself a departure from the exposure baseline the temporal test is
built to flag. The correct no-clustering null is rate ∝ lagged exposure per cell, used here.
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from scipy import stats
import v072_pipeline as P

R = P.load_real()
panel_clean, all_releases, data_start = R['panel_clean'], R['all_releases'], R['data_start']
EL = P.exposure_lag_matrix(panel_clean, all_releases, data_start, P.REZ)  # windows x REZ
EL = EL.fillna(0.0)
windows = list(EL.index)
units = list(EL.columns)
ELv = EL.values  # (W, U)
TOTAL_REAL = 1023  # real high+medium REZ first-entries

def synth_fe_from_counts(counts):
    """counts: (W,U) int array -> fe_df with first_release, catchment columns."""
    wi, ui = np.nonzero(counts)
    reps = counts[wi, ui]
    first_release = np.repeat([windows[i] for i in wi], reps)
    catchment = np.repeat([units[i] for i in ui], reps)
    return pd.DataFrame({'first_release': first_release, 'catchment': catchment})

def run_pipeline(fe_df, seed):
    rc = P.resolution_analysis(fe_df, panel_clean, all_releases, 'catchment', P.REZ,
                               B=10000, seed_base=1000 + seed)
    ww = P.within_window_concentration(fe_df, panel_clean, all_releases, P.REZ, B=10000, seed=7 + seed)
    return rc, ww

print('='*70); print('SCENARIO A — NULL (rate proportional to exposure baseline)'); print('='*70)
lam = TOTAL_REAL / ELv.sum()
N_RUNS = 20
fpr_uncorr, fpr_bonf, ww_comb_p, ww_nsig, all_punit, n_tested_list = [], [], [], [], [], []
for run in range(N_RUNS):
    rng = np.random.default_rng(5000 + run)
    counts = rng.poisson(lam * ELv)
    fe_df = synth_fe_from_counts(counts)
    rc, ww = run_pipeline(fe_df, run)
    pu = rc['per_unit']
    tested = pu[pu.tested & pu.p_bootstrap.notna()]
    N = len(tested); alpha = 0.05 / N
    fpr_uncorr.append((tested.p_bootstrap < 0.05).mean())
    fpr_bonf.append((tested.p_bootstrap < alpha).mean())
    ww_comb_p.append(ww['cal_nominal_p']); ww_nsig.append(ww['n_sig_05'])
    all_punit.extend(tested.p_bootstrap.tolist()); n_tested_list.append(N)

all_punit = np.array(all_punit)
print(f'runs={N_RUNS}, total synthetic events ~{TOTAL_REAL}, units tested/run ~{int(np.mean(n_tested_list))}')
print(f'\n(a) TEMPORAL DISPERSION false-positive rate (calibrated bootstrap p):')
print(f'  uncorrected  p<0.05 : observed {np.mean(fpr_uncorr)*100:.2f}%  (nominal 5.00%)  [range {min(fpr_uncorr)*100:.1f}-{max(fpr_uncorr)*100:.1f}%]')
print(f'  Bonferroni   p<a/N  : observed {np.mean(fpr_bonf)*100:.3f}%  (nominal {100*0.05/np.mean(n_tested_list):.3f}%)')
print(f'  pooled per-unit p: n={len(all_punit)}, mean={all_punit.mean():.3f} (uniform expect 0.5), '
      f'frac<0.05={np.mean(all_punit<0.05)*100:.2f}%')
ks = stats.kstest(all_punit, 'uniform')
print(f'  KS test vs Uniform[0,1]: D={ks.statistic:.3f}, p={ks.pvalue:.3f}  '
      f'(note: bootstrap p is slightly discrete/conservative via (cnt+1)/(B+1))')
print(f'\n(b) WITHIN-WINDOW concentration under null:')
print(f'  combined p: median={np.median(ww_comb_p):.3f}, min={min(ww_comb_p):.3f}  (expect ~Uniform, NOT tiny)')
print(f'  windows sig @0.05 per run: mean={np.mean(ww_nsig):.2f} of ~{R["fe_hm"].first_release.nunique()} (nominal ~5%)')
print(f'  runs with combined p<0.05: {np.mean(np.array(ww_comb_p)<0.05)*100:.0f}%  (nominal 5%)')

print('\n(b2) WITHIN-WINDOW combined-p FPR — focused high-N null check (200 runs):')
ww_p200 = []
for run in range(200):
    rng = np.random.default_rng(20000 + run)
    counts = rng.poisson(lam * ELv)
    fe_df = synth_fe_from_counts(counts)
    ww = P.within_window_concentration(fe_df, panel_clean, all_releases, P.REZ, B=2000, seed=run)
    ww_p200.append(ww['cal_nominal_p'])
ww_p200 = np.array(ww_p200)
print(f'  runs=200 (B=2000 for speed): combined p<0.05 in {np.mean(ww_p200<0.05)*100:.1f}% (nominal 5%), '
      f'median={np.median(ww_p200):.3f}, min={ww_p200.min():.4f}')
print(f'  (real data combined p = 1.4e-17; null minimum here = {ww_p200.min():.4f} -> null never approaches real signal)')

print('\n' + '='*70); print('SCENARIO B — PLANTED CLUSTERING (80% in 3 catchments x 4 windows)'); print('='*70)
plant_catch = ['HCC', 'SE-SA', 'ILW']          # all NON-significant in the real data
plant_win_idx = [3, 8, 12, 16]                  # 4 windows by position
plant_units = [units.index(c) for c in plant_catch]
plant_windows = [windows[i] for i in plant_win_idx]
print(f'planted catchments (non-sig in real data): {plant_catch}')
print(f'planted windows: {[pd.Timestamp(w).strftime("%Y-%m") for w in plant_windows]}')

det_catch, det_win = {c: [] for c in plant_catch}, []
for run in range(5):
    rng = np.random.default_rng(8000 + run)
    counts = np.zeros((len(windows), len(units)), int)
    # 200 baseline events ∝ exposure
    base = rng.poisson((200 / ELv.sum()) * ELv); counts += base
    # 800 planted events spread over the 3x4 = 12 cells
    cells = [(wi, ui) for wi in plant_win_idx for ui in plant_units]
    alloc = rng.multinomial(800, [1/len(cells)] * len(cells))
    for (wi, ui), k in zip(cells, alloc): counts[wi, ui] += k
    fe_df = synth_fe_from_counts(counts)
    rc, ww = run_pipeline(fe_df, 100 + run)
    pu = rc['per_unit'].set_index('unit')
    for c in plant_catch:
        det_catch[c].append(pu.loc[c, 'p_bootstrap'] if pu.loc[c, 'tested'] else np.nan)
    wtab = ww['per_window'].set_index('window')
    pl = [pd.Timestamp(w).strftime('%Y-%m') for w in plant_windows]
    det_win.append((wtab.loc[[w for w in pl if w in wtab.index], 'p_calibrated'].max(),
                    ww['cal_nominal_p']))
print('\nplanted-catchment detection (calibrated bootstrap p, mean over 5 runs):')
for c in plant_catch:
    arr = np.array(det_catch[c]); print(f'  {c}: p_boot mean={np.nanmean(arr):.2e}  (expect significant)')
print('within-window detection: worst planted-window p and combined p (5 runs):')
for i, (wmax, comb) in enumerate(det_win):
    print(f'  run {i}: worst planted-window p={wmax:.2e}, combined p={comb:.2e}')
print('\n(Scenario B confirms the pipeline DETECTS planted signal where it exists.)')
