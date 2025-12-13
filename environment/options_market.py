from environment.options_order_book import OptionsOrderBook
from utils.bs_utils import bs_price, bs_delta
import config as cfg

class OptionsMarket:
    def __init__(self, strikes=None, tau=cfg.OPTION_TAU, r=cfg.OPTION_R, q=cfg.OPTION_Q, vol=cfg.OPTION_VOL, option_type = 'call'):
        self.strikes = strikes or cfg.OPTION_STRIKES
        self.tau = tau
        self.r = r
        self.q = q
        self.vol = vol
        self.option_type = option_type
        self.logger = None

        self.order_books = {
            K: {
                'call': OptionsOrderBook(
                    initial_price=bs_price(cfg.INITIAL_PRICE, K, self.r, self.q, self.vol, self.tau, option_type='call')
                ),
                'put': OptionsOrderBook(
                    initial_price=bs_price(cfg.INITIAL_PRICE, K, self.r, self.q, self.vol, self.tau, option_type='put')
                )
            }
            for K in self.strikes
        }
        self.mid_prices_call = {K: self.order_books[K]['call'].last_price for K in self.strikes}
        self.mid_prices_put = {K: self.order_books[K]['put'].last_price for K in self.strikes}
        self.agents = {}

    def set_agents(self, agents):
        self.agents = {a.id: a for a in agents}
        for K_books in self.order_books.values():  # K_books = {'call': ..., 'put': ...}
            for ob in K_books.values():  # ob = OptionsOrderBook
                ob.agents = self.agents

    def theoretical_price(self, S, K, option_type='call'):
        return bs_price(S, K, self.r, self.q, self.vol, self.tau, option_type=option_type)

    def step(self, t, S, agents, vol=None):
        trades = []
        if vol is not None:
            vol = float(vol)
            self.vol = vol

        for K in self.strikes:
            for opt_type in ['call', 'put']:
                theo = self.theoretical_price(S, K, option_type=opt_type)
                ob = self.order_books[K][opt_type]

        for agent in agents:
            for K_books in self.order_books.values():
                for ob in K_books.values():
                    ob.cancel_orders_for_agent(agent.id)

            orders = agent.act({
                'spot': S,
                'tau': self.tau,
                'r': self.r,
                'q': self.q,
                'vol': self.vol,
                'strikes': self.strikes,
                'mid_prices_call': self.mid_prices_call,
                'mid_prices_put': self.mid_prices_put
            })
            for o in orders:
                K = o.get('strike')
                opt_type = o.get('option_type', 'call')
                if K not in self.order_books or opt_type not in ['call', 'put']:
                    continue
                if hasattr(self, 'logger') and self.logger:
                    self.logger.log_option_order(t, o, agent=agent)

                new_trades = self.order_books[K][opt_type].add_order(o)
                for tr in new_trades:
                    tr['time'] = t
                    tr['instrument'] = 'option'
                    tr['strike'] = K
                    tr['option_type'] = opt_type
                trades += new_trades

        for K in self.strikes:
            self.mid_prices_call[K] = self.order_books[K]['call'].get_mid_price(self.mid_prices_call[K])
            self.mid_prices_put[K] = self.order_books[K]['put'].get_mid_price(self.mid_prices_put[K])

            self.mid_prices_call[K] = max(self.mid_prices_call[K], 0.0001)
            self.mid_prices_put[K] = max(self.mid_prices_put[K], 0.0001)

        return trades
