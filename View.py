import pygame

WIDTH, HEIGHT = 1000, 800


class GameView:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 22)

        self.hit_button = pygame.Rect(300, 520, 100, 45)
        self.double_button = pygame.Rect(420, 520, 100, 45)
        self.stand_button = pygame.Rect(540, 520, 100, 45)
        self.new_game_button = pygame.Rect(0, 0, 130, 45)
        self.new_game_button.center = (WIDTH // 2, 400)

    def draw(self, game):
        """Called once per frame. Take a model object, draw its current state."""
        self.screen.fill((0, 100, 0))

        # TODO: draw dealer's hand
        # TODO: draw player's hand
        # TODO: draw buttons / prompts depending on game state
        player_text = self.font.render("Your hand: "+ game.convert_player_hand(game.player.hand)+ ". Total value: " + str(game.player.hand.value_in_hand), True, (255, 255, 255))
        self.screen.blit(player_text, (150, 600))
        if (game.game_over == False):
            dealer_text = self.font.render("Dealer hand: "+ game.convert_dealer_hand(game.dealer.hand), True, (255, 255, 255))
            self.screen.blit(dealer_text, (150, 50))
            pygame.draw.rect(self.screen, (90, 90, 90), self.hit_button)
            pygame.draw.rect(self.screen, (90, 90, 90), self.double_button)
            pygame.draw.rect(self.screen, (90, 90, 90), self.stand_button)
            hit_label = self.font.render("Hit", True, (255, 255, 255))
            self.screen.blit(hit_label, hit_label.get_rect(center=self.hit_button.center))
            double_label = self.font.render("Double", True, (255, 255, 255))
            self.screen.blit(double_label, double_label.get_rect(center=self.double_button.center))
            stand_label = self.font.render("Stand", True, (255, 255, 255))
            self.screen.blit(stand_label, stand_label.get_rect(center=self.stand_button.center))
        elif (game.game_over == True):
            victory_text = self.font.render(game.victory_text, True, (255,255,255))
            self.screen.blit(victory_text, victory_text.get_rect(center=(WIDTH // 2, 350)))
            dealer_text = self.font.render("Dealer hand: "+ game.convert_player_hand(game.dealer.hand)+ ". Total value: " + str(game.dealer.hand.value_in_hand), True, (255, 255, 255))
            self.screen.blit(dealer_text, (150, 50))
            pygame.draw.rect(self.screen, (90,90,90), self.new_game_button)
            new_game_label = self.font.render("New Game", True, (255,255,255))
            self.screen.blit(new_game_label, new_game_label.get_rect(center=self.new_game_button.center))

        pygame.display.flip()