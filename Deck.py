from dataclasses import dataclass
import random

@dataclass(frozen=True)
class Card:
    rank: int
    suit: str

    def value(self):
        if self.rank in (11,12,13):
            return 10
        if self.rank == (1):
            return 11
        return self.rank

    def __str__(self):
        names = {1: "Ace", 11: "Jack", 12: "Queen", 13: "King"}
        rank_name = names.get(self.rank, str(self.rank))
        return f"{rank_name} of {self.suit}"

class Deck:
    def __init__(self):
        suits = ["Hearts", "Clubs", "Diamonds", "Spades"]
        ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
        random.shuffle(self.cards)

    def draw(self):
        return self.cards.pop()

    @property
    def remaining_cards(self):
        return list(self.cards)

class Hand:
    def __init__(self):
        self.cards=[]

    def add_card(self, card):
        self.cards.append(card)

    @property
    def cards_in_hand(self):
        return list(self.cards)

    @property
    def value_in_hand(self):
        cards = [card.value() for card in self.cards]
        value = sum(cards)
        aces = sum(1 for card in self.cards if card.rank == 1)

        i=0
        while (value > 21 and aces>i):
            value=value-10
            i=i+1
        return value
    
    def clear(self):
        self.cards=[]