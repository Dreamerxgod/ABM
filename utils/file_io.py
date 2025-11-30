import csv

def save_price_history(filename, price_history):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['time', 'mid_price'])
        for t, price in enumerate(price_history):
            writer.writerow([t, price])

def save_trades(filename, trades):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['time', 'buyer', 'seller', 'price', 'qty'])
        for trade in trades:
            writer.writerow([trade.get('time', 0), trade['buyer'], trade['seller'], trade['price'], trade['qty']])
