import pygame
from Game import GameState

WIDTH, HEIGHT = 1000, 800


class GameView:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 22)

        self.hit_button = pygame.Rect(300, 720, 100, 45)
        self.double_button = pygame.Rect(420, 720, 100, 45)
        self.stand_button = pygame.Rect(540, 720, 100, 45)
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

        if game.state == GameState.BETTING:
            pygame.draw.rect(self.screen, (255,255,255), self.betting_box)
            bet_label = self.font.render(game.bet_value, True, (0,0,0))
            self.screen.blit(bet_label, (self.betting_box.x+10, self.betting_box.y+10))
            if game.money_error == False:
                bet_info_label1 = self.font.render("Please write the amount you wish to bet, and press 'Enter' to confirm", True, (255, 255, 255))
            elif game.money_error == True:
                bet_info_label1 = self.font.render("Error: Not enough money, or no value written. Please enter a valid amount", True, (255, 255, 255))
            bet_info_label2 = self.font.render("Current balance: "+ str(game.player.money), True, (255, 255, 255))
            self.screen.blit(bet_info_label1, bet_info_label1.get_rect(center=(WIDTH// 2, 350)))
            self.screen.blit(bet_info_label2, bet_info_label2.get_rect(center=(WIDTH// 2, 450)))

        if (game.state == GameState.PLAYER_TURN):
            #dealer_text = self.font.render("Dealer hand: "+ game.convert_dealer_hand(game.dealer.hand), True, (255, 255, 255))
            #self.screen.blit(dealer_text, (150, 50))
            self.screen.blit(self.card_back, (300, 100))
            card = game.dealer.hand.cards_in_hand[1]
            self.screen.blit(self.card_images[(card.rank, card.suit)], (420, 100))
            x = 300
            for card in game.player.hand.cards_in_hand:
                self.screen.blit(self.card_images[(card.rank, card.suit)], (x, 500))
                x += 120
            player_text = self.font.render("Total value: " + str(game.player.hand.value_in_hand), True, (255, 255, 255))
            self.screen.blit(player_text, player_text.get_rect(centerx=WIDTH // 2, y=670))
            pygame.draw.rect(self.screen, (90, 90, 90), self.hit_button)
            pygame.draw.rect(self.screen, (90, 90, 90), self.double_button)
            pygame.draw.rect(self.screen, (90, 90, 90), self.stand_button)
            hit_label = self.font.render("Hit", True, (255, 255, 255))
            self.screen.blit(hit_label, hit_label.get_rect(center=self.hit_button.center))
            double_label = self.font.render("Double", True, (255, 255, 255))
            self.screen.blit(double_label, double_label.get_rect(center=self.double_button.center))
            stand_label = self.font.render("Stand", True, (255, 255, 255))
            self.screen.blit(stand_label, stand_label.get_rect(center=self.stand_button.center))
            if game.money_error == True:
                bet_info_label1 = self.font.render("Error: Not enough money to double your bet. Please be less poor", True, (255, 255, 255))
                self.screen.blit(bet_info_label1, bet_info_label1.get_rect(center=(WIDTH// 2, 350)))

        elif (game.state == GameState.ROUND_OVER):
            victory_text = self.font.render(game.victory_text, True, (255,255,255))
            self.screen.blit(victory_text, victory_text.get_rect(center=(WIDTH // 2, 350)))
            x = 300
            for card in game.dealer.hand.cards_in_hand:
                self.screen.blit(self.card_images[(card.rank, card.suit)], (x, 100))
                x += 120
            dealer_text = self.font.render("Total value: " + str(game.dealer.hand.value_in_hand), True, (255, 255, 255))
            self.screen.blit(dealer_text, dealer_text.get_rect(centerx=WIDTH // 2, y=50))
            x = 300
            for card in game.player.hand.cards_in_hand:
                self.screen.blit(self.card_images[(card.rank, card.suit)], (x, 500))
                x += 120
            player_text = self.font.render("Total value: " + str(game.player.hand.value_in_hand), True, (255, 255, 255))
            self.screen.blit(player_text, player_text.get_rect(centerx=WIDTH // 2, y=670))
            pygame.draw.rect(self.screen, (90,90,90), self.new_game_button)
            new_game_label = self.font.render("New Game", True, (255,255,255))
            self.screen.blit(new_game_label, new_game_label.get_rect(center=self.new_game_button.center))
            bet_info_label2 = self.font.render("Current balance: "+ str(game.player.money), True, (255, 255, 255))
            self.screen.blit(bet_info_label2, bet_info_label2.get_rect(center=(WIDTH// 2, 450)))

        pygame.display.flip()