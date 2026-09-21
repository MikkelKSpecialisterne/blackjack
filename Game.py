from Participant import Player, Dealer
from Deck import Deck
from enum import Enum, auto

class GameState(Enum):
    BETTING = auto()
    PLAYER_TURN = auto()
    ROUND_OVER = auto()

class Game:
    def __init__(self):
        self.player=Player()
        self.dealer=Dealer()
        self.state = GameState.PLAYER_TURN
        self.victory_text =""
        self.bet_value =""
        self.money_error=False

    def bet(self):
        self.bet_value = ""
        self.state=GameState.BETTING
        if self.player.money <= 0:
            self.player=Player()

    def new_game(self):
        self.state=GameState.PLAYER_TURN
        self.dealer.hand.clear()
        self.player.hand.clear()
        if (self.player.passed==True):
            self.player.passed=False
        self.deck = Deck()
        self.player.hit(self.deck)
        self.player.hit(self.deck)
        self.dealer.draw(self.deck)
        self.dealer.draw(self.deck)
        if (self.player.hand.value_in_hand == 21):
            self.check_victory()
        return

    def convert_player_hand(self, hand):
        return ", ".join(map(str, hand.cards_in_hand))

    def convert_dealer_hand(self, hand):
        return ", ".join(map(str, hand.cards_in_hand[1:]))

    def check_victory(self):
        player = self.player.hand.value_in_hand
        dealer = self.dealer.hand.value_in_hand
        if (player>dealer and player < 22 or player < 22 and dealer > 21):
            if (self.state == GameState.PLAYER_TURN):
                if self.player.hand.value_in_hand == 21 and len(self.player.hand.cards_in_hand)==2:
                    self.victory_text = "Blackjack!"
                    self.player.money += int(round(int(self.bet_value)*1.5))
                else:
                    self.victory_text = "You win. Congratulations!"
                    self.player.money += int(self.bet_value)
        elif (dealer>player and dealer < 22 or dealer < 22 and player > 21):
            if (self.state == GameState.PLAYER_TURN):
                self.player.money -= int(self.bet_value)
            if self.player.money > 0:
                self.victory_text = "You lose lmfao."
            else:
                self.victory_text = "You are out of money. You get nothing! You lose! Good day!"

        elif (dealer == player):
            self.victory_text = "It's a tie."
        else:
            self.victory_text = "Some unforseen outcome happened and I have not accounted for it, so this is also a tie, but I dont really know why or how."
        if (self.state == GameState.PLAYER_TURN):
            self.state = GameState.ROUND_OVER

class TerminalGame:
    def __init__(self):
        self.player=Player()
        self.dealer=Dealer()
        self.new_game()

    def new_game(self):
        self.dealer.hand.clear()
        self.player.hand.clear()
        if (self.player.passed==True):
            self.player.passed=False
        self.deck = Deck()
        self.player.hit(self.deck)
        self.player.hit(self.deck)
        self.dealer.draw(self.deck)
        self.dealer.draw(self.deck)
        while (self.player.passed == False and self.player.hand.value_in_hand < 21):
            print("Dealer hand: "+ self.convert_dealer_hand(self.dealer.hand))
            print("Your hand: "+ self.convert_player_hand(self.player.hand)+ ". Total value: " + str(self.player.hand.value_in_hand))
            response = input().lower()
            if (response == "hit"):
                self.player.hit(self.deck)
            elif (response == "stand"):
                self.player.stand()
            elif(response == "double"):
                self.player.hit(self.deck)
                self.player.stand()
            else:
                print("Please input a valid response. Either hit, stand, or double")
        if (self.player.hand.value_in_hand<22):
            self.dealer.play(self.deck)
        print("Dealer final hand: "+ self.convert_player_hand(self.dealer.hand)+ ". Dealer value: " + str(self.dealer.hand.value_in_hand))
        print("Your final hand: "+ self.convert_player_hand(self.player.hand)+ ". Final value: " + str(self.player.hand.value_in_hand))
        self.check_victory()
        return

    def convert_player_hand(self, hand):
        return ", ".join(map(str, hand.cards_in_hand))

    def convert_dealer_hand(self, hand):
        return ", ".join(map(str, hand.cards_in_hand[1:]))

    def check_victory(self):
        player = self.player.hand.value_in_hand
        dealer = self.dealer.hand.value_in_hand
        if (player>dealer and player < 22 or player < 22 and dealer > 21):
            print("You win. Congratulations!")
        elif (dealer>player and dealer < 22 or dealer < 22 and player > 21):
            print("You lose lmfao.")
        elif (dealer == player):
            print("It's a tie.")
        else:
            print("Some unforseen outcome happened and I have not accounted for it, so this is also a tie, but I dont really know why or how.")

if __name__ == "__main__":
    TerminalGame().new_game()