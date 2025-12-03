import csv
import json
from datetime import datetime
import os


class Logger:
    def __init__(self, trades_file="logs/trades.csv",
                 events_file="logs/events.log",
                 enable_console=True):
        self.trades_file = trades_file
        self.events_file = events_file
        self.enable_console = enable_console
        os.makedirs(os.path.dirname(self.trades_file), exist_ok=True)

        # заголовок CSV
        with open(self.trades_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["time", "price", "qty", "buyer", "seller"])

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")

        # в файл .log
        with open(self.events_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

        # optionally выводить в консоль
        if self.enable_console:
            print(f"[{timestamp}] {message}")

    def log_trade(self, t, trade):
        with open(self.trades_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                t,
                trade["price"],
                trade["qty"],
                trade["buyer"],
                trade["seller"]
            ])

        if self.enable_console:
            print(f"[TRADE t={t}] "
                  f"{trade['buyer']} -> {trade['seller']} | "
                  f"qty={trade['qty']} price={trade['price']:.2f}")

    def log_news(self, t, news):
        self.log(f"[NEWS t={t}] news={news:.3f}")

    def log_mid_price(self, t, mid):
        self.log(f"[MID t={t}] mid_price={mid:.2f}")

    def log_order(self, t, order, agent=None):
        trader_type = agent.__class__.__name__ if agent is not None else "Unknown"

        inventory = getattr(agent, 'inventory', None)
        inv_str = f" inv={inventory}" if inventory is not None else ""

        trend = getattr(agent, 'last_trend', None)
        trend_str = f" trend={trend:+.4f}" if trend is not None else ""

        self.log(
            f"[ORDER t={t}] "
            f"{trader_type}({order['agent_id']}) {order['side']} "
            f"p={order['price']:.2f} qty={order['qty']}{inv_str}{trend_str}"
        )