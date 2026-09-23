from Participant import Player, Dealer
from Deck import Deck
from enum import Enum, auto

class GameState(Enum):
    PLAYER_SELECT = auto()
    BETTING = auto()
    PLAYER_TURN = auto()
    ROUND_OVER = auto()

class RoundResult(Enum):
    WIN = auto()
    BLACKJACK = auto()
    LOSE = auto()
    TIE = auto()
    BANKRUPT = auto()
    ERROR = auto()

class Game:
    def __init__(self):
        self.players=[]
        self.dealer=Dealer()
        self.state = GameState.PLAYER_SELECT
        self.victory_text =""
        self.player_turn = 0

    def player_amount(self, amount):
        for i in range(amount):
            self.players.append(Player())

    def next_player(self):
        if all(player.passed for player in self.players):
            self.round_over()
        else:
            self.player_turn = (self.player_turn+1) % len(self.players)
            if self.players[self.player_turn].passed:
                self.next_player()

    def bet(self, player):
        player.bet_value = ""
        self.state=GameState.BETTING

    def new_game(self):
        self.state=GameState.PLAYER_TURN
        self.dealer.hand.clear()
        self.deck = Deck()
        for p in self.players:
            p.hand.clear()
            if (p.passed==True):
                p.passed=False
            p.hit(self.deck)
            p.hit(self.deck)
        for p in self.players:
            if (p.hand.value_in_hand == 21):
                p.passed=True
        self.dealer.draw(self.deck)
        self.dealer.draw(self.deck)
        if self.dealer.hand.value_in_hand == 21:
            self.round_over()
        elif self.players[0].passed:
            self.next_player()

    def convert_player_hand(self, hand):
        return ", ".join(map(str, hand.cards_in_hand))

    def convert_dealer_hand(self, hand):
        return ", ".join(map(str, hand.cards_in_hand[1:]))

    def check_victory(self,player):
        p = player.hand.value_in_hand
        dealer = self.dealer.hand.value_in_hand
        if (p>dealer and p < 22 or p < 22 and dealer > 21):
            if p == 21 and len(player.hand.cards_in_hand)==2:
                player.money += int(round(int(player.bet_value)*1.5))
                return RoundResult.BLACKJACK
            else:
                player.money += int(player.bet_value)
                return RoundResult.WIN
        elif (dealer>p and dealer < 22 or dealer < 22 and p > 21 or dealer > 21 and p > 21):
            player.money -= int(player.bet_value)
            if player.money == 0:
                player.bankrupt = True
            return RoundResult.LOSE
        elif (dealer == p):
            return RoundResult.TIE
        else:
            return RoundResult.ERROR

    def hit(self, player):
        player.hit(self.deck)
        player.money_error=False

    def double(self, player):
        if int(player.bet_value)*2 <= player.money:
            player.bet_value = str(int(player.bet_value)*2)
            player.hit(self.deck)
            player.stand()
        else:
            player.money_error=True

    def confirm_bet(self, player):
        if  not player.bet_value == "" and int(player.bet_value) <= player.money and int(player.bet_value) > 0:
            player.money_error =False
            if self.player_turn == len(self.players)-1:
                self.player_turn = 0
                self.new_game()
            else: 
                self.player_turn += 1
        else:
            player.money_error=True

    def round_over(self):
        if any (player.hand.value_in_hand < 22 for player in self.players):
            self.dealer.play(self.deck)
        for i in self.players:
            i.round_result = self.check_victory(i)
            i.bet_value = ""
        self.state = GameState.ROUND_OVER
        self.player_turn = 0

    def current_player(self):
        return self.players[self.player_turn]

    def remove_bankrupt(self):
        for p in self.players.copy():
            if p.bankrupt == True:
                self.players.remove(p)
        if len(self.players) == 0:
            return False
        else: 
            return True