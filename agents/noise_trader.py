# agents/noise_trader.py
import random
from agents.base_agent import Agent

class NoiseTrader(Agent):
    def __init__(self, id, noise_level=0.05):
        super().__init__(id)
        self.noise_level = noise_level

    def act(self, market_state):
        mid = market_state['mid_price']
        price = mid * (1 + random.uniform(-self.noise_level, self.noise_level))
        qty = random.randint(1, 5)
        side = random.choice(['buy', 'sell'])
        return [{'agent_id': self.id, 'side': side, 'price': price, 'qty': qty}]
