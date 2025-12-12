from agents.noise_trader import NoiseTrader
from agents.market_maker import MarketMaker
from agents.informed_trader import InformedTrader
from agents.fundamental import FundamentalTrader
from utils.plotting import plot_price_series
from utils.plotting import plot_options_prices
from environment.news_process import NewsProcess
import config as cfg
from utils import file_io
from environment.market import Market
from agents.trend_trader import TrendTrader
from environment.options_market import OptionsMarket
from agents.options_market_maker import OptionsMarketMaker
from agents.options_noise_trader import OptionsNoiseTrader
from agents.options_arbitrageur import OptionsArbitrageur
from utils.logger import Logger

def main():
    agents = []

    for i in range(cfg.NUM_NOISE_TRADERS):
        agents.append(NoiseTrader(id=i+1,
                                  noise_level=cfg.NOISE_TRADER_NOISE_LEVEL))

    for i in range(cfg.NUM_MARKET_MAKERS):
        agents.append(MarketMaker(
            id=cfg.NUM_NOISE_TRADERS + i + 1,
            base_spread=cfg.MM_BASE_SPREAD,
            inventory_risk_aversion=cfg.MM_INV_RISK,
            max_inventory=cfg.MM_MAX_INVENTORY,
            base_size=cfg.MM_BASE_SIZE
        ))

    for i in range(cfg.NUM_INFORMED_TRADERS):
        agents.append(InformedTrader(
            id=cfg.NUM_NOISE_TRADERS + cfg.NUM_MARKET_MAKERS + i + 1,
            sensitivity=cfg.INFORMED_TRADER_SENSITIVITY,
            aggressiveness=cfg.INFORMED_TRADER_AGGRESSIVENESS
        ))

    for i in range(cfg.NUM_TREND_TRADERS):
        agents.append(TrendTrader(
            id=cfg.NUM_NOISE_TRADERS
               + cfg.NUM_MARKET_MAKERS
               + cfg.NUM_INFORMED_TRADERS
               + i + 1
        ))

    for i in range(cfg.NUM_FUNDAMENTAL_TRADERS):
        agents.append(FundamentalTrader(
            id=cfg.NUM_NOISE_TRADERS
               + cfg.NUM_MARKET_MAKERS
               + cfg.NUM_INFORMED_TRADERS
               + cfg.NUM_TREND_TRADERS
               + i + 1,
            fundamental_price=cfg.INITIAL_PRICE,
            aggressiveness=cfg.FUNDAMENTAL_TRADER_AGGRESSIVENESS
        ))

    market = Market(initial_price=cfg.INITIAL_PRICE)
    market.set_agents(agents)

    logger = Logger(enable_console=True)

    market = Market(initial_price=cfg.INITIAL_PRICE)
    market.logger = logger


    options_market = OptionsMarket(
        strikes=cfg.OPTION_STRIKES,
        tau=cfg.OPTION_TAU,
        r=cfg.OPTION_R,
        q=cfg.OPTION_Q,
        vol=cfg.OPTION_VOL
    )
    options_market.logger = logger

    options_agents = []
    for i in range(cfg.NUM_OPTION_MARKET_MAKERS):
        options_agents.append(OptionsMarketMaker(
            id=1000 + i + 1,
        ))

    for i in range(cfg.NUM_OPTION_NOISE_TRADERS):
        options_agents.append(OptionsNoiseTrader(
            id=2000 + i + 1,
        ))

    for i in range(cfg.NUM_OPTION_ARB):
        options_agents.append(OptionsArbitrageur(
            id=3000 + i + 1,
        ))

    options_market.set_agents(options_agents)

    price_history = []
    trades = []
    option_trades = []
    option_price_history_call = []
    option_price_history_put = []

    #logger = Logger(enable_console=True)

    for t in range(cfg.WARMUP_STEPS):
        market.step(t, agents)

    for t in range(cfg.WARMUP_STEPS, cfg.WARMUP_STEPS + cfg.NUM_STEPS):
        step_trades = market.step(t, agents)

        # лог/дебаг
        print(f"[Time {t}] News: {market.news:.2f}")
        print(f"Mid price: {market.mid_price:.2f}\n")

        # добавляем время в сделки и копим их
        for tr in step_trades:
            tr['time'] = t
        trades.extend(step_trades)


        price_history.append(market.mid_price)
        S = market.mid_price

        opt_trades = options_market.step(
            t=t,
            S=S,
            agents=options_agents
        )

        option_price_history_call.append(options_market.mid_prices_call.copy())
        option_price_history_put.append(options_market.mid_prices_put.copy())

        option_trades.extend(opt_trades)

        # затем внутри цикла:
        for tr in opt_trades:
            logger.log_option_trade(t, tr)  # экземпляр logger, а не класс



    # график
    plot_price_series(price_history)
    # график опционов
    plot_options_prices(option_price_history_call, strikes=cfg.OPTION_STRIKES, title='Call Options Prices')
    plot_options_prices(option_price_history_put, strikes=cfg.OPTION_STRIKES, title='Put Options Prices')

    # CSV
    file_io.save_price_history('price_history.csv', price_history)
    file_io.save_trades('trades.csv', trades)
    file_io.save_trades('option_trades.csv', option_trades)


if __name__ == "__main__":
    main()
