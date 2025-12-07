from agents.base_agent import Agent
import config as cfg
from utils.bs_utils import bs_price

class OptionsMarketMaker(Agent):
    def __init__(self, id, base_spread_factor=cfg.OPTION_SPREAD_FACTOR, base_size=1):
        super().__init__(id)
        self.base_spread_factor = base_spread_factor
        self.base_size = base_size

    def act(self, market_state):
        # market_state содержит spot, strikes, vol, tau
        S = market_state['spot']
        vol = market_state['vol']
        tau = market_state['tau']
        K_list = market_state['strikes']

        orders = []
        for K in K_list:
            theo = bs_price(S, K, market_state.get('r', 0.0), market_state.get('q', 0.0), vol, tau, option_type='call')
            spread = max(0.0001, self.base_spread_factor * theo)
            bid = max(0.0001, theo - spread/2)
            ask = theo + spread/2
            qty = self.base_size

            orders.append({'agent_id': self.id, 'side': 'buy', 'price': bid, 'qty': qty, 'type': 'limit', 'strike': K})
            orders.append({'agent_id': self.id, 'side': 'sell', 'price': ask, 'qty': qty, 'type': 'limit', 'strike': K})
        return orders