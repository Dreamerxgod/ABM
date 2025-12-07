from agents.base_agent import Agent
import config as cfg
from utils.bs_utils import bs_price, bs_delta

class OptionsArbitrageur(Agent):
    def __init__(self, id, threshold=cfg.OPTION_ARB_THRESHOLD, max_qty=5):
        super().__init__(id)
        self.threshold = threshold
        self.max_qty = max_qty

    def act(self, market_state):
        S = market_state['spot']
        strikes = market_state['strikes']
        vol = market_state['vol']
        tau = market_state['tau']

        orders = []
        for K in strikes:
            market_price = market_state['mid_prices'].get(K)
            if market_price is None:
                 continue
            theo = bs_price(S, K, market_state.get('r', 0.0), market_state.get('q', 0.0), vol, tau, option_type='call')
            if theo <= 0:
                continue
            diff = (market_price - theo) / theo
            if abs(diff) > self.threshold:
                # если опцион существенно дороже теоретического — продаём его, иначе — покупаем
                side = 'sell' if diff > 0 else 'buy'
                qty = min(self.max_qty, max(1, int(abs(diff) * 10)))
                orders.append({'agent_id': self.id, 'side': side, 'price': market_price, 'qty': qty, 'strike': K})
        return orders