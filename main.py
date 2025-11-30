from agents.noise_trader import NoiseTrader
from agents.market_maker import MarketMaker
from agents.informed_trader import InformedTrader
from agents.fundamental import FundamentalTrader
from utils.plotting import plot_price_series
from environment.news_process import NewsProcess
import config as cfg
from utils import file_io

class Market:
    def __init__(self, initial_price=100.0, news_probability = cfg.NEWS_PROBABILITY, news_volatility=cfg.NEWS_VOLATILITY):
        self.mid_price = initial_price
        self.news_process = NewsProcess(probability=news_probability, volatility=news_volatility)
        self.news = 0.0

    def update_news(self):
        self.news_process.step()
        self.news = self.news_process.get_news()

    def get_state(self):
        return {'mid_price': self.mid_price, 'news': self.news}

def main():
    agents = []

    for i in range(cfg.NUM_NOISE_TRADERS):
        agents.append(NoiseTrader(id=i+1, noise_level=cfg.NOISE_TRADER_NOISE_LEVEL))

    for i in range(cfg.NUM_MARKET_MAKERS):
        agents.append(MarketMaker(id=cfg.NUM_NOISE_TRADERS+i+1, spread=cfg.MARKET_MAKER_SPREAD))

    for i in range(cfg.NUM_INFORMED_TRADERS):
        agents.append(InformedTrader(
            id=cfg.NUM_NOISE_TRADERS + cfg.NUM_MARKET_MAKERS + i + 1,
            sensitivity=cfg.INFORMED_TRADER_SENSITIVITY,
            aggressiveness=cfg.INFORMED_TRADER_AGGRESSIVENESS
        ))
    for i in range(cfg.NUM_FUNDAMENTAL_TRADERS):
        agents.append(FundamentalTrader(
            id=cfg.NUM_NOISE_TRADERS + cfg.NUM_MARKET_MAKERS + cfg.NUM_INFORMED_TRADERS + i + 1,
            fundamental_price=cfg.INITIAL_PRICE,
            aggressiveness=cfg.FUNDAMENTAL_TRADER_AGGRESSIVENESS
        ))

    market = Market(initial_price=cfg.INITIAL_PRICE)
    price_history = []
    trades = []


    for t in range(cfg.NUM_STEPS):
        market.update_news()
        state = market.get_state()
        print(f"[Time {t}] News: {market.news:.2f}")

        all_orders = []
        for agent in agents:
            orders = agent.act(state)
            all_orders.extend(orders)
            for o in orders:
                trades.append({
                    'time': t,
                    'buyer': o['agent_id'] if o['side'] == 'buy' else None,
                    'seller': o['agent_id'] if o['side'] == 'sell' else None,
                    'price': o['price'],
                    'qty': o['qty']
                })
                print(f"DEBUG: agent_id={o['agent_id']} -> order={o}")

        # обновление mid_price через среднюю цену всех ордеров
        all_prices = [o['price'] for o in all_orders]
        if all_prices:
            market.mid_price = sum(all_prices)/len(all_prices)
        price_history.append(market.mid_price)
        print(f"Mid price: {market.mid_price:.2f}\n")

    # построение графика
    plot_price_series(price_history)

    # сохранение в CSV
    file_io.save_price_history('price_history.csv', price_history)
    file_io.save_trades('trades.csv', trades)

if __name__ == "__main__":
    main()
