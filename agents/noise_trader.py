from agents.base_agent import Agent
from utils import random_utils as ru

class NoiseTrader(Agent):

    def __init__(self, id, noise_level=0.05):
        super().__init__(id)
        self.noise_level = noise_level

    def act(self, market_state):
        mid = market_state['mid_price']
        price = mid * (1 + ru.uniform(-self.noise_level, self.noise_level))
        qty = ru.randint(1, 5)
        side = ru.choice(['buy', 'sell'])

        return [{'agent_id': self.id, 'side': side, 'price': price, 'qty': qty}]
