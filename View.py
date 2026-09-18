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
            dealer_text = self.font.render("Dealer hand: "+ game.convert_dealer_hand(game.dealer.hand), True, (255, 255, 255))
            self.screen.blit(dealer_text, (150, 50))
            player_text = self.font.render("Your hand: "+ game.convert_player_hand(game.player.hand)+ ". Total value: " + str(game.player.hand.value_in_hand), True, (255, 255, 255))
            self.screen.blit(player_text, (150, 600))
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
            dealer_text = self.font.render("Dealer hand: "+ game.convert_player_hand(game.dealer.hand)+ ". Total value: " + str(game.dealer.hand.value_in_hand), True, (255, 255, 255))
            self.screen.blit(dealer_text, (150, 50))
            player_text = self.font.render("Your hand: "+ game.convert_player_hand(game.player.hand)+ ". Total value: " + str(game.player.hand.value_in_hand), True, (255, 255, 255))
            self.screen.blit(player_text, (150, 600))
            pygame.draw.rect(self.screen, (90,90,90), self.new_game_button)
            new_game_label = self.font.render("New Game", True, (255,255,255))
            self.screen.blit(new_game_label, new_game_label.get_rect(center=self.new_game_button.center))
            bet_info_label2 = self.font.render("Current balance: "+ str(game.player.money), True, (255, 255, 255))
            self.screen.blit(bet_info_label2, bet_info_label2.get_rect(center=(WIDTH// 2, 450)))

        pygame.display.flip()