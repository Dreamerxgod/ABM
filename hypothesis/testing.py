import config as cfg
from utils import file_io, plotting
from hypothesis import funcs as H
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PRICE_PATH      = ROOT / "price_history.csv"
OPT_TRADES_PATH = ROOT / "option_trades.csv"
MID_CALL_PATH   = ROOT / "option_mid_call.csv"
MID_PUT_PATH    = ROOT / "option_mid_put.csv"
IV_CALL_PATH    = ROOT / "iv_call.csv"
NEWS_PATH       = ROOT / "news_history.csv"

prices       = file_io.load_price_history(str(PRICE_PATH))
option_trades = file_io.load_trades(str(OPT_TRADES_PATH))

mid_call = file_io.load_wide_series_csv(str(MID_CALL_PATH))
mid_put  = file_io.load_wide_series_csv(str(MID_PUT_PATH))
iv_call  = file_io.load_wide_series_csv(str(IV_CALL_PATH))

news = file_io.load_series_csv(str(NEWS_PATH), colname="news")

strikes = cfg.OPTION_STRIKES
r, q, T = cfg.OPTION_R, cfg.OPTION_Q, cfg.OPTION_TAU

# H2

res2 = H.run_h2(
    prices=prices,
    option_trades=option_trades,
    mid_call=mid_call,
    mid_put=mid_put,
    iv_call=iv_call,
    strikes=strikes,
    r=r, q=q, T=T
)

print("H2: arb reduces parity error & smooths IV smile")


H.print_tests("Metric: parity_mae (mean |put-call parity error|)", res2["tests"]["parity_mae"])
H.print_tests("Metric: smile_rough (mean |ΔIV| across strikes)",   res2["tests"]["smile_rough"])

plotting.plot_series(
    res2["series"]["parity_mae"],
    title="H2: mean |put-call parity error| over strikes",
    ylabel="MAE"
)
plotting.plot_series(
    res2["series"]["smile_rough"],
    title="H2: IV smile roughness (mean |ΔIV| across strikes)",
    ylabel="roughness"
)
plotting.plot_binary_regime(
    res2["series"]["arb_active"],
    title="H2: Arb active regime (rolling)"
)


# H3
res3 = H.compute_h3(
    prices=prices,
    news=news,
    iv_call=iv_call,
    strikes=strikes,
    parity_mae=res2["series"]["parity_mae"],
    news_quantile=0.8
)

print("H3 : news impact affects on higher IV sensitivity & better arb efficiency")

H.print_tests("Metric: iv_sensitivity (mean |ΔIV_t - ΔIV_{t-1}| across strikes)", res3["tests"]["iv_sensitivity"])
H.print_tests("Metric: parity_efficiency (parity_mae lower in high-news)",        res3["tests"]["parity_efficiency"])

abs_news = [abs(x) if x is not None else None for x in news]

dS = [None] * len(prices)
for t in range(1, len(prices)):
    if prices[t] is None or prices[t-1] is None:
        continue
    dS[t] = abs(float(prices[t]) - float(prices[t-1]))

plotting.plot_scatter(
    abs_news, dS,
    title="H3: News impact on spot moves",
    xlabel="|news|",
    ylabel="|ΔS|"
)

plotting.plot_series(
    res3["series"]["dIV"],
    title="H3: IV sensitivity over time (mean |ΔIV| across strikes)",
    ylabel="mean |ΔIV|"
)
