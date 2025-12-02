from environment.order_book import OrderBook
from environment.news_process import NewsProcess
import config as cfg
from utils.logger import Logger

class Market:
    def __init__(self, initial_price=100.0,
                 news_probability = cfg.NEWS_PROBABILITY,
                 news_volatility=cfg.NEWS_VOLATILITY):
        self.mid_price = initial_price
        self.order_book = OrderBook(initial_price=initial_price)
        self.news_process = NewsProcess(probability=news_probability,
                                        volatility=news_volatility)
        self.news = 0.0
        self.logger = Logger()

    def update_news(self):
        self.news_process.step()
        self.news = self.news_process.get_news()

    def get_state(self):
        return {'mid_price': self.mid_price, 'news': self.news}

    def set_agents(self, agents):
        self.order_book.agents = {a.id: a for a in agents}

    def step(self, t, agents):
        self.update_news()
        state = self.get_state()

        self.logger.log_news(t, self.news)

        trades = []
        for agent in agents:
            orders = agent.act(state)
            for o in orders:
                self.logger.log_order(t, o)
                trades += self.order_book.add_order(o)

        self.mid_price = self.order_book.get_mid_price(last_price=self.mid_price)
        self.logger.log_mid_price(t, self.mid_price)

        for tr in trades:
            self.logger.log_trade(t, tr)

        return trades
