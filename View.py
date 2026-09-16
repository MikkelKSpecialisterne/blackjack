import pygame

WIDTH, HEIGHT = 800, 600


class GameView:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 22)

        # TODO: define any Rects you need for buttons here, e.g.
        # self.hit_button = pygame.Rect(300, 520, 100, 45)

    def draw(self, game):
        """Called once per frame. Take a model object, draw its current state."""
        self.screen.fill((0, 100, 0))

        # TODO: draw dealer's hand
        # TODO: draw player's hand
        # TODO: draw buttons / prompts depending on game state
        text_surface = self.font.render("Your hand: "+ game.convert_player_hand(game.player.hand)+ ". Total value: " + str(game.player.hand.value_in_hand), True, (255, 255, 255))
        self.screen.blit(text_surface, (100, 400))
        text_surface = self.font.render("Dealer hand: "+ game.convert_player_hand(game.dealer.hand)+ ". Total value: " + str(game.dealer.hand.value_in_hand), True, (255, 255, 255))
        self.screen.blit(text_surface, (100, 50))

        pygame.display.flip()