"""Task 2 — fully INDEPENDENT manual re-derivation of the bootstrap-calibrated p.

Deliberately does NOT import scripts/v072_pipeline.py. Everything below — the observed
statistic, the null specification, the bootstrap loop — is re-implemented from scratch, so
a shared coding error could not pass both. Two checks per catchment:

  (A) Reproducibility: with the notebook's exact seed (seed_base 1000 + REZ-index), an
      independent re-implementation must reproduce the notebook's bootstrap count exactly.
  (B) Accuracy: an independent high-B run (different seed) gives a tight estimate of the
      true p; the notebook's B=10,000 count must be consistent with it (Poisson check).

Targets: MN (notebook p_bootstrap = 3.9996e-4, i.e. count = 3 of 10,000) and
WD (notebook p_bootstrap = 6.4994e-3, count = 64 of 10,000).
"""
import warnings; warnings.filterwarnings('ignore')
import sys; sys.path.insert(0, 'src')
from pathlib import Path
import numpy as np, pandas as pd
from nem_herding.projects import load_all_releases, join_catchment

DATA = Path('data')
REZ = ['CWO','HCC','NEW','SW-NSW','ILW','CN-VIC','MR','WV','GIP','SW-VIC','MN','SE-SA','RIV','EYR','TAS-NW',
       'WD','SD','DD','TG','WG','FNQ','CQ','SEQ']

# ---- load panel + first-entries independently (standard deterministic pandas) ----
panel = load_all_releases(DATA / 'projects' / 'aemo_geninfo')
panel = join_catchment(panel, DATA / 'rez' / 'transmission_catchment_lookup.csv')
lk = pd.read_csv(DATA / 'rez' / 'transmission_catchment_lookup.csv')
panel = panel.merge(lk[['site_name', 'phantom_risk']], on='site_name', how='left', suffixes=('', '_lk'))
panel['phantom_risk'] = pd.to_numeric(panel['phantom_risk'], errors='coerce').fillna(0).astype(int)
pc = panel[panel['phantom_risk'] < 2].copy()
ds = pc['release_date'].min(); allr = sorted(pc['release_date'].unique())
fe = (pc.sort_values('release_date').groupby('site_name', as_index=False).first()
      [['site_name', 'release_date', 'status_bucket', 'catchment', 'catchment_confidence']]
      .rename(columns={'release_date': 'first_release', 'status_bucket': 'first_status'}))
fe = fe[(fe.first_release > ds) & (fe.first_status.isin(['Proposed', 'Anticipated']))]
fe_hm = fe[fe.catchment_confidence.isin(['high', 'medium'])]

# window grid = windows where the high+medium REZ universe has >=1 first-entry (nb06-faithful)
wc_all = (fe_hm[fe_hm.catchment.isin(REZ)].groupby(['first_release', 'catchment']).size()
          .unstack(fill_value=0).reindex(columns=REZ, fill_value=0))
win = list(wc_all.index)
expo = (pc.groupby(['release_date', 'catchment']).size().unstack(fill_value=0)
        .reindex(columns=REZ, fill_value=0).reindex(index=allr, fill_value=0))
expo_lag_full = expo.shift(1).reindex(win)

def manual_derivation(catchment, notebook_count, notebook_p):
    # observed first-entry counts per window for this catchment (high+medium)
    o_full = wc_all[catchment].values.astype(float)
    lag_full = expo_lag_full[catchment].values.astype(float)
    valid = (~np.isnan(lag_full)) & (lag_full > 0)
    o = o_full[valid]; lag = lag_full[valid]
    # null: o_w ~ Poisson(e_w), e_w = lag_w * rate_hat ; rate_hat = mean over windows of o_w/lag_w
    rate_hat = np.mean(o / lag)
    e = lag * rate_hat
    T_obs = float(np.sum((o - e) ** 2 / np.maximum(e, 1e-9)))
    print(f'\n=== {catchment} ===')
    print(f'  n first-entries = {int(o.sum())}, windows used = {valid.sum()}')
    print(f'  observed per-window counts: {o.astype(int).tolist()}')
    print(f'  rate_hat (MLE) = {rate_hat:.6g}')
    print(f'  observed dispersion statistic T = {T_obs:.4f}')

    def boot(B, seed):
        rng = np.random.default_rng(seed)
        sims = rng.poisson(e, size=(B, len(e)))            # null draws
        rs = (sims / lag).mean(axis=1)                      # refit rate per sim (matches procedure)
        es = lag[None, :] * rs[:, None]
        Ts = ((sims - es) ** 2 / np.maximum(es, 1e-9)).sum(axis=1)
        cnt = int((Ts >= T_obs).sum())
        return cnt, (cnt + 1) / (B + 1)

    # (A) reproduce notebook exactly: seed_base=1000, seed = 1000 + index_in_REZ, B=10000
    seed_nb = 1000 + REZ.index(catchment)
    cntA, pA = boot(10000, seed_nb)
    print(f'  (A) reproduce w/ notebook seed {seed_nb}, B=10,000: count={cntA}, p={pA:.4e}'
          f'   | notebook: count={notebook_count}, p={notebook_p:.4e}'
          f'   -> {"MATCH" if cntA == notebook_count else "MISMATCH"}')

    # (B) independent high-B estimate of the true p (different seed)
    cntB, pB = boot(500000, 999)
    se = np.sqrt(cntB) / 500000
    print(f'  (B) independent high-B (B=500,000, seed 999): count={cntB}, p_true={pB:.4e} '
          f'(+/- {se:.1e})')
    # consistency: is the notebook's B=10,000 count consistent with true p? expected ~ p_true*10000
    exp10k = pB * 10000
    print(f'      expected count at B=10,000 given p_true: {exp10k:.1f} +/- {np.sqrt(exp10k):.1f}'
          f'  -> notebook count {notebook_count} is {abs(notebook_count-exp10k)/np.sqrt(max(exp10k,1)):.2f} sigma away')

print('INDEPENDENT MANUAL RE-DERIVATION (no import of v072_pipeline)')
manual_derivation('MN', notebook_count=3, notebook_p=3.9996e-4)
manual_derivation('WD', notebook_count=64, notebook_p=6.4994e-3)
