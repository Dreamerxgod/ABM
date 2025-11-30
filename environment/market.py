from environment.order_book import OrderBook

class Market:
    def __init__(self, initial_price=100):
        """
        Market хранит mid_price и стакан ордеров.
        Новости берутся извне, чтобы не дублировать генерацию.
        """
        self.mid_price = initial_price
        self.order_book = OrderBook(initial_price=initial_price)

    def get_state(self, news=0.0):
        """
        Возвращает текущее состояние рынка для агентов.
        news — значение новости извне
        """
        return {
            'mid_price': self.mid_price,
            'news': news
        }

    def step(self, t, agents, news=0.0):
        """
        Выполняет шаг рынка:
        - агенты делают действия (orders)
        - orders добавляются в order_book
        - mid_price обновляется через order_book.get_mid_price()
        """
        print(f"[Time {t}] News: {news:.2f}")

        trades = []
        for agent in agents:
            orders = agent.act(self.get_state(news=news))
            for o in orders:
                if o is None:
                    continue
                print(f"DEBUG: agent_id={agent.id} ({agent.__class__.__name__}) -> order={o}")
            for o in orders:
                trades += self.order_book.add_order(o)

        self.mid_price = self.order_book.get_mid_price()
        print(f"Mid price: {round(self.mid_price, 2)}\n")

        return trades
