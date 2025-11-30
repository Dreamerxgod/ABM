from agents.base_agent import Agent
import random

class MarketMaker(Agent):
    def __init__(self, id, spread=0.05):
        super().__init__(id)
        self.spread = spread

    def act(self, market_state):
        mid_price = market_state['mid_price']
        bid_price = mid_price * (1 - self.spread/2)
        ask_price = mid_price * (1 + self.spread/2)
        qty_bid = random.randint(1, 5)
        qty_ask = random.randint(1, 5)
        return [
            {'agent_id': self.id, 'side': 'buy', 'price': bid_price, 'qty': qty_bid, 'type': 'limit'},
            {'agent_id': self.id, 'side': 'sell', 'price': ask_price, 'qty': qty_ask, 'type': 'limit'}
        ]
