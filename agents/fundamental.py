from agents.base_agent import Agent
import config as cfg

class FundamentalTrader(Agent):
    def __init__(self, id, fundamental_price=100, aggressiveness=cfg.FUNDAMENTAL_TRADER_AGGRESSIVENESS):
        super().__init__(id)
        self.fundamental_price = fundamental_price
        self.aggressiveness = aggressiveness

    def act(self, market_state):
        mid = market_state['mid_price']
        self.fundamental_price = market_state['fundamental_price']

        deviation = self.fundamental_price - mid  # если положительное — цена ниже фундаментала
        side = 'buy' if deviation > 0 else 'sell'
        price = mid + deviation * 0.5  # корректируем цену, чтобы немного подтолкнуть рынок
        qty = max(1, int(abs(deviation) / self.aggressiveness))
        return [{'agent_id': self.id, 'side': side, 'price': price, 'qty': qty}]
