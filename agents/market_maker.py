from agents.base_agent import Agent
import config as cfg
from utils import random_utils as ru


class MarketMaker(Agent):
    def __init__(self, id, spread=cfg.MARKET_MAKER_SPREAD,
                 max_inventory=50):
        super().__init__(id)
        self.spread = spread
        self.max_inventory = max_inventory
        self.current_inventory = 0  # стартуем с 0

    def act(self, market_state):
        mid = market_state['mid_price']

        bid_price = mid * (1 - self.spread / 2)
        ask_price = mid * (1 + self.spread / 2)

        qty_bid = ru.randint(1, 5)
        qty_ask = ru.randint(1, 5)

        orders = []

        # Может купить ТОЛЬКО если запас < max_inventory
        if self.current_inventory < self.max_inventory:
            orders.append({
                'agent_id': self.id,
                'side': 'buy',
                'price': bid_price,
                'qty': min(qty_bid, self.max_inventory - self.current_inventory),
                'type': 'limit'
            })

        # Может продать ТОЛЬКО если запас > -max_inventory
        if self.current_inventory > -self.max_inventory:
            orders.append({
                'agent_id': self.id,
                'side': 'sell',
                'price': ask_price,
                'qty': min(qty_ask, self.current_inventory + self.max_inventory),
                'type': 'limit'
            })

        return orders
