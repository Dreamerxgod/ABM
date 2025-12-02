class OrderBook:
    def __init__(self, initial_price=100):
        self.bids = []      # (price, qty, agent_id)
        self.asks = []      # (price, qty, agent_id)
        self.last_price = initial_price
        self.trades = []

    def add_order(self, order):
        price = order['price']
        qty = order['qty']
        agent = order['agent_id']

        if order['side'] == 'buy':
            # сортируем по убыванию цены
            self.bids.append((price, qty, agent))
            self.bids.sort(key=lambda x: x[0], reverse=True)
        else:
            # сортируем по возрастанию цены
            self.asks.append((price, qty, agent))
            self.asks.sort(key=lambda x: x[0])

        return self.match_orders()

    def match_orders(self):
        trades = []

        # матчим, пока лучший покупатель >= лучшего продавца
        while self.bids and self.asks and self.bids[0][0] >= self.asks[0][0]:
            bid_price, bid_qty, bid_agent = self.bids[0]
            ask_price, ask_qty, ask_agent = self.asks[0]

            # не торгуем сам с собой
            if bid_agent == ask_agent:
                # Удаляем меньший ордер полностью (bid или ask)
                if bid_qty <= ask_qty:
                    self.bids.pop(0)
                    self.asks[0] = (ask_price, ask_qty - bid_qty, ask_agent)
                    if self.asks[0][1] <= 0:
                        self.asks.pop(0)
                else:
                    self.bids[0] = (bid_price, bid_qty - ask_qty, bid_agent)
                    self.asks.pop(0)
                continue

            # объём сделки
            trade_qty = min(bid_qty, ask_qty)
            trade_price = (bid_price + ask_price) / 2

            trades.append({
                'price': trade_price,
                'qty': trade_qty,
                'buyer': bid_agent,
                'seller': ask_agent
            })

            # обновляем bid
            if bid_qty > trade_qty:
                self.bids[0] = (bid_price, bid_qty - trade_qty, bid_agent)
            else:
                self.bids.pop(0)

            # обновляем ask
            if ask_qty > trade_qty:
                self.asks[0] = (ask_price, ask_qty - trade_qty, ask_agent)
            else:
                self.asks.pop(0)

        self.trades.extend(trades)
        return trades

    def get_mid_price(self, last_price=100):
        """Корректный mid-price"""
        if self.bids and self.asks:
            best_bid = self.bids[0][0]  # уже отсортировано
            best_ask = self.asks[0][0]
            mid = (best_bid + best_ask) / 2

        elif self.bids:
            mid = self.bids[0][0]

        elif self.asks:
            mid = self.asks[0][0]

        else:
            mid = last_price

        # минимальная цена — просто страховка
        return max(mid, 1.0)
