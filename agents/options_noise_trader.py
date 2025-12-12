from agents.base_agent import Agent
from utils import random_utils as ru

class OptionsNoiseTrader(Agent):
    def __init__(self, id, max_qty=2, noise=0.3):
        super().__init__(id)
        self.max_qty = max_qty
        self.noise = noise

    def act(self, market_state):
        S = market_state['spot']
        strikes = market_state['strikes']

        if ru.choice([True, False]):
            K = ru.choice(strikes)
            option_type = ru.choice(['call', 'put'])  # выбираем тип опциона
            if option_type == 'call':
                price = market_state['mid_prices_call'].get(K, 1.0) * (1 + ru.uniform(-self.noise, self.noise))
            else:
                price = market_state['mid_prices_put'].get(K, 1.0) * (1 + ru.uniform(-self.noise, self.noise))

            qty = ru.randint(1, self.max_qty)
            side = ru.choice(['buy', 'sell'])
            return [{'agent_id': self.id, 'side': side, 'price': price, 'qty': qty, 'strike': K, 'type': option_type}]

        return []
