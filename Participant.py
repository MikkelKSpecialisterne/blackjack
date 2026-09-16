from Deck import Hand

class Participant:
    def __init__(self):
        self.hand=Hand()

class Player(Participant):
    def __init__(self):
        super().__init__()
        self.money = 500
        self.passed = False

    def hit(self, deck):
        self.hand.add_card(deck.draw())

    def stand(self):
        self.passed = True

class Dealer(Participant):
    def play(self, deck):
        while (self.hand.value_in_hand < 17):
            self.draw(deck)
    def draw(self, deck):
        self.hand.add_card(deck.draw())