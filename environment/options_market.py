# environment/options_market.py
from utils.bs_utils import bs_price, bs_delta
import config as cfg

class OptionsOrderBook:
    def __init__(self, strike, option_type, initial_price=1.0):
        self.strike = strike
        self.option_type = option_type
        self.bids = []  # (price, qty, agent_id)
        self.asks = []  # (price, qty, agent_id)
        self.last_price = initial_price
        self.trades = []
        self.agents = {}

    def cancel_orders_for_agent(self, agent_id):
        self.bids = [b for b in self.bids if b[2] != agent_id]
        self.asks = [a for a in self.asks if a[2] != agent_id]

    def add_order(self, order):
        price = order['price']
        qty = order['qty']
        agent = order['agent_id']
        side = order['side']

        if side == 'buy':
            self.bids.append((price, qty, agent))
            self.bids.sort(key=lambda x: x[0], reverse=True)
        else:
            self.asks.append((price, qty, agent))
            self.asks.sort(key=lambda x: x[0])

        return self.match_orders()

    def match_orders(self):
        trades = []
        while self.bids and self.asks and self.bids[0][0] >= self.asks[0][0]:
            bid_price, bid_qty, bid_agent = self.bids[0]
            ask_price, ask_qty, ask_agent = self.asks[0]

            if bid_agent == ask_agent:
                # self-cross skip
                if bid_qty <= ask_qty:
                    self.bids.pop(0)
                else:
                    self.bids[0] = (bid_price, bid_qty - ask_qty, bid_agent)
                continue

            trade_qty = min(bid_qty, ask_qty)

            for agent_id, delta in [(bid_agent, +trade_qty), (ask_agent, -trade_qty)]:
                agent_obj = self.agents.get(agent_id)
                if agent_obj is not None:
                    if hasattr(agent_obj, "inventory_by_option"):
                        key = (self.strike, self.option_type)
                        agent_obj.inventory_by_option[key] = agent_obj.inventory_by_option.get(key, 0) + delta
                    if hasattr(agent_obj, "inventory"):
                        agent_obj.inventory += delta

            trade_price = (bid_price + ask_price) / 2

            trades.append({
                'price': trade_price,
                'qty': trade_qty,
                'buyer': bid_agent,
                'seller': ask_agent
            })

            if bid_qty > trade_qty:
                self.bids[0] = (bid_price, bid_qty - trade_qty, bid_agent)
            else:
                self.bids.pop(0)

            if ask_qty > trade_qty:
                self.asks[0] = (ask_price, ask_qty - trade_qty, ask_agent)
            else:
                self.asks.pop(0)

            self.last_price = trade_price

        self.trades.extend(trades)
        return trades

    def get_mid_price(self, last_price=1.0):
        if self.bids and self.asks:
            mid = (self.bids[0][0] + self.asks[0][0]) / 2
        elif self.bids:
            mid = self.bids[0][0]
        elif self.asks:
            mid = self.asks[0][0]
        else:
            mid = last_price
        return max(mid, 0.0001)


class OptionsMarket:
    def __init__(self, strikes=None, tau=cfg.OPTION_TAU, r=cfg.OPTION_R, q=cfg.OPTION_Q, vol=cfg.OPTION_VOL):
        self.strikes = strikes or cfg.OPTION_STRIKES
        self.tau = tau
        self.r = r
        self.q = q
        self.vol = vol
        self.logger = None

        self.order_books = {
            K: {
                'call': OptionsOrderBook(
                    strike=K,
                    option_type='call',
                    initial_price=bs_price(cfg.INITIAL_PRICE, K, self.r, self.q, self.vol, self.tau, option_type='call')
                ),
                'put': OptionsOrderBook(
                    strike=K,
                    option_type='put',
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
        for K_books in self.order_books.values():
            for ob in K_books.values():
                ob.agents = self.agents

    def theoretical_price(self, S, K, option_type='call'):
        return bs_price(S, K, self.r, self.q, self.vol, self.tau, option_type=option_type)

    def step(self, t, S, agents, spot_order_book=None):

        trades = []

        for agent in agents:
            for K_books in self.order_books.values():
                for ob in K_books.values():
                    ob.cancel_orders_for_agent(agent.id)

        for agent in agents:
            orders = agent.act({'spot': S, 'tau': self.tau, 'r': self.r, 'q': self.q, 'vol': self.vol,
                                'strikes': self.strikes,
                                'mid_prices_call': self.mid_prices_call,
                                'mid_prices_put': self.mid_prices_put})
            for o in orders:
                if o.get('instrument') == 'spot':
                    if spot_order_book is not None:
                        if hasattr(self, 'logger') and self.logger:
                            self.logger.log_order(t, o, agent=agent)
                        new_trades = spot_order_book.add_order(o)
                        for tr in new_trades:
                            tr['time'] = t
                            if hasattr(self, 'logger') and self.logger:
                                self.logger.log_trade(t, tr)
                    continue

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

        if spot_order_book is not None:
            for agent in agents:
                inv_map = getattr(agent, "inventory_by_option", None)
                if not inv_map:
                    continue

                delta_exposure = 0.0
                for (K, opt_type), qty in inv_map.items():
                    if qty == 0:
                        continue
                    d = bs_delta(S, K, self.r, self.q, self.vol, self.tau, option_type=opt_type)
                    delta_exposure += qty * d

                hedge_qty = int(round(abs(delta_exposure)))

                if hedge_qty <= 0:
                    continue

                if delta_exposure > 0:
                    side = 'sell'
                    price = max(0.0001, S - 0.0001)
                else:
                    side = 'buy'
                    price = S + 0.0001

                spot_order = {
                    'agent_id': agent.id,
                    'instrument': 'spot',
                    'order_type': 'limit',
                    'side': side,
                    'price': float(price),
                    'qty': hedge_qty
                }

                if hasattr(self, 'logger') and self.logger:
                    self.logger.log_order(t, spot_order, agent=agent)
                spot_trades = spot_order_book.add_order(spot_order)
                for tr in spot_trades:
                    tr['time'] = t
                    if hasattr(self, 'logger') and self.logger:
                        self.logger.log_trade(t, tr)

        return trades
