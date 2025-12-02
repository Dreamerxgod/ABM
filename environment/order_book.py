class OrderBook:
    def __init__(self, initial_price=100):
        self.bids = []
        self.asks = []
        self.last_price = initial_price
        self.trades = []


    def add_order(self, order):
        if order['side'] == 'buy':
            self.bids.append((order['price'], order['qty'], order['agent_id']))
            self.bids.sort(reverse=True)
        else:
            self.asks.append((order['price'], order['qty'], order['agent_id']))
            self.asks.sort()
        return self.match_orders()

    def match_orders(self):
        trades = []
        while self.bids and self.asks and self.bids[0][0] >= self.asks[0][0]:
            bid_price, bid_qty, bid_agent = self.bids[0]
            ask_price, ask_qty, ask_agent = self.asks[0]

            # Игнорируем сделки внутри одного агента
            if bid_agent == ask_agent:
                # Убираем один из ордеров, чтобы не застрять
                if bid_qty <= ask_qty:
                    self.bids.pop(0)
                else:
                    self.bids[0] = (bid_qty - ask_qty, bid_agent, bid_agent)
                continue

            trade_qty = min(bid_qty, ask_qty)
            trade_price = (bid_price + ask_price)/2
            trades.append({'price': trade_price, 'qty': trade_qty, 'buyer': bid_agent, 'seller': ask_agent})

            # Обновляем заявки
            if bid_qty > trade_qty:
                self.bids[0] = (bid_qty - trade_qty, bid_agent, bid_agent)
            else:
                self.bids.pop(0)

            if ask_qty > trade_qty:
                self.asks[0] = (ask_qty - trade_qty, ask_agent, ask_agent)
            else:
                self.asks.pop(0)

        self.trades.extend(trades)
        return trades

    def get_mid_price(self, last_price=100):
        """
        Возвращает mid-price. Если нет bids/asks — используем last_price.
        """
        if self.bids and self.asks:
            best_bid = max(self.bids)[0]
            best_ask = min(self.asks)[0]
            mid = (best_bid + best_ask) / 2
        elif self.bids:
            mid = max(self.bids)[0]
        elif self.asks:
            mid = min(self.asks)[0]
        else:
            mid = last_price

        # Минимальная цена
        mid = max(mid, 1.0)
        return mid



