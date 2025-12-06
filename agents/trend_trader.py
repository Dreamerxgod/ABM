from agents.base_agent import Agent
import numpy as np
from collections import deque

class TrendTrader(Agent):
    def __init__(self, id,
                 lookback=20,
                 threshold=0.2,
                 k=0.01,
                 max_qty=20):
        super().__init__(id)
        self.lookback = lookback
        self.threshold = threshold
        self.k = k
        self.max_qty = max_qty
        self.price_history = deque(maxlen=lookback)

    def atr(self):
        if len(self.price_history) < 20:
            return None
        closes = np.array(self.price_history)
        returns = np.abs(np.diff(closes))
        atr = np.mean(returns)
        return atr if atr > 0 else None

    def trend(self):
        if len(self.price_history) < 10:
            return 0
        prices = np.array(self.price_history)
        logp = np.log(prices)
        x = np.arange(len(logp))
        slope = np.polyfit(x, logp, 1)[0]
        ret = np.diff(logp)
        vol = np.std(ret) if len(ret) > 1 else 0
        if vol == 0:
            return 0
        return slope / vol

    def act(self, market_state):
        mid = market_state['mid_price']
        self.price_history.append(mid)

        trend = self.trend()
        if abs(trend) < self.threshold:
            return []

        atr = self.atr()
        if atr is None:
            return []


        side = 'buy' if trend > 0 else 'sell'
        qty = max(1, int(self.max_qty * (1 - np.exp(-abs(trend)/self.threshold))))


        spread = mid * 0.05
        price = mid + (spread / 2 if side == 'buy' else -spread / 2)

        return [{
            'agent_id': self.id,
            'side': side,
            'price': price,
            'qty': qty,
            'type': 'limit'
        }]
