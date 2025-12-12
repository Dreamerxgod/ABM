from agents.base_agent import Agent
import config as cfg
from utils.bs_utils import bs_price

class OptionsArbitrageur(Agent):
    def __init__(self, id, threshold=cfg.OPTION_ARB_THRESHOLD, max_qty=5):
        super().__init__(id)
        self.threshold = threshold
        self.max_qty = max_qty

    def act(self, market_state):
        S = market_state['spot']
        strikes = market_state['strikes']
        vol = market_state['vol']
        tau = market_state['tau']
        r = market_state.get('r', 0.0)
        q = market_state.get('q', 0.0)

        mid_prices_call = market_state['mid_prices_call']
        mid_prices_put = market_state['mid_prices_put']

        orders = []

        for K in strikes:
            C_market = mid_prices_call.get(K)
            P_market = mid_prices_put.get(K)

            if C_market is None or P_market is None:
                continue

            C_theo = bs_price(S, K, r, q, vol, tau, option_type='call')
            P_theo = bs_price(S, K, r, q, vol, tau, option_type='put')

            if C_theo <= 0 or P_theo <= 0:
                continue

            parity_diff = (C_market - P_market) - (S - K * (2.71828 ** (-r * tau)))

            if abs(parity_diff) > self.threshold:
                if parity_diff > 0:
                    orders.append({'agent_id': self.id, 'side': 'sell', 'price': C_market, 'qty': self.max_qty, 'strike': K, 'type': 'call'})
                    orders.append({'agent_id': self.id, 'side': 'buy', 'price': P_market, 'qty': self.max_qty, 'strike': K, 'type': 'put'})
                else:
                    orders.append({'agent_id': self.id, 'side': 'buy', 'price': C_market, 'qty': self.max_qty, 'strike': K, 'type': 'call'})
                    orders.append({'agent_id': self.id, 'side': 'sell', 'price': P_market, 'qty': self.max_qty, 'strike': K, 'type': 'put'})

        return orders
