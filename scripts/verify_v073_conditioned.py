"""v0.7.3 re-verification: the window-total-conditioned temporal test.

(1) Type I under synthetic null (rate proportional to exposure baseline).
(2) Permutation collapse — the confirmation criterion. The v0.7.2 (unconditioned) temporal
    test only dropped 12 -> ~7.7 significant catchments under permutation; the conditioned
    test should collapse close to null (the way the within-window §5 test does).
"""
import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from scipy import stats
import v072_pipeline as P

R = P.load_real()
pc, allr, ds = R['panel_clean'], R['all_releases'], R['data_start']
fe_hm = R['fe_hm']
RES = [('catchment', P.REZ, fe_hm[fe_hm.catchment.isin(P.REZ)]),
       ('cluster', P.CLUSTER_ORDER, fe_hm[fe_hm.cluster.notna()]),
       ('state', ['NSW','VIC','SA','QLD'], fe_hm[fe_hm.state.isin(['NSW','VIC','SA','QLD'])])]

print('='*70); print('REAL DATA — conditioned temporal significant counts (B=100,000)'); print('='*70)
real = {}
for col, units, sub in RES:
    r = P.conditioned_temporal(sub, pc, allr, col, units, B=100000, seed=11)
    real[col] = r
    print(f'  {col:9}: {len(r["sig"])}/{r["N_tested"]} significant -> {sorted(r["sig"])}')

print('\n' + '='*70); print('(1) TYPE I — synthetic null (rate proportional to exposure), conditioned test'); print('='*70)
EL = P.exposure_lag_matrix(pc, allr, ds, P.REZ).fillna(0.0); ELv = EL.values; lam = 1023 / ELv.sum()
win = list(EL.index)
allp = []; fpr = []
for run in range(20):
    rng = np.random.default_rng(5000 + run)
    counts = rng.poisson(lam * ELv)
    wi, ui = np.nonzero(counts); reps = counts[wi, ui]
    fe_df = pd.DataFrame({'first_release': np.repeat([win[i] for i in wi], reps),
                          'catchment': np.repeat([P.REZ[i] for i in ui], reps)})
    r = P.conditioned_temporal(fe_df, pc, allr, 'catchment', P.REZ, B=10000, seed=900 + run)
    tt = r['per_unit'][r['per_unit'].tested & r['per_unit'].p_conditioned.notna()]
    fpr.append((tt.p_conditioned < 0.05).mean()); allp.extend(tt.p_conditioned.tolist())
allp = np.array(allp)
print(f'  uncorrected FPR: {np.mean(fpr)*100:.2f}% (nominal 5%)')
print(f'  pooled p: mean={allp.mean():.3f} (uniform->0.5), frac<0.05={np.mean(allp<0.05)*100:.2f}%, '
      f'KS vs Uniform p={stats.kstest(allp,"uniform").pvalue:.3f}')

print('\n' + '='*70); print('(2) PERMUTATION COLLAPSE — conditioned test (confirmation criterion)'); print('='*70)
for col, units, sub in RES:
    win_counts = sub.groupby('first_release').size()
    expo = (pc.groupby(['release_date', col]).size().unstack(fill_value=0)
            .reindex(columns=units, fill_value=0).reindex(index=allr, fill_value=0))
    w = sorted(sub.first_release.unique()); el = expo.shift(1).reindex(w).fillna(0.0)
    sigs = []
    for k in range(20):
        rng = np.random.default_rng(7000 + k); rows = []
        for ww, n in win_counts.items():
            if ww not in el.index: continue
            sh = el.loc[ww].values.astype(float)
            if sh.sum() == 0: continue
            sh = sh / sh.sum()
            rows.append(pd.DataFrame({'first_release': [ww]*int(n), col: rng.choice(units, size=int(n), p=sh)}))
        fp = pd.concat(rows, ignore_index=True)
        r = P.conditioned_temporal(fp, pc, allr, col, units, B=20000, seed=300 + k)
        sigs.append(len(r['sig']))
    sigs = np.array(sigs)
    print(f'  {col:9}: real conditioned={len(real[col]["sig"])}; permuted mean={sigs.mean():.2f} '
          f'range {sigs.min()}-{sigs.max()} (nominal ~{0.05*real[col]["N_tested"]:.1f})  '
          f'[v0.7.2 unconditioned permuted was ~7.7 at catchment]')
