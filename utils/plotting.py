import matplotlib.pyplot as plt

def plot_price_series(price_history):
    plt.figure(figsize=(10, 5))
    plt.plot(price_history, label='Mid Price')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.title('Price Evolution')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_options_prices(option_price_history, strikes, title='Options Prices Evolution'):
    plt.figure(figsize=(12, 6))
    for K in strikes:
        prices = [step[K] for step in option_price_history]
        plt.plot(prices, label=f'Strike {K}')
    plt.xlabel('Time')
    plt.ylabel('Option Price')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_realised_vol(rv_history, rv_avg, title="Realised Vol"):
    import matplotlib.pyplot as plt
    rv_plot = [x if x is not None else float("nan") for x in rv_history]
    avg_plot = [x if x is not None else float("nan") for x in rv_avg]

    plt.figure(figsize=(12, 5))
    plt.plot(rv_plot, label="Realised vol")
    plt.plot(avg_plot, label="Average vol")
    plt.xlabel("Time")
    plt.ylabel("Vol (annualized)")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.show()

def plot_implied_vol_series(iv_history, strikes, title="Implied Volatility"):
    """
    iv_history: список словарей {K: iv} на каждом шаге
    strikes: список страйков
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 5))
    for K in strikes:
        series = [step.get(K, float("nan")) for step in iv_history]
        # None -> nan
        series = [x if x is not None else float("nan") for x in series]
        plt.plot(series, label=f"K={K}")

    plt.xlabel("Time")
    plt.ylabel("IV (annualized)")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.show()
