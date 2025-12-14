import math
import numpy as np
from scipy.stats import ttest_ind, mannwhitneyu, ks_2samp

# H2
def parity_error(C, P, S, K, r, q, T):
    if C is None or P is None or S is None:
        return None
    return (float(C) - float(P)) - (float(S) * math.exp(-q * T) - float(K) * math.exp(-r * T))


def mean_abs_parity_error_t(mid_call_t, mid_put_t, S, strikes, r, q, T):
    errs = []
    for K in strikes:
        C = mid_call_t.get(K)
        P = mid_put_t.get(K)
        e = parity_error(C, P, S, K, r, q, T)
        if e is None:
            continue
        if isinstance(e, float) and math.isnan(e):
            continue
        errs.append(abs(float(e)))
    return float(np.mean(errs)) if errs else None


def smile_roughness(iv_t, strikes):
    Ks = list(sorted(strikes))
    diffs = []
    for i in range(len(Ks) - 1):
        a = iv_t.get(Ks[i])
        b = iv_t.get(Ks[i + 1])
        if a is None or b is None:
            continue
        a = float(a); b = float(b)
        if (isinstance(a, float) and math.isnan(a)) or (isinstance(b, float) and math.isnan(b)):
            continue
        diffs.append(abs(b - a))
    return float(np.mean(diffs)) if diffs else None

def is_arb_trade(tr, arb_id_min=3001, arb_id_max=3999):
    b = tr.get("buyer")
    s = tr.get("seller")
    try:
        b = int(b)
        s = int(s)
    except Exception:
        return False
    return (arb_id_min <= b <= arb_id_max) or (arb_id_min <= s <= arb_id_max)


def arb_active_series(option_trades, T_max, window=20, arb_id_min=3001, arb_id_max=3999):
    hit = [0] * (T_max + 1)
    for tr in option_trades:
        t = tr.get("time")
        if t is None:
            continue
        try:
            t = int(t)
        except Exception:
            continue
        if 0 <= t <= T_max and is_arb_trade(tr, arb_id_min, arb_id_max):
            hit[t] = 1

    active = [0] * (T_max + 1)
    run = 0
    for t in range(T_max + 1):
        run += hit[t]
        if t - window >= 0:
            run -= hit[t - window]
        active[t] = 1 if run > 0 else 0
    return active

def _take(series, idxs):
    out = []
    for i in idxs:
        if 0 <= i < len(series):
            v = series[i]
            if v is None:
                continue
            v = float(v)
            if isinstance(v, float) and math.isnan(v):
                continue
            out.append(v)
    return out


def welch_ttest_p(group_a, group_b):
    if len(group_a) < 10 or len(group_b) < 10:
        return None
    _, p = ttest_ind(group_a, group_b, equal_var=False, nan_policy="omit")
    return float(p)

def mann_whitney_p(group_a, group_b):
    if len(group_a) < 10 or len(group_b) < 10:
        return None
    try:
        _, p = mannwhitneyu(group_a, group_b, alternative="two-sided")
        return float(p)
    except Exception:
        return None

def ks_test_p(group_a, group_b):
    if len(group_a) < 10 or len(group_b) < 10:
        return None
    _, p = ks_2samp(group_a, group_b)
    return float(p)

def run_3tests(group_a, group_b):
    return {
        "ttest_p": welch_ttest_p(group_a, group_b),
        "mw_p": mann_whitney_p(group_a, group_b),
        "ks_p": ks_test_p(group_a, group_b),
    }

def compute_h2(
    prices,
    mid_call,
    mid_put,
    iv_call,
    strikes,
    option_trades,
    r,
    q,
    T,
    arb_window=20
):

    T_max = min(len(prices) - 1, len(mid_call) - 1, len(mid_put) - 1, len(iv_call) - 1)
    active = arb_active_series(option_trades, T_max, window=arb_window)

    parity_mae = [None] * (T_max + 1)
    rough = [None] * (T_max + 1)

    for t in range(T_max + 1):
        S = prices[t]
        if S is None:
            continue
        parity_mae[t] = mean_abs_parity_error_t(mid_call[t], mid_put[t], S, strikes, r, q, T)
        rough[t] = smile_roughness(iv_call[t], strikes)

    idx_active = [t for t in range(T_max + 1) if active[t] == 1]
    idx_inact  = [t for t in range(T_max + 1) if active[t] == 0]

    gA_par = _take(parity_mae, idx_active)
    gI_par = _take(parity_mae, idx_inact)

    gA_rgh = _take(rough, idx_active)
    gI_rgh = _take(rough, idx_inact)

    return {
        "series": {
            "arb_active": active,
            "parity_mae": parity_mae,
            "smile_rough": rough
        },
        "groups": {
            "active_idx": idx_active,
            "inactive_idx": idx_inact,
            "active_parity": gA_par,
            "inactive_parity": gI_par,
            "active_rough": gA_rgh,
            "inactive_rough": gI_rgh
        },
        "tests": {
            # сравним inactive vs active
            "parity_mae": run_3tests(gI_par, gA_par),
            "smile_rough": run_3tests(gI_rgh, gA_rgh)
        }
    }


def run_h2(
    prices,
    option_trades,
    mid_call,
    mid_put,
    iv_call,
    strikes,
    r,
    q,
    T,
    arb_window=20
):
    return compute_h2(
        prices=prices,
        mid_call=mid_call,
        mid_put=mid_put,
        iv_call=iv_call,
        strikes=strikes,
        option_trades=option_trades,
        r=r, q=q, T=T,
        arb_window=arb_window
    )

# H3
def compute_h3(
    prices,
    news,
    iv_call,
    strikes,
    parity_mae,
    news_quantile=0.8
):

    T_max = min(len(prices), len(news), len(iv_call)) - 1

    dS = [None]
    for t in range(1, T_max + 1):
        if prices[t] is None or prices[t-1] is None:
            dS.append(None)
        else:
            dS.append(abs(prices[t] - prices[t-1]))

    dIV = [None]
    for t in range(1, T_max + 1):
        diffs = []
        for K in strikes:
            a = iv_call[t].get(K)
            b = iv_call[t-1].get(K)
            if a is None or b is None:
                continue
            diffs.append(abs(float(a) - float(b)))
        dIV.append(float(np.mean(diffs)) if diffs else None)

    abs_news = [abs(x) for x in news if x is not None]
    thr = np.quantile(abs_news, news_quantile)

    idx_high = [t for t in range(T_max + 1) if news[t] is not None and abs(news[t]) > thr]
    idx_low  = [t for t in range(T_max + 1) if news[t] is not None and abs(news[t]) <= thr]

    gH_dIV = _take(dIV, idx_high)
    gL_dIV = _take(dIV, idx_low)

    gH_par = _take(parity_mae, idx_high)
    gL_par = _take(parity_mae, idx_low)

    return {
        "series": {
            "dIV": dIV,
            "news": news,
        },
        "tests": {
            "iv_sensitivity": run_3tests(gL_dIV, gH_dIV),
            "parity_efficiency": run_3tests(gL_par, gH_par),
        }
    }
ALPHA = 0.05

def _verdict(p, alpha=ALPHA):
    if p is None:
        return "NO DATA"
    return "REJECT H0" if p < alpha else "FAIL TO REJECT H0"

def print_tests(title, tests_dict):
    print(f"\n{title}")
    p = tests_dict.get("ttest_p"); print(f"  Welch t-test   p={p:.3g} -> {_verdict(p)}" if p is not None else "  Welch t-test   p=None -> NO DATA")
    p = tests_dict.get("mw_p");    print(f"  Mann–Whitney   p={p:.3g} -> {_verdict(p)}" if p is not None else "  Mann–Whitney   p=None -> NO DATA")
    p = tests_dict.get("ks_p");    print(f"  KS test        p={p:.3g} -> {_verdict(p)}" if p is not None else "  KS test        p=None -> NO DATA")