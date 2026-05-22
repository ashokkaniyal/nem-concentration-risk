"""Faithful, parameterised copy of notebook 07 v0.7.2's statistical pipeline.

These are byte-for-byte the same statistical functions as
notebooks/07_nem_first_entry_tests.ipynb, with the notebook's module-level globals
(panel_clean, all_releases, B, FLOOR) lifted to explicit arguments so the SAME code
can be run on real, synthetic, or permuted first-entry panels.

`self_check()` proves this module reproduces the committed real numbers exactly before
it is trusted for the synthetic / permutation verification (tasks 1 & 3).
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, 'src')
from nem_herding.projects import load_all_releases, join_catchment

REZ = ['CWO','HCC','NEW','SW-NSW','ILW','CN-VIC','MR','WV','GIP','SW-VIC','MN','SE-SA','RIV','EYR','TAS-NW',
       'WD','SD','DD','TG','WG','FNQ','CQ','SEQ']
STATE = {**{c:'NSW' for c in ['CWO','HCC','NEW','SW-NSW','ILW']},
         **{c:'VIC' for c in ['CN-VIC','MR','WV','GIP','SW-VIC']},
         **{c:'SA'  for c in ['MN','SE-SA','RIV','EYR']}, 'TAS-NW':'TAS',
         **{c:'QLD' for c in ['WD','SD','DD','TG','WG','FNQ','CQ','SEQ']}}
CLUSTER = {**{c:'Central-Northern NSW' for c in ['CWO','HCC','NEW']},
           **{c:'Southern QLD' for c in ['WD','SD','DD','TG','WG']},
           **{c:'Eastern SA' for c in ['MN','RIV']},
           **{c:'Western Victoria' for c in ['WV','SW-VIC']},
           **{c:'Northern Victoria' for c in ['CN-VIC','MR']}}
CLUSTER_ORDER = ['Central-Northern NSW','Southern QLD','Western Victoria','Northern Victoria','Eastern SA']


def floor_of(B):
    return 1.0 / (B + 1)


# ---------- statistics (identical to notebook 07) ----------
def fano_with_ci(counts, n_boot=2000, seed=0):
    counts = np.asarray(counts, float)
    if counts.mean() == 0 or len(counts) < 3:
        return np.nan, (np.nan, np.nan)
    point = counts.var(ddof=1) / counts.mean()
    rng = np.random.default_rng(seed); boots = []
    for _ in range(n_boot):
        s = rng.choice(counts, size=len(counts), replace=True)
        if s.mean() > 0: boots.append(s.var(ddof=1) / s.mean())
    return point, (np.percentile(boots, 2.5), np.percentile(boots, 97.5)) if boots else (np.nan, np.nan)


def fishers_index(pvals, floor):
    p = np.maximum(np.asarray([x for x in pvals if not np.isnan(x)], float), floor)
    if len(p) == 0: return np.nan, 0
    return float(-2 * np.sum(np.log(p))), len(p)


def fishers_p(pvals):
    p = np.maximum(np.asarray([x for x in pvals if not np.isnan(x)], float), 1e-12)
    if len(p) == 0: return np.nan, 0, np.nan
    cs = -2 * np.sum(np.log(p)); df = 2 * len(p)
    return float(cs), df, float(stats.chi2.sf(cs, df))


def bootstrap_p(o, e, lag, seed, B):
    stat = float(((o - e) ** 2 / np.maximum(e, 1e-9)).sum())
    rng = np.random.default_rng(seed)
    sims = rng.poisson(np.maximum(e, 0), size=(B, len(e)))
    mrs = (sims / lag).mean(axis=1)
    es = lag[None, :] * mrs[:, None]
    sim_stat = ((sims - es) ** 2 / np.maximum(es, 1e-9)).sum(axis=1)
    cnt = int((sim_stat >= stat).sum())
    return stat, (cnt + 1) / (B + 1), cnt == 0


def resolution_analysis(fe_df, panel_clean, all_releases, unit_col, units,
                        B=10000, min_n=10, do_bootstrap=True, seed_base=1000):
    FLOOR = floor_of(B)
    wc = (fe_df.groupby(['first_release', unit_col]).size().unstack(fill_value=0)
          .reindex(columns=units, fill_value=0))
    win = list(wc.index)
    expo = (panel_clean.groupby(['release_date', unit_col]).size().unstack(fill_value=0)
            .reindex(columns=units, fill_value=0).reindex(index=all_releases, fill_value=0))
    expo_lag = expo.shift(1).reindex(win)
    rate = (wc / expo_lag).replace([np.inf, -np.inf], np.nan)
    expected = expo_lag * rate.mean(axis=0)

    rows = []
    for i, u in enumerate(units):
        o = wc[u].values.astype(float); e = expected[u].values.astype(float); el = expo_lag[u].values.astype(float)
        valid = (~np.isnan(e)) & (el > 0)
        n_tot = int(o.sum())
        if valid.sum() >= 2 and np.nansum(e[valid]) > 0:
            ov, ev, lv = o[valid], e[valid], el[valid]
            stat = float(((ov - ev) ** 2 / np.maximum(ev, 1e-9)).sum())
            df = int(valid.sum() - 1); p_asym = float(stats.chi2.sf(stat, df))
            if do_bootstrap and n_tot >= min_n:
                _, p_boot, at_floor = bootstrap_p(ov, ev, lv, seed_base + i, B)
            else:
                p_boot, at_floor = (np.nan, False)
        else:
            stat = p_asym = np.nan; p_boot, at_floor = (np.nan, False)
        rows.append({'unit': u, 'n': n_tot, 'chi2_stat': stat,
                     'p_asymptotic': p_asym, 'p_bootstrap': p_boot, 'at_floor': at_floor,
                     'tested': n_tot >= min_n})
    per_unit = pd.DataFrame(rows)
    pcol = 'p_bootstrap' if do_bootstrap else 'p_asymptotic'
    tested = per_unit[per_unit.tested & per_unit[pcol].notna()]
    N = len(tested); alpha = 0.05 / N if N else np.nan
    sig = tested[tested[pcol] < alpha]['unit'].tolist() if N else []
    ev_idx, _ = fishers_index(tested[pcol].values, FLOOR) if N else (np.nan, 0)
    best = min(float(tested[pcol].min()) * N, 1.0) if N else np.nan
    return {'per_unit': per_unit, 'N_tested': N, 'alpha': alpha, 'sig': sig,
            'best_p_corrected': best, 'evidence_index': ev_idx,
            'n_at_floor': int(tested['at_floor'].sum()) if N else 0}


def conditioned_temporal(fe_df, panel_clean, all_releases, unit_col, units,
                         B=100000, min_n=10, seed=11):
    """v0.7.3 window-total-CONDITIONED temporal test.

    Expected[X, W] = n_W * share_W[X], where n_W is the window's total over the unit
    universe and share_W[X] = exposure_lag[X,W] / sum_units exposure_lag. By scaling the
    expected by the window total, a unit that merely rides a national surge contributes ~0;
    only units that capture MORE than their exposure share of the window's activity are
    flagged. Null = per-window Multinomial(n_W, share_W); a single set of B panel draws
    yields every unit's null distribution (units are coupled within a window, independent
    across windows). This replaces v0.7.2's constant-mean-rate test, which conflated a
    national temporal trend with unit-specific concentration (see verification report)."""
    wc = (fe_df.groupby(['first_release', unit_col]).size().unstack(fill_value=0)
          .reindex(columns=units, fill_value=0))
    win = list(wc.index)
    expo = (panel_clean.groupby(['release_date', unit_col]).size().unstack(fill_value=0)
            .reindex(columns=units, fill_value=0).reindex(index=all_releases, fill_value=0))
    el = expo.shift(1).reindex(win).fillna(0.0)
    o = wc.values.astype(float); U = len(units)
    rng = np.random.default_rng(seed)
    T_obs = np.zeros(U); acc = np.zeros((B, U))
    for wi in range(len(win)):
        ex = el.iloc[wi].values.astype(float); m = ex > 0
        n = int(o[wi, m].sum())
        if n < 1 or ex[m].sum() == 0: continue
        p = ex[m] / ex[m].sum(); expv = n * p; idx = np.where(m)[0]
        T_obs[idx] += (o[wi, m] - expv) ** 2 / expv
        sims = rng.multinomial(n, p, size=B).astype(float)
        acc[:, idx] += (sims - expv[None, :]) ** 2 / expv[None, :]
    n_tot = o.sum(axis=0); rows = []
    for j, X in enumerate(units):
        tested = n_tot[j] >= min_n
        cnt = int((acc[:, j] >= T_obs[j]).sum()) if tested else None
        rows.append({'unit': X, 'n': int(n_tot[j]), 'T_conditioned': round(float(T_obs[j]), 2),
                     'p_conditioned': (cnt + 1) / (B + 1) if tested else np.nan,
                     'tested': bool(tested), 'at_floor': bool(tested and cnt == 0)})
    per_unit = pd.DataFrame(rows)
    tt = per_unit[per_unit.tested]
    N = len(tt); alpha = 0.05 / N if N else np.nan
    sig = tt[tt.p_conditioned < alpha]['unit'].tolist() if N else []
    best = min(float(tt['p_conditioned'].min()) * N, 1.0) if N else np.nan
    return {'per_unit': per_unit, 'N_tested': N, 'alpha': alpha, 'sig': sig,
            'best_p_corrected': best, 'n_at_floor': int(tt['at_floor'].sum()) if N else 0}


def within_window_concentration(fe_df, panel_clean, all_releases, units,
                                B=10000, min_n_window=3, seed=7):
    FLOOR = floor_of(B)
    wc = (fe_df[fe_df['catchment'].isin(units)].groupby(['first_release', 'catchment']).size()
          .unstack(fill_value=0).reindex(columns=units, fill_value=0))
    win = list(wc.index)
    expo = (panel_clean.groupby(['release_date', 'catchment']).size().unstack(fill_value=0)
            .reindex(columns=units, fill_value=0).reindex(index=all_releases, fill_value=0))
    expo_lag = expo.shift(1).reindex(win)
    rng = np.random.default_rng(seed); rows = []
    for w in win:
        obs = wc.loc[w].values.astype(float); ex = expo_lag.loc[w].values.astype(float)
        ex = np.where(np.isnan(ex), 0, ex); m = ex > 0
        n = int(obs[m].sum())
        if n < min_n_window or ex[m].sum() == 0: continue
        p = ex[m] / ex[m].sum(); o = obs[m]; expv = n * p
        stat = float(((o - expv) ** 2 / expv).sum()); df = int(m.sum() - 1)
        p_asym = float(stats.chi2.sf(stat, df))
        sims = rng.multinomial(n, p, size=B).astype(float)
        sim_stat = ((sims - expv[None, :]) ** 2 / expv[None, :]).sum(axis=1)
        cnt = int((sim_stat >= stat).sum())
        rows.append({'window': pd.Timestamp(w).strftime('%Y-%m'), 'n': n,
                     'p_asymptotic': p_asym, 'p_calibrated': (cnt + 1) / (B + 1), 'at_floor': cnt == 0})
    t = pd.DataFrame(rows)
    asym = fishers_p(t['p_asymptotic'].values)
    cal_idx, k = fishers_index(t['p_calibrated'].values, FLOOR)
    cal_nom_p = float(stats.chi2.sf(cal_idx, 2 * k)) if k else np.nan
    return {'per_window': t, 'n_windows': len(t), 'n_sig_05': int((t['p_calibrated'] < 0.05).sum()),
            'n_at_floor': int(t['at_floor'].sum()), 'asym_combined_p': asym[2],
            'cal_evidence_index': cal_idx, 'cal_nominal_p': cal_nom_p}


# ---------- data loading ----------
def load_real(repo='.'):
    DATA = Path(repo) / 'data'
    panel = load_all_releases(DATA / 'projects' / 'aemo_geninfo')
    panel = join_catchment(panel, DATA / 'rez' / 'transmission_catchment_lookup.csv')
    lk = pd.read_csv(DATA / 'rez' / 'transmission_catchment_lookup.csv')
    panel = panel.merge(lk[['site_name', 'phantom_risk']], on='site_name', how='left', suffixes=('', '_lk'))
    panel['phantom_risk'] = pd.to_numeric(panel['phantom_risk'], errors='coerce').fillna(0).astype(int)
    panel_clean = panel[panel['phantom_risk'] < 2].copy()
    data_start = panel_clean['release_date'].min()
    all_releases = sorted(panel_clean['release_date'].unique())
    fe = (panel_clean.sort_values('release_date').groupby('site_name', as_index=False).first()
          [['site_name', 'release_date', 'status_bucket', 'catchment', 'catchment_confidence']]
          .rename(columns={'release_date': 'first_release', 'status_bucket': 'first_status'}))
    fe = fe[(fe.first_release > data_start) & (fe.first_status.isin(['Proposed', 'Anticipated']))].copy()
    for df in (panel_clean, fe):
        df['state'] = df['catchment'].map(STATE); df['cluster'] = df['catchment'].map(CLUSTER)
    fe_hm = fe[fe.catchment_confidence.isin(['high', 'medium'])].copy()
    return {'panel_clean': panel_clean, 'all_releases': all_releases, 'fe': fe, 'fe_hm': fe_hm,
            'data_start': data_start}


def exposure_lag_matrix(panel_clean, all_releases, data_start, units=REZ):
    """The lagged exposure matrix (windows x units) used as the generative baseline."""
    expo = (panel_clean.groupby(['release_date', 'catchment']).size().unstack(fill_value=0)
            .reindex(columns=units, fill_value=0).reindex(index=all_releases, fill_value=0))
    expo_lag = expo.shift(1)
    win = [w for w in all_releases if w > data_start]
    return expo_lag.reindex(win)  # rows=windows, cols=units


def self_check():
    R = load_real()
    rc = resolution_analysis(R['fe_hm'], R['panel_clean'], R['all_releases'], 'catchment', REZ)
    ww = within_window_concentration(R['fe_hm'], R['panel_clean'], R['all_releases'], REZ)
    committed = pd.read_csv('data/rez/notebook_07_catchment_results.csv').set_index('unit')['p_bootstrap']
    got = rc['per_unit'].set_index('unit')['p_bootstrap']
    maxdiff = float((got.dropna() - committed.reindex(got.dropna().index)).abs().max())
    print('SELF-CHECK vs committed notebook 07 numbers')
    print(f'  catchment: {len(rc["sig"])} sig (expect 12); set={sorted(rc["sig"])}')
    print(f'  max |p_bootstrap diff| vs committed CSV: {maxdiff:.2e}  (expect 0.0 exactly)')
    print(f'  within-window: {ww["n_sig_05"]}/{ww["n_windows"]} sig (expect 10/18); '
          f'cal nominal p={ww["cal_nominal_p"]:.3e} (expect 1.375e-17)')
    ok = (len(rc['sig']) == 12 and maxdiff < 1e-12 and ww['n_sig_05'] == 10)
    print(f'  SELF-CHECK {"PASSED" if ok else "FAILED"}')
    return ok


if __name__ == '__main__':
    import warnings; warnings.filterwarnings('ignore')
    self_check()
