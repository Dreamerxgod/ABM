# agents/informed_trader.py
from agents.base_agent import Agent
import random

class InformedTrader(Agent):
    def __init__(self, id, sensitivity=0.5, aggressiveness=0.1):
        super().__init__(id)
        self.sensitivity = sensitivity
        self.aggressiveness = aggressiveness

    def act(self, market_state):
        mid = market_state['mid_price']
        news = market_state['news']
        price_move = self.sensitivity * news
        price = mid + price_move
        qty = max(1, int(abs(news) / self.aggressiveness))
        side = 'buy' if news > 0 else 'sell'
        return [{'agent_id': self.id, 'side': side, 'price': price, 'qty': qty}]
