from agents.base_agent import Agent
import config as cfg
from utils import random_utils as ru


class MarketMaker(Agent):
    def __init__(self, id,
                 spread=cfg.MARKET_MAKER_SPREAD,
                 max_inventory=50,
                 mean_reversion_speed=0.3,
                 max_step_frac=0.3):
        super().__init__(id)
        self.spread = spread
        self.max_inventory = max_inventory
        self.inventory = 0

        self.mean_reversion_speed = mean_reversion_speed
        self.max_step_frac = max_step_frac

    def _compute_quantities(self):
        target_inventory = 0

        # желательное изменение инвентаря
        desired_change = self.mean_reversion_speed * (target_inventory - self.inventory)

        max_step = int(self.max_inventory * self.max_step_frac)
        if max_step < 1:
            max_step = 1

        desired_change = max(-max_step, min(max_step, int(round(desired_change))))

        # чуть шуму
        noise = ru.randint(-1, 1)
        desired_change += noise

        # сколько вообще можем ещё купить/продать с учётом лимитов
        capacity_long = max(0, self.max_inventory - self.inventory)      # запас до +max_inventory
        capacity_short = max(0, self.inventory + self.max_inventory)     # запас до -max_inventory (по модулю)

        qty_bid = 0
        qty_ask = 0

        if desired_change > 0:
            qty_bid = min(desired_change, capacity_long)
            small_sell = max(0, ru.randint(0, 2))
            qty_ask = min(small_sell, capacity_short)
        elif desired_change < 0:
            qty_ask = min(-desired_change, capacity_short)
            small_buy = max(0, ru.randint(0, 2))
            qty_bid = min(small_buy, capacity_long)
        else:
            base = ru.randint(1, 3)
            qty_bid = min(base, capacity_long)
            qty_ask = min(base, capacity_short)

        return qty_bid, qty_ask

    def act(self, market_state):
        mid = market_state['mid_price']

        bid_price = mid * (1 - self.spread / 2)
        ask_price = mid * (1 + self.spread / 2)

        qty_bid, qty_ask = self._compute_quantities()

        orders = []

        # ограничения на покупку
        if self.inventory < self.max_inventory and qty_bid > 0:
            orders.append({
                'agent_id': self.id,
                'side': 'buy',
                'price': bid_price,
                'qty': min(qty_bid, self.max_inventory - self.inventory),
                'type': 'limit'
            })

        # ограничения на продажу
        if self.inventory > -self.max_inventory and qty_ask > 0:
            orders.append({
                'agent_id': self.id,
                'side': 'sell',
                'price': ask_price,
                'qty': min(qty_ask, self.inventory + self.max_inventory),
                'type': 'limit'
            })

        return orders
