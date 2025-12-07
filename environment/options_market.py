from environment.options_order_book import OptionsOrderBook
from utils.bs_utils import bs_price, bs_delta
import config as cfg

class OptionsMarket:
    def __init__(self, strikes=None, tau=cfg.OPTION_TAU, r=cfg.OPTION_R, q=cfg.OPTION_Q, vol=cfg.OPTION_VOL):
        self.strikes = strikes or cfg.OPTION_STRIKES
        self.tau = tau
        self.r = r
        self.q = q
        self.vol = vol
        # Для простоты — один инструмент (например, call) на каждый страйк
        self.order_books = {K: OptionsOrderBook(initial_price=bs_price(cfg.INITIAL_PRICE, K, self.r, self.q, self.vol, self.tau)) for K in self.strikes}
        self.mid_prices = {K: self.order_books[K].last_price for K in self.strikes}
        self.agents = {}

    def set_agents(self, agents):
        # agents — список агентов для опционного рынка
        self.agents = {a.id: a for a in agents}
        for ob in self.order_books.values():
            ob.agents = self.agents

    def theoretical_price(self, S, K):
        return bs_price(S, K, self.r, self.q, self.vol, self.tau, option_type='call')

    def step(self, t, S, agents):
        """S — базовый (spot) mid_price. agents — список опционных агентов"""
        trades = []
        # пересчитать теоретические цены и обновить book.mid (market makers будут размещать ордера в act)
        for K in self.strikes:
            theo = self.theoretical_price(S, K)
            # если в стакане нет ордеров — обновим last_price
            ob = self.order_books[K]
            ob.last_price = max(theo, 0.0001)

        # выполнить действия агентов
        for agent in agents:
            if hasattr(agent, 'inventory'):
                # убрать старые заявки
                for ob in self.order_books.values():
                    ob.cancel_orders_for_agent(agent.id)
            orders = agent.act({'spot': S, 'tau': self.tau, 'r': self.r, 'q': self.q, 'vol': self.vol, 'strikes': self.strikes, 'mid_prices': self.mid_prices})
            for o in orders:
                K = o.get('strike')
                if K not in self.order_books:
                    continue
                trades += self.order_books[K].add_order(o)

        # обновить mid_prices
        for K, ob in self.order_books.items():
            self.mid_prices[K] = ob.get_mid_price(last_price=ob.last_price)

        # добавить время в сделки
        for tr in trades:
            tr['time'] = t
            tr['instrument'] = 'CALL'
        return trades
