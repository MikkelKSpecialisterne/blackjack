import pygame
from Game import GameState, RoundResult

WIDTH, HEIGHT = 1200, 800


class GameView:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 22)

        self.hit_button = pygame.Rect(400, 720, 100, 45)
        self.double_button = pygame.Rect(520, 720, 100, 45)
        self.stand_button = pygame.Rect(640, 720, 100, 45)
        self.new_game_button = pygame.Rect(0, 0, 130, 45)
        self.new_game_button.center = (WIDTH // 2, 400)
        self.betting_box = pygame.Rect(0, 0, 130, 45)
        self.betting_box.center = (WIDTH // 2, 400)

        self.card_images = {}
        suits = ["Hearts", "Clubs", "Diamonds", "Spades"]
        ranks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        card_size = (100,140)
        for suit in suits:
            for rank in ranks:
                path = f"cards/{self.filename_for(rank,suit)}.png"
                self.card_images[(rank, suit)]= pygame.image.load(path).convert_alpha()
                image = pygame.image.load(path).convert_alpha()
                self.card_images[(rank, suit)] = pygame.transform.scale(image, card_size)
        self.card_back = pygame.image.load(f"cards/Back Red 1.png").convert_alpha()
        self.card_back = pygame.transform.scale(self.card_back, card_size)

    def filename_for(self,rank,suit):
        suit_names = {"Hearts": "Hearts", "Clubs": "Clubs", "Diamonds": "Diamond", "Spades": "Spades"}
        return f"{suit_names[suit]} {rank}"

    def draw(self, game):
        """Called once per frame. Take a model object, draw its current state."""
        self.screen.fill((0, 100, 0))

        if game.state == GameState.PLAYER_SELECT:
            bet_info_label1 = self.font.render("Press 1-4 to select the amount of players", True, (255, 255, 255))
            self.screen.blit(bet_info_label1, bet_info_label1.get_rect(center=(WIDTH// 2, 350)))

        elif game.state == GameState.BETTING:
            pygame.draw.rect(self.screen, (255,255,255), self.betting_box)
            bet_label = self.font.render(game.current_player().bet_value, True, (0,0,0))
            self.screen.blit(bet_label, (self.betting_box.x+10, self.betting_box.y+10))
            if game.current_player().money_error == False:
                bet_info_label1 = self.font.render("Player " + str(game.player_turn + 1) + ": Please write the amount you wish to bet, and press 'Enter' to confirm", True, (255, 255, 255))
            elif game.current_player().money_error == True:
                bet_info_label1 = self.font.render("Player " + str(game.player_turn + 1) + ": Error: Not enough money, or no value written. Please enter a valid amount", True, (255, 255, 255))
            bet_info_label2 = self.font.render("Current balance: "+ str(game.current_player().money), True, (255, 255, 255))
            self.screen.blit(bet_info_label1, bet_info_label1.get_rect(center=(WIDTH// 2, 350)))
            self.screen.blit(bet_info_label2, bet_info_label2.get_rect(center=(WIDTH// 2, 450)))

        elif (game.state == GameState.PLAYER_TURN):
            player = game.current_player()
            self.screen.blit(self.card_back, (400, 100))
            card = game.dealer.hand.cards_in_hand[1]
            self.screen.blit(self.card_images[(card.rank, card.suit)], (520, 100))
            turn_label = self.font.render("Player " + str(game.player_turn + 1) + "'s turn", True, (255, 255, 255))
            self.screen.blit(turn_label, turn_label.get_rect(centerx=WIDTH // 2, y=440))
            x = 100
            for p in game.players:
                hand_start = x
                for card in p.hand.cards_in_hand:
                    self.screen.blit(self.card_images[(card.rank, card.suit)], (x, 500))
                    x += 30
                if p is game.current_player():
                    hand_width = (x - hand_start) + (100 - 30) 
                    highlight_rect = pygame.Rect(hand_start - 10, 500 - 10, hand_width + 20, 140 + 20)
                    pygame.draw.rect(self.screen, (255, 255, 0), highlight_rect, width=4)
                x = hand_start + 280
                player_text = self.font.render("Total value: " + str(p.hand.value_in_hand), True, (255, 255, 255))
                self.screen.blit(player_text, player_text.get_rect(x=hand_start, y=670))
                    
            pygame.draw.rect(self.screen, (90, 90, 90), self.hit_button)
            pygame.draw.rect(self.screen, (90, 90, 90), self.double_button)
            pygame.draw.rect(self.screen, (90, 90, 90), self.stand_button)
            hit_label = self.font.render("Hit", True, (255, 255, 255))
            self.screen.blit(hit_label, hit_label.get_rect(center=self.hit_button.center))
            double_label = self.font.render("Double", True, (255, 255, 255))
            self.screen.blit(double_label, double_label.get_rect(center=self.double_button.center))
            stand_label = self.font.render("Stand", True, (255, 255, 255))
            self.screen.blit(stand_label, stand_label.get_rect(center=self.stand_button.center))
            if player.money_error == True:
                bet_info_label1 = self.font.render("Player " + str(game.player_turn + 1) + ": Error: Not enough money to double your bet. Please be less poor", True, (255, 255, 255))
                self.screen.blit(bet_info_label1, bet_info_label1.get_rect(center=(WIDTH// 2, 350)))

        elif (game.state == GameState.ROUND_OVER):
            result_text = {
                RoundResult.WIN: "Win",
                RoundResult.BLACKJACK: "Blackjack!",
                RoundResult.LOSE: "Lose",
                RoundResult.TIE: "Tie",
                RoundResult.ERROR: "?",
            }
            x = 400
            for card in game.dealer.hand.cards_in_hand:
                self.screen.blit(self.card_images[(card.rank, card.suit)], (x, 100))
                x += 120
            dealer_text = self.font.render("Total value: " + str(game.dealer.hand.value_in_hand), True, (255, 255, 255))
            self.screen.blit(dealer_text, dealer_text.get_rect(centerx=WIDTH // 2, y=50))
            x = 100
            for p in game.players:
                hand_start = x
                for card in p.hand.cards_in_hand:
                    self.screen.blit(self.card_images[(card.rank, card.suit)], (x, 500))
                    x += 30
                x = hand_start + 280
                player_text = self.font.render("Total value: " + str(p.hand.value_in_hand), True, (255, 255, 255))
                self.screen.blit(player_text, player_text.get_rect(x=hand_start, y=670))
                result_label = self.font.render(result_text.get(p.round_result, ""), True, (255, 255, 0))
                self.screen.blit(result_label, result_label.get_rect(x=hand_start, y=645))
                money_label = self.font.render("Balance: " + str(p.money), True, (255, 255, 255))
                self.screen.blit(money_label, money_label.get_rect(x=hand_start, y=720))
            pygame.draw.rect(self.screen, (90,90,90), self.new_game_button)
            new_game_label = self.font.render("New Game", True, (255,255,255))
            self.screen.blit(new_game_label, new_game_label.get_rect(center=self.new_game_button.center))

        pygame.display.flip()