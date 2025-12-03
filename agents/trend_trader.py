from agents.base_agent import Agent
import config as cfg
import numpy as np


class TrendTrader(Agent):

    def __init__(self, id,
                 lookback=cfg.TREND_TRADER_LOOKBACK,
                 threshold=cfg.TREND_TRADER_THRESHOLD,
                 aggressiveness=cfg.TREND_TRADER_AGGRESSIVENESS,
                 max_qty=cfg.TREND_TRADER_MAX_QTY):
        super().__init__(id)
        self.lookback = lookback
        self.threshold = threshold
        self.aggressiveness = aggressiveness
        self.max_qty = max_qty

        self.price_history = []
        self.last_trend = 0.0

    def _update_history(self, mid):
        self.price_history.append(mid)
        if len(self.price_history) > self.lookback:
            self.price_history.pop(0)

    # пока регрессия
    def _compute_trend(self):
        ph = self.price_history
        if len(ph) < 3:
            return 0.0

        y = np.array(ph)
        x = np.arange(len(ph))

        b = np.polyfit(x, y, 1)[0]
        trend = b / y[-1]

        return trend

    def act(self, market_state):
        mid = market_state['mid_price']
        self._update_history(mid)

        trend = self._compute_trend()
        self.last_trend = trend

        if abs(trend) < self.threshold:
            return []

        side = 'buy' if trend > 0 else 'sell'

        base_qty = int(abs(trend) / self.aggressiveness)
        qty = max(1, min(base_qty, self.max_qty))

        if side == 'buy':
            price = mid * 1.002
        else:
            price = mid * 0.998

        return [{
            'agent_id': self.id,
            'side': side,
            'price': price,
            'qty': qty,
            'type': 'limit'
        }]