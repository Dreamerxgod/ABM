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