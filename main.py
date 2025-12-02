from agents.noise_trader import NoiseTrader
from agents.market_maker import MarketMaker
from agents.informed_trader import InformedTrader
from agents.fundamental import FundamentalTrader
from utils.plotting import plot_price_series
from environment.news_process import NewsProcess
import config as cfg
from utils import file_io
from environment.market import Market


def main():
    agents = []

    for i in range(cfg.NUM_NOISE_TRADERS):
        agents.append(NoiseTrader(id=i+1,
                                  noise_level=cfg.NOISE_TRADER_NOISE_LEVEL))

    for i in range(cfg.NUM_MARKET_MAKERS):
        agents.append(MarketMaker(id=cfg.NUM_NOISE_TRADERS + i + 1,
                                  spread=cfg.MARKET_MAKER_SPREAD))

    for i in range(cfg.NUM_INFORMED_TRADERS):
        agents.append(InformedTrader(
            id=cfg.NUM_NOISE_TRADERS + cfg.NUM_MARKET_MAKERS + i + 1,
            sensitivity=cfg.INFORMED_TRADER_SENSITIVITY,
            aggressiveness=cfg.INFORMED_TRADER_AGGRESSIVENESS
        ))

    for i in range(cfg.NUM_FUNDAMENTAL_TRADERS):
        agents.append(FundamentalTrader(
            id=cfg.NUM_NOISE_TRADERS + cfg.NUM_MARKET_MAKERS
               + cfg.NUM_INFORMED_TRADERS + i + 1,
            fundamental_price=cfg.INITIAL_PRICE,
            aggressiveness=cfg.FUNDAMENTAL_TRADER_AGGRESSIVENESS
        ))

    market = Market(initial_price=cfg.INITIAL_PRICE)
    market.set_agents(agents)
    price_history = []
    trades = []

    WARMUP_STEPS = 50
    for t in range(WARMUP_STEPS):
        market.step(t, agents)

    for t in range(cfg.NUM_STEPS):
        step_trades = market.step(t, agents)

        # лог/дебаг
        print(f"[Time {t}] News: {market.news:.2f}")
        print(f"Mid price: {market.mid_price:.2f}\n")

        # добавляем время в сделки и копим их
        for tr in step_trades:
            tr['time'] = t
        trades.extend(step_trades)

        price_history.append(market.mid_price)

    # график
    plot_price_series(price_history)

    # CSV
    file_io.save_price_history('price_history.csv', price_history)
    file_io.save_trades('trades.csv', trades)


if __name__ == "__main__":
    main()
