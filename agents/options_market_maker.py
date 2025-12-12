from agents.base_agent import Agent
import config as cfg
from utils.bs_utils import bs_price

class OptionsMarketMaker(Agent):
    def __init__(self, id, base_spread_factor=cfg.OPTION_SPREAD_FACTOR, base_size=1):
        super().__init__(id)
        self.inventory = 0  # <-- добавь
        self.base_spread_factor = base_spread_factor
        self.base_size = base_size


    def act(self, market_state):
        S = market_state['spot']
        vol = market_state['vol']
        tau = market_state['tau']
        r = market_state.get('r', 0.0)
        q = market_state.get('q', 0.0)
        strikes = market_state['strikes']

        orders = []
        for K in strikes:
            for option_type in ['call', 'put']:
                theo = bs_price(S, K, r, q, vol, tau, option_type=option_type)

                theo = max(float(theo), 0.0001)  # защита от нулей
                spread = max(0.0001, self.base_spread_factor * theo)

                bid = max(0.0001, theo - spread / 2)
                ask = theo + spread / 2
                qty = int(self.base_size)

                orders.append({
                    'agent_id': self.id,
                    'instrument': 'option',
                    'order_type': 'limit',
                    'side': 'buy',
                    'price': float(bid),
                    'qty': qty,
                    'strike': K,
                    'option_type': option_type,
                })

                orders.append({
                    'agent_id': self.id,
                    'instrument': 'option',
                    'order_type': 'limit',
                    'side': 'sell',
                    'price': float(ask),
                    'qty': qty,
                    'strike': K,
                    'option_type': option_type,
                })

        return orders