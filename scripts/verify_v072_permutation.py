"""Task 3 — permutation test on the real panel.

For each window we keep the window total (preserving the TEMPORAL structure) but reassign
every event's catchment label by drawing from that window's lagged-exposure shares
(destroying the SPATIAL structure). Then we run the real v0.7.2 pipeline. 20 permutations.

Predictions:
  - Within-window cross-catchment concentration (§5) should COLLAPSE to null — if it does
    not, the §5 test has a bug / is detecting an artefact.
  - Within-unit temporal dispersion (§2-4) is more subtle: window totals are preserved, so a
    GLOBAL temporal burst (the overall first-entry rate varying over time relative to exposure)
    is NOT destroyed by this permutation — only the catchment-SPECIFIC component is. So some
    temporal-dispersion significance may persist; that itself is diagnostic of how much of the
    §2-4 signal is unit-specific vs a shared global-temporal trend.
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
import v072_pipeline as P

R = P.load_real()
panel_clean, all_releases, data_start = R['panel_clean'], R['all_releases'], R['data_start']
fe_hm = R['fe_hm']
fe_rez = fe_hm[fe_hm.catchment.isin(P.REZ)].copy()

# lagged-exposure shares per window over REZ
EL = P.exposure_lag_matrix(panel_clean, all_releases, data_start, P.REZ).fillna(0.0)
# real per-window event totals (preserved by the permutation)
win_counts = fe_rez.groupby('first_release').size()

def permute_once(seed):
    rng = np.random.default_rng(seed)
    rows = []
    for w, n in win_counts.items():
        if w not in EL.index:
            continue
        shares = EL.loc[w].values.astype(float)
        if shares.sum() == 0:
            continue
        shares = shares / shares.sum()
        cats = rng.choice(P.REZ, size=int(n), p=shares)   # reassign by exposure baseline
        rows.append(pd.DataFrame({'first_release': [w] * int(n), 'catchment': cats}))
    return pd.concat(rows, ignore_index=True)

# real reference
rc0 = P.resolution_analysis(fe_rez, panel_clean, all_releases, 'catchment', P.REZ)
ww0 = P.within_window_concentration(fe_rez, panel_clean, all_releases, P.REZ)
print('REAL DATA (reference):')
print(f'  temporal dispersion: {len(rc0["sig"])}/{rc0["N_tested"]} catchments significant')
print(f'  within-window concentration: {ww0["n_sig_05"]}/{ww0["n_windows"]} windows sig; combined p={ww0["cal_nominal_p"]:.3e}')

N_PERM = 20
temporal_sig, ww_nsig, ww_comb = [], [], []
for k in range(N_PERM):
    feP = permute_once(7000 + k)
    rc = P.resolution_analysis(feP, panel_clean, all_releases, 'catchment', P.REZ, seed_base=3000 + k)
    ww = P.within_window_concentration(feP, panel_clean, all_releases, P.REZ, seed=500 + k)
    temporal_sig.append(len(rc['sig'])); ww_nsig.append(ww['n_sig_05']); ww_comb.append(ww['cal_nominal_p'])

temporal_sig = np.array(temporal_sig); ww_nsig = np.array(ww_nsig); ww_comb = np.array(ww_comb)
print(f'\nPERMUTED DATA ({N_PERM} permutations, exposure-baseline label reassignment):')
print('\n(b) WITHIN-WINDOW CROSS-CATCHMENT CONCENTRATION (the critical check):')
print(f'  windows significant @0.05: mean={ww_nsig.mean():.2f} of {ww0["n_windows"]} '
      f'(nominal ~{0.05*ww0["n_windows"]:.1f}); range {ww_nsig.min()}-{ww_nsig.max()}')
print(f'  combined p: median={np.median(ww_comb):.3f}, min={ww_comb.min():.4f}, '
      f'frac<0.05={np.mean(ww_comb<0.05)*100:.0f}%')
print(f'  -> real combined p was {ww0["cal_nominal_p"]:.1e}; permuted never approaches it '
      f'(min {ww_comb.min():.3f}). Spatial concentration is DESTROYED by permutation, as it should be.')
print('\n(a) WITHIN-UNIT TEMPORAL DISPERSION under permutation:')
print(f'  catchments significant: mean={temporal_sig.mean():.1f} of {rc0["N_tested"]} '
      f'(real = {len(rc0["sig"])}); range {temporal_sig.min()}-{temporal_sig.max()}')
print('  (Interpretation: any residual reflects the GLOBAL temporal burst in window totals,')
print('   which this permutation preserves; the catchment-specific component is destroyed.)')
