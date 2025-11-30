class Agent:
    def __init__(self, id):
        self.id = id

    def act(self, market_state):
        """Возвращает список ордеров: [{'agent_id', 'side', 'price', 'qty', 'type'}]"""
        raise NotImplementedError
