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
